import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.config import Config
from src.data_loader import DataLoader
from src.preprocessing import (
    ClientePreprocessor,
    TransaccionalPreprocessor,
    quality_report,
)
from src.feature_engineering import TransactionalFeatureBuilder, FeatureAssembler
from src.eda import EDAReport
from src.model import ModelTrainer
from src.evaluation import ModelEvaluator, BusinessImpactAnalyzer
from src.strategy import StrategyBuilder
from src.visualization import Visualizer

warnings.filterwarnings("ignore")


def main() -> None:
    cfg = Config()
    viz = Visualizer(
        output_dir=cfg.graficos_dir,
        dpi=cfg.figure_dpi,
        figsize=cfg.figure_size,
        palette_primary=cfg.palette_primary,
        palette_secondary=cfg.palette_secondary,
        palette_accent=cfg.palette_accent,
    )
    summary: dict = {}

    loader = DataLoader(cfg.data_clientes_path, cfg.data_transaccional_path)
    raw = loader.load()

    summary["calidad_clientes"] = quality_report(raw.clientes).__dict__
    summary["calidad_transacciones"] = quality_report(raw.transacciones).__dict__

    cli_prep = ClientePreprocessor(age_strategy="median")
    clientes_clean = cli_prep.fit_transform(raw.clientes)

    trans_prep = TransaccionalPreprocessor(excel_date_origin=cfg.excel_date_origin)
    trans_clean = trans_prep.transform(raw.transacciones)

    summary["clientes_postlimpieza"] = quality_report(clientes_clean).__dict__
    summary["transacciones_postlimpieza"] = quality_report(trans_clean).__dict__
    summary["periodo_transacciones"] = {
        "min": str(trans_clean["date"].min().date()),
        "max": str(trans_clean["date"].max().date()),
        "dias": int((trans_clean["date"].max() - trans_clean["date"].min()).days),
    }

    eda = EDAReport(target_col=cfg.target_col)
    target_dist = eda.target_distribution(clientes_clean)
    summary["target_distribution"] = {
        "n": target_dist.n,
        "counts": target_dist.counts,
        "proportions": {int(k): float(v) for k, v in target_dist.proportions.items()},
    }

    viz.target_balance(clientes_clean[cfg.target_col])
    viz.target_rate_by_category(clientes_clean, "territory_id")
    viz.target_rate_by_category(clientes_clean, "segment")
    viz.initiatives_vs_target(clientes_clean)
    viz.transactions_over_time(trans_clean)
    viz.category_amount(trans_clean)

    feature_builder = TransactionalFeatureBuilder()
    trans_features = feature_builder.build(trans_clean)
    assembler = FeatureAssembler()
    master = assembler.assemble(clientes_clean, trans_features)
    summary["n_features_finales"] = int(master.shape[1])
    summary["n_clientes_finales"] = int(master.shape[0])

    numeric_features = [c for c in master.columns if c not in (
        cfg.business_categorical + [cfg.id_col, cfg.target_col]
    ) and master[c].dtype != object]

    corr = eda.correlation_with_target(master, numeric_features)
    viz.correlation_with_target(corr, top=15)
    corr.to_csv(cfg.outputs_dir / "correlation_with_target.csv")

    X = master[cfg.business_categorical + numeric_features]
    y = master[cfg.target_col].astype(int)

    trainer = ModelTrainer(
        categorical_features=cfg.business_categorical,
        numeric_features=numeric_features,
        random_state=cfg.random_state,
        test_size=cfg.test_size,
        cv_folds=5,
    )

    X_train, X_test, y_train, y_test = trainer.split(X, y)
    cv_scores = trainer.cross_validate_models(X_train, y_train)
    summary["cv_scores"] = {k: {"mean": v[0], "std": v[1]} for k, v in cv_scores.items()}
    viz.cv_scores(cv_scores)

    best_name = max(cv_scores, key=lambda k: cv_scores[k][0])
    summary["best_model"] = best_name

    best_pipeline = trainer.fit_final(best_name, X_train, y_train)
    y_proba_test = best_pipeline.predict_proba(X_test)[:, 1]

    evaluator = ModelEvaluator()
    best_threshold = evaluator.optimal_f1_threshold(y_test.values, y_proba_test)
    metrics_default = evaluator.evaluate(y_test.values, y_proba_test, threshold=0.5)
    metrics_optimal = evaluator.evaluate(y_test.values, y_proba_test, threshold=best_threshold)

    summary["test_metrics_threshold_default"] = {
        k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else None)
        for k, v in metrics_default.__dict__.items()
        if k not in ("confusion", "classification_text")
    }
    summary["test_metrics_threshold_optimal"] = {
        k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else None)
        for k, v in metrics_optimal.__dict__.items()
        if k not in ("confusion", "classification_text")
    }
    summary["confusion_matrix_optimal"] = metrics_optimal.confusion.tolist()
    summary["classification_report_optimal"] = metrics_optimal.classification_text

    fpr, tpr = evaluator.roc_points(y_test.values, y_proba_test)
    viz.roc_curve_plot(fpr, tpr, metrics_default.roc_auc)
    rec, prec = evaluator.pr_points(y_test.values, y_proba_test)
    viz.pr_curve_plot(rec, prec, metrics_default.pr_auc)
    viz.confusion_matrix_plot(metrics_optimal.confusion)

    deciles = evaluator.decile_analysis(y_test.values, y_proba_test)
    deciles.to_csv(cfg.outputs_dir / "decile_analysis.csv", index=False)
    viz.lift_chart(deciles)
    viz.cumulative_gains(deciles)

    feature_names = None
    try:
        cat_names = list(
            best_pipeline.named_steps["preprocessor"]
            .named_transformers_["cat"]
            .get_feature_names_out(cfg.business_categorical)
        )
        feature_names = numeric_features + cat_names
        model_step = best_pipeline.named_steps["model"]
        if hasattr(model_step, "feature_importances_"):
            importance = pd.Series(model_step.feature_importances_, index=feature_names)
            importance.to_csv(cfg.outputs_dir / "feature_importance.csv")
            viz.feature_importance(importance, top=15)
        elif hasattr(model_step, "coef_"):
            importance = pd.Series(np.abs(model_step.coef_[0]), index=feature_names)
            importance.to_csv(cfg.outputs_dir / "feature_importance.csv")
            viz.feature_importance(importance, top=15)
    except Exception as exc:
        summary["feature_importance_error"] = str(exc)

    y_proba_full = best_pipeline.predict_proba(X)[:, 1]
    business = BusinessImpactAnalyzer(
        incremental_potencial=cfg.incremental_potencial,
        incremental_potencial_iniciativa=cfg.incremental_potencial_iniciativa,
        incremental_no_potencial=cfg.incremental_no_potencial,
    )
    business_df = business.deciles_business_value(master, y_proba_full, amount_col="total_amount")
    business_df.to_csv(cfg.outputs_dir / "business_value_by_decile.csv", index=False)
    viz.business_impact(business_df)

    strategy = StrategyBuilder()
    master_scored = master.copy()
    master_scored["score"] = y_proba_full
    master_scored["tier"] = strategy.assign_tier(y_proba_full)
    tier_summary = strategy.tier_summary(master_scored, score_col="score", amount_col="total_amount")
    tier_summary.to_csv(cfg.outputs_dir / "tier_summary.csv", index=False)
    viz.tier_distribution(tier_summary)

    master_scored[[cfg.id_col, "score", "tier", "target"]].to_csv(
        cfg.outputs_dir / "predicciones_clientes.csv", index=False
    )

    summary["business_impact"] = {
        "total_uplift_esperado_S/.": float(business_df["uplift_total"].sum()),
        "uplift_top_3_deciles_S/.": float(business_df.head(3)["uplift_total"].sum()),
        "uplift_top_3_pct_total": float(
            business_df.head(3)["uplift_total"].sum() / business_df["uplift_total"].sum()
        ),
    }
    summary["tiers"] = tier_summary.to_dict(orient="records")
    summary["best_threshold_f1"] = float(best_threshold)

    with open(cfg.outputs_dir / "pipeline_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
