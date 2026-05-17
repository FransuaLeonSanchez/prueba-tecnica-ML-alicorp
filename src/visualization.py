from pathlib import Path
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class Visualizer:
    def __init__(
        self,
        output_dir: Path,
        dpi: int = 130,
        figsize: tuple = (10, 6),
        palette_primary: str = "#C8102E",
        palette_secondary: str = "#1F1F1F",
        palette_accent: str = "#F2A900",
    ) -> None:
        self._output_dir = output_dir
        self._dpi = dpi
        self._figsize = figsize
        self._primary = palette_primary
        self._secondary = palette_secondary
        self._accent = palette_accent
        sns.set_theme(style="whitegrid", context="talk")

    def _save(self, name: str) -> Path:
        path = self._output_dir / f"{name}.png"
        plt.tight_layout()
        plt.savefig(path, dpi=self._dpi, bbox_inches="tight")
        plt.close()
        return path

    def target_balance(self, target: pd.Series, name: str = "01_target_balance") -> Path:
        counts = target.value_counts().sort_index()
        labels = ["Sin potencial (0)", "Con potencial (1)"]
        fig, ax = plt.subplots(figsize=self._figsize)
        bars = ax.bar(labels, counts.values, color=[self._secondary, self._primary])
        for bar, v in zip(bars, counts.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + max(counts.values) * 0.01,
                f"{v:,}\n({v / counts.sum():.1%})",
                ha="center",
                va="bottom",
                fontsize=12,
            )
        ax.set_title("Distribucion de la variable target")
        ax.set_ylabel("Clientes")
        return self._save(name)

    def target_rate_by_category(
        self,
        df: pd.DataFrame,
        group_col: str,
        target_col: str = "target",
        name: Optional[str] = None,
    ) -> Path:
        agg = df.groupby(group_col)[target_col].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=self._figsize)
        bars = ax.bar(agg.index.astype(str), agg.values, color=self._primary)
        ax.axhline(df[target_col].mean(), color=self._secondary, linestyle="--", label="Tasa global")
        for bar, v in zip(bars, agg.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + 0.005,
                f"{v:.1%}",
                ha="center",
                va="bottom",
                fontsize=11,
            )
        ax.set_title(f"Tasa de target por {group_col}")
        ax.set_ylabel("Tasa de target")
        ax.legend()
        out_name = name or f"02_target_rate_by_{group_col}"
        return self._save(out_name)

    def initiatives_vs_target(self, df: pd.DataFrame, name: str = "03_initiatives_vs_target") -> Path:
        cols = ["has_credit_line", "has_perfect_customer", "has_marketing_impulse"]
        rates = []
        for c in cols:
            with_flag = df.loc[df[c] == 1, "target"].mean()
            without_flag = df.loc[df[c] == 0, "target"].mean()
            rates.append((c, with_flag, without_flag))
        labels = [r[0] for r in rates]
        with_v = [r[1] for r in rates]
        without_v = [r[2] for r in rates]
        x = np.arange(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=self._figsize)
        b1 = ax.bar(x - width / 2, with_v, width, label="Con iniciativa", color=self._primary)
        b2 = ax.bar(x + width / 2, without_v, width, label="Sin iniciativa", color=self._secondary)
        for bars in (b1, b2):
            for b in bars:
                ax.text(
                    b.get_x() + b.get_width() / 2,
                    b.get_height() + 0.005,
                    f"{b.get_height():.1%}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=0)
        ax.set_title("Tasa de target segun iniciativas comerciales")
        ax.set_ylabel("Tasa de target")
        ax.legend()
        return self._save(name)

    def transactions_over_time(self, trans: pd.DataFrame, name: str = "04_transactions_over_time") -> Path:
        ts = trans.groupby(trans["date"].dt.to_period("W").dt.start_time).agg(
            ventas=("amount", "sum"), transacciones=("date", "size")
        )
        fig, ax1 = plt.subplots(figsize=self._figsize)
        ax1.plot(ts.index, ts["ventas"], color=self._primary, marker="o", label="Ventas (S/.)")
        ax1.set_ylabel("Ventas semanales (S/.)", color=self._primary)
        ax1.tick_params(axis="y", labelcolor=self._primary)
        ax2 = ax1.twinx()
        ax2.plot(ts.index, ts["transacciones"], color=self._secondary, marker="x", label="Transacciones")
        ax2.set_ylabel("Transacciones", color=self._secondary)
        ax2.tick_params(axis="y", labelcolor=self._secondary)
        plt.title("Evolucion semanal de ventas y transacciones")
        fig.autofmt_xdate()
        return self._save(name)

    def category_amount(self, trans: pd.DataFrame, name: str = "05_category_amount") -> Path:
        agg = trans.groupby("category_product")["amount"].sum().sort_values(ascending=True)
        fig, ax = plt.subplots(figsize=self._figsize)
        ax.barh(agg.index, agg.values, color=self._primary)
        for i, v in enumerate(agg.values):
            ax.text(v, i, f" S/. {v:,.0f}", va="center", fontsize=10)
        ax.set_title("Ventas totales por categoria de producto")
        ax.set_xlabel("Ventas en soles")
        return self._save(name)

    def correlation_with_target(
        self, corr: pd.DataFrame, name: str = "06_corr_top_features", top: int = 15
    ) -> Path:
        top_corr = corr.head(top)
        fig, ax = plt.subplots(figsize=self._figsize)
        colors = [self._primary if v >= 0 else self._secondary for v in top_corr.iloc[:, 0]]
        ax.barh(top_corr.index[::-1], top_corr.iloc[::-1, 0], color=colors[::-1])
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title(f"Top {top} variables por correlacion con target")
        ax.set_xlabel("Correlacion con target")
        return self._save(name)

    def cv_scores(self, scores: dict, name: str = "07_cv_scores") -> Path:
        names = list(scores.keys())
        means = [v[0] for v in scores.values()]
        stds = [v[1] for v in scores.values()]
        fig, ax = plt.subplots(figsize=self._figsize)
        bars = ax.bar(names, means, yerr=stds, capsize=8, color=self._primary)
        for bar, m in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{m:.4f}",
                ha="center",
                va="bottom",
                fontsize=12,
            )
        ax.set_ylim(min(means) - 0.05, max(means) + 0.05)
        ax.set_title("ROC-AUC promedio en validacion cruzada (5-fold)")
        ax.set_ylabel("ROC-AUC")
        return self._save(name)

    def roc_curve_plot(self, fpr: np.ndarray, tpr: np.ndarray, auc: float, name: str = "08_roc_curve") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        ax.plot(fpr, tpr, color=self._primary, lw=3, label=f"AUC = {auc:.4f}")
        ax.plot([0, 1], [0, 1], linestyle="--", color=self._secondary, label="Modelo aleatorio")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("Curva ROC - test")
        ax.legend(loc="lower right")
        return self._save(name)

    def pr_curve_plot(self, recall: np.ndarray, precision: np.ndarray, ap: float, name: str = "09_pr_curve") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        ax.plot(recall, precision, color=self._primary, lw=3, label=f"AP = {ap:.4f}")
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_title("Curva Precision-Recall - test")
        ax.legend(loc="upper right")
        return self._save(name)

    def confusion_matrix_plot(self, cm: np.ndarray, name: str = "10_confusion_matrix") -> Path:
        fig, ax = plt.subplots(figsize=(7, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Reds",
            cbar=False,
            xticklabels=["Pred 0", "Pred 1"],
            yticklabels=["Real 0", "Real 1"],
            ax=ax,
        )
        ax.set_title("Matriz de confusion - test")
        return self._save(name)

    def lift_chart(self, deciles: pd.DataFrame, name: str = "11_lift_chart") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        ax.bar(deciles["decile"], deciles["lift"], color=self._primary)
        ax.axhline(1.0, color=self._secondary, linestyle="--", label="Linea base (modelo aleatorio)")
        for _, row in deciles.iterrows():
            ax.text(row["decile"], row["lift"] + 0.05, f"{row['lift']:.2f}x", ha="center", fontsize=10)
        ax.set_xticks(deciles["decile"])
        ax.set_title("Lift por decil de score")
        ax.set_xlabel("Decil (1 = mayor score)")
        ax.set_ylabel("Lift sobre tasa base")
        ax.legend()
        return self._save(name)

    def cumulative_gains(self, deciles: pd.DataFrame, name: str = "12_cumulative_gains") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        x = np.concatenate(([0], deciles["cum_population_pct"].values))
        y = np.concatenate(([0], deciles["cum_positives_pct"].values))
        ax.plot(x, y, marker="o", color=self._primary, lw=3, label="Modelo")
        ax.plot([0, 1], [0, 1], linestyle="--", color=self._secondary, label="Aleatorio")
        ax.set_xlabel("Proporcion de clientes contactados")
        ax.set_ylabel("Proporcion de positivos capturados")
        ax.set_title("Curva de ganancias acumuladas")
        ax.legend()
        return self._save(name)

    def feature_importance(self, importance: pd.Series, name: str = "13_feature_importance", top: int = 15) -> Path:
        top_imp = importance.sort_values(ascending=False).head(top)
        fig, ax = plt.subplots(figsize=self._figsize)
        ax.barh(top_imp.index[::-1], top_imp.values[::-1], color=self._primary)
        ax.set_title(f"Top {top} variables - importancia del modelo")
        ax.set_xlabel("Importancia")
        return self._save(name)

    def business_impact(self, business_df: pd.DataFrame, name: str = "14_business_impact") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        x = business_df["decile"]
        ax.bar(x, business_df["uplift_total"], color=self._primary, label="Uplift S/. con accion")
        ax.set_xticks(x)
        ax.set_xlabel("Decil de score (1 = mayor probabilidad)")
        ax.set_ylabel("Uplift esperado (S/.)")
        ax.set_title("Impacto economico esperado por decil")
        for _, r in business_df.iterrows():
            ax.text(r["decile"], r["uplift_total"], f" S/. {r['uplift_total']:,.0f}", ha="center", fontsize=9, rotation=0, va="bottom")
        ax.legend()
        return self._save(name)

    def tier_distribution(self, tier_summary: pd.DataFrame, name: str = "15_tier_distribution") -> Path:
        fig, ax = plt.subplots(figsize=self._figsize)
        bars = ax.bar(tier_summary["tier"], tier_summary["clientes"], color=self._primary)
        for bar, v in zip(bars, tier_summary["clientes"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + max(tier_summary["clientes"]) * 0.01,
                f"{int(v):,}",
                ha="center",
                fontsize=11,
            )
        plt.xticks(rotation=20, ha="right")
        ax.set_title("Clientes por tier de accion comercial")
        ax.set_ylabel("Numero de clientes")
        return self._save(name)
