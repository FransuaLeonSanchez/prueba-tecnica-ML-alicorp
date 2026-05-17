from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


@dataclass
class EvaluationMetrics:
    roc_auc: float
    pr_auc: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    threshold: float
    confusion: np.ndarray
    classification_text: str


class ModelEvaluator:
    def __init__(self, threshold: float = 0.5) -> None:
        self._threshold = threshold

    def evaluate(self, y_true: np.ndarray, y_proba: np.ndarray, threshold: Optional[float] = None) -> EvaluationMetrics:
        thr = threshold if threshold is not None else self._threshold
        y_pred = (y_proba >= thr).astype(int)
        return EvaluationMetrics(
            roc_auc=float(roc_auc_score(y_true, y_proba)),
            pr_auc=float(average_precision_score(y_true, y_proba)),
            accuracy=float(accuracy_score(y_true, y_pred)),
            precision=float(precision_score(y_true, y_pred, zero_division=0)),
            recall=float(recall_score(y_true, y_pred, zero_division=0)),
            f1=float(f1_score(y_true, y_pred, zero_division=0)),
            threshold=float(thr),
            confusion=confusion_matrix(y_true, y_pred),
            classification_text=classification_report(y_true, y_pred, zero_division=0),
        )

    def optimal_f1_threshold(self, y_true: np.ndarray, y_proba: np.ndarray) -> float:
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_proba)
        f1s = (2 * precisions * recalls) / np.where(
            precisions + recalls > 0, precisions + recalls, 1e-9
        )
        idx = int(np.argmax(f1s[:-1])) if len(thresholds) > 0 else 0
        return float(thresholds[idx]) if len(thresholds) > 0 else 0.5

    def roc_points(self, y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        return fpr, tpr

    def pr_points(self, y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        precisions, recalls, _ = precision_recall_curve(y_true, y_proba)
        return recalls, precisions

    def decile_analysis(self, y_true: np.ndarray, y_proba: np.ndarray) -> pd.DataFrame:
        df = pd.DataFrame({"y": y_true, "p": y_proba})
        df["decile"] = pd.qcut(df["p"].rank(method="first", ascending=False), 10, labels=False) + 1
        agg = (
            df.groupby("decile")
            .agg(n=("y", "size"), positives=("y", "sum"), mean_prob=("p", "mean"))
            .reset_index()
        )
        agg["positive_rate"] = agg["positives"] / agg["n"]
        base_rate = df["y"].mean()
        agg["lift"] = agg["positive_rate"] / base_rate if base_rate > 0 else 0
        agg["cum_positives"] = agg["positives"].cumsum()
        agg["cum_positives_pct"] = agg["cum_positives"] / df["y"].sum()
        agg["cum_population_pct"] = agg["n"].cumsum() / len(df)
        return agg


class BusinessImpactAnalyzer:
    def __init__(
        self,
        incremental_potencial: float = 0.10,
        incremental_potencial_iniciativa: float = 0.15,
        incremental_no_potencial: float = 0.005,
    ) -> None:
        self._incr_potencial = incremental_potencial
        self._incr_potencial_iniciativa = incremental_potencial_iniciativa
        self._incr_no_potencial = incremental_no_potencial

    def expected_incremental(
        self,
        clientes_features: pd.DataFrame,
        y_proba: np.ndarray,
        amount_col: str = "total_amount",
    ) -> pd.DataFrame:
        df = clientes_features.copy()
        df["score"] = y_proba
        df["expected_incremental_no_action"] = df.apply(
            lambda r: self._expected_incremental_row(r, with_action=False, amount_col=amount_col),
            axis=1,
        )
        df["expected_incremental_with_action"] = df.apply(
            lambda r: self._expected_incremental_row(r, with_action=True, amount_col=amount_col),
            axis=1,
        )
        df["uplift_with_action"] = (
            df["expected_incremental_with_action"] - df["expected_incremental_no_action"]
        )
        return df

    def _expected_incremental_row(self, row: pd.Series, with_action: bool, amount_col: str) -> float:
        amount = float(row.get(amount_col, 0.0))
        p = float(row["score"])
        if with_action:
            rate_pos = self._incr_potencial_iniciativa
        else:
            already_iniciativa = (
                int(row.get("has_perfect_customer", 0)) == 1
                or int(row.get("has_marketing_impulse", 0)) == 1
            )
            rate_pos = self._incr_potencial_iniciativa if already_iniciativa else self._incr_potencial
        expected = (p * rate_pos + (1 - p) * self._incr_no_potencial) * amount
        return expected

    def deciles_business_value(
        self,
        clientes_features: pd.DataFrame,
        y_proba: np.ndarray,
        amount_col: str = "total_amount",
    ) -> pd.DataFrame:
        enriched = self.expected_incremental(clientes_features, y_proba, amount_col=amount_col)
        enriched["decile"] = pd.qcut(
            enriched["score"].rank(method="first", ascending=False), 10, labels=False
        ) + 1
        agg = (
            enriched.groupby("decile")
            .agg(
                clientes=("score", "size"),
                ventas_periodo=(amount_col, "sum"),
                score_promedio=("score", "mean"),
                incremental_esperado_con_accion=("expected_incremental_with_action", "sum"),
                incremental_esperado_sin_accion=("expected_incremental_no_action", "sum"),
                uplift_total=("uplift_with_action", "sum"),
            )
            .reset_index()
        )
        agg["roi_uplift_pct_ventas"] = np.where(
            agg["ventas_periodo"] > 0, agg["uplift_total"] / agg["ventas_periodo"], 0
        )
        return agg
