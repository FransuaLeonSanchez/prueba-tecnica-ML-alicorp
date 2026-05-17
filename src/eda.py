from dataclasses import dataclass
from typing import Dict
import pandas as pd


@dataclass
class TargetDistribution:
    counts: Dict[int, int]
    proportions: Dict[int, float]
    n: int


class EDAReport:
    def __init__(self, target_col: str = "target") -> None:
        self._target_col = target_col

    def target_distribution(self, df: pd.DataFrame) -> TargetDistribution:
        counts = df[self._target_col].value_counts().to_dict()
        props = df[self._target_col].value_counts(normalize=True).to_dict()
        return TargetDistribution(counts=counts, proportions=props, n=len(df))

    def numeric_summary(self, df: pd.DataFrame, cols: list) -> pd.DataFrame:
        return df[cols].describe().T

    def target_rate_by_group(self, df: pd.DataFrame, group_col: str) -> pd.DataFrame:
        agg = (
            df.groupby(group_col)
            .agg(n=(self._target_col, "size"), positives=(self._target_col, "sum"))
            .reset_index()
        )
        agg["target_rate"] = agg["positives"] / agg["n"]
        return agg.sort_values("target_rate", ascending=False)

    def correlation_with_target(self, df: pd.DataFrame, numeric_cols: list) -> pd.DataFrame:
        corrs = df[numeric_cols + [self._target_col]].corr(numeric_only=True)[self._target_col]
        corrs = corrs.drop(self._target_col).sort_values(key=abs, ascending=False)
        return corrs.to_frame("correlation_with_target")
