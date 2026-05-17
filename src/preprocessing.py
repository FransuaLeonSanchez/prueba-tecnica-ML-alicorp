from dataclasses import dataclass
from typing import Optional
import numpy as np
import pandas as pd


@dataclass
class QualityReport:
    rows: int
    cols: int
    duplicates: int
    nulls_total: int
    nulls_by_col: dict
    memory_mb: float


def quality_report(df: pd.DataFrame) -> QualityReport:
    return QualityReport(
        rows=len(df),
        cols=df.shape[1],
        duplicates=int(df.duplicated().sum()),
        nulls_total=int(df.isna().sum().sum()),
        nulls_by_col={c: int(v) for c, v in df.isna().sum().items() if v > 0},
        memory_mb=round(df.memory_usage(deep=True).sum() / 1024**2, 3),
    )


class ClientePreprocessor:
    def __init__(self, age_strategy: str = "median") -> None:
        if age_strategy not in {"median", "mean", "zero"}:
            raise ValueError("age_strategy debe ser median, mean o zero")
        self._age_strategy = age_strategy
        self._age_imputer_value: Optional[float] = None

    def fit(self, df: pd.DataFrame) -> "ClientePreprocessor":
        if self._age_strategy == "median":
            self._age_imputer_value = float(df["age_alicorp"].median())
        elif self._age_strategy == "mean":
            self._age_imputer_value = float(df["age_alicorp"].mean())
        else:
            self._age_imputer_value = 0.0
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self._age_imputer_value is None:
            raise RuntimeError("Ejecuta fit antes de transform")
        out = df.copy()
        out = out.drop_duplicates(subset=["customer_id"])
        out["age_alicorp"] = out["age_alicorp"].fillna(self._age_imputer_value)
        out["age_alicorp"] = out["age_alicorp"].astype(float)
        for c in ["has_credit_line", "has_perfect_customer", "has_marketing_impulse"]:
            out[c] = out[c].astype(int)
        out["territory_id"] = out["territory_id"].astype(str)
        out["segment"] = out["segment"].astype(str)
        out["has_any_initiative"] = (
            (out["has_perfect_customer"] == 1) | (out["has_marketing_impulse"] == 1)
        ).astype(int)
        out["initiatives_count"] = (
            out["has_credit_line"]
            + out["has_perfect_customer"]
            + out["has_marketing_impulse"]
        )
        return out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)


class TransaccionalPreprocessor:
    def __init__(self, excel_date_origin: str = "1899-12-30") -> None:
        self._excel_date_origin = excel_date_origin

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["date"] = pd.to_datetime(out["date"], origin=self._excel_date_origin, unit="D")
        out["amount"] = out["amount"].astype(float)
        out["discount"] = out["discount"].astype(float)
        out["net_amount"] = out["amount"] - out["discount"]
        out["discount_ratio"] = np.where(out["amount"] > 0, out["discount"] / out["amount"], 0.0)
        out["year_month"] = out["date"].dt.to_period("M").astype(str)
        out["weekday"] = out["date"].dt.weekday
        out["week"] = out["date"].dt.isocalendar().week.astype(int)
        return out
