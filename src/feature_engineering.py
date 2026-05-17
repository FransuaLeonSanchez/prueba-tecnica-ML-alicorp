from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureGroups:
    base: List[str]
    monetary: List[str]
    behavioral: List[str]
    diversity: List[str]
    recency_frequency: List[str]
    category_share: List[str]
    trend: List[str]


class TransactionalFeatureBuilder:
    def __init__(self, reference_date: Optional[pd.Timestamp] = None) -> None:
        self._reference_date = reference_date

    def build(self, trans: pd.DataFrame) -> pd.DataFrame:
        ref_date = self._reference_date or trans["date"].max()
        monetary = self._monetary_features(trans)
        behavioral = self._behavioral_features(trans)
        diversity = self._diversity_features(trans)
        rf = self._recency_frequency_features(trans, ref_date)
        cat_share = self._category_share_features(trans)
        trend = self._trend_features(trans)

        out = (
            monetary
            .merge(behavioral, on="customer_id", how="outer")
            .merge(diversity, on="customer_id", how="outer")
            .merge(rf, on="customer_id", how="outer")
            .merge(cat_share, on="customer_id", how="outer")
            .merge(trend, on="customer_id", how="outer")
        )
        return out.fillna(0)

    @staticmethod
    def _monetary_features(trans: pd.DataFrame) -> pd.DataFrame:
        g = trans.groupby("customer_id")
        out = g.agg(
            total_amount=("amount", "sum"),
            mean_amount=("amount", "mean"),
            median_amount=("amount", "median"),
            std_amount=("amount", "std"),
            max_amount=("amount", "max"),
            min_amount=("amount", "min"),
            total_discount=("discount", "sum"),
            mean_discount=("discount", "mean"),
            total_net_amount=("net_amount", "sum"),
            mean_discount_ratio=("discount_ratio", "mean"),
        ).reset_index()
        out["std_amount"] = out["std_amount"].fillna(0)
        out["amount_volatility"] = np.where(
            out["mean_amount"] > 0, out["std_amount"] / out["mean_amount"], 0
        )
        return out

    @staticmethod
    def _behavioral_features(trans: pd.DataFrame) -> pd.DataFrame:
        g = trans.groupby("customer_id")
        out = g.agg(
            n_transactions=("date", "count"),
            n_unique_dates=("date", "nunique"),
            n_unique_products=("product_id", "nunique"),
            n_unique_categories=("category_product", "nunique"),
            active_weeks=("week", "nunique"),
            active_months=("year_month", "nunique"),
        ).reset_index()
        out["avg_basket_size"] = np.where(
            out["n_unique_dates"] > 0, out["n_transactions"] / out["n_unique_dates"], 0
        )
        return out

    @staticmethod
    def _diversity_features(trans: pd.DataFrame) -> pd.DataFrame:
        cat_counts = trans.groupby(["customer_id", "category_product"]).size().unstack(fill_value=0)
        totals = cat_counts.sum(axis=1).replace(0, np.nan)
        shares = cat_counts.div(totals, axis=0)
        entropy = -(shares * np.log(shares.where(shares > 0))).sum(axis=1)
        hhi = (shares**2).sum(axis=1)
        out = pd.DataFrame(
            {
                "category_entropy": entropy.fillna(0).values,
                "category_hhi": hhi.fillna(0).values,
            },
            index=cat_counts.index,
        ).reset_index()
        return out

    @staticmethod
    def _recency_frequency_features(trans: pd.DataFrame, ref_date: pd.Timestamp) -> pd.DataFrame:
        g = trans.groupby("customer_id")
        first = g["date"].min().rename("first_purchase")
        last = g["date"].max().rename("last_purchase")
        out = pd.concat([first, last], axis=1).reset_index()
        out["recency_days"] = (ref_date - out["last_purchase"]).dt.days.astype(int)
        out["tenure_in_period_days"] = (out["last_purchase"] - out["first_purchase"]).dt.days.astype(int)
        return out.drop(columns=["first_purchase", "last_purchase"])

    @staticmethod
    def _category_share_features(trans: pd.DataFrame) -> pd.DataFrame:
        amount_by_cat = (
            trans.groupby(["customer_id", "category_product"])["amount"].sum().unstack(fill_value=0)
        )
        totals = amount_by_cat.sum(axis=1).replace(0, np.nan)
        share = amount_by_cat.div(totals, axis=0).fillna(0)
        share.columns = [f"share_{c}" for c in share.columns]
        return share.reset_index()

    @staticmethod
    def _trend_features(trans: pd.DataFrame) -> pd.DataFrame:
        mid = trans["date"].min() + (trans["date"].max() - trans["date"].min()) / 2
        early = trans[trans["date"] < mid].groupby("customer_id")["amount"].sum().rename("amount_early")
        late = trans[trans["date"] >= mid].groupby("customer_id")["amount"].sum().rename("amount_late")
        out = pd.concat([early, late], axis=1).fillna(0)
        out["amount_growth_ratio"] = np.where(
            out["amount_early"] > 0, out["amount_late"] / out["amount_early"], 0
        )
        out["amount_growth_abs"] = out["amount_late"] - out["amount_early"]
        return out.reset_index()


class FeatureAssembler:
    def __init__(self) -> None:
        pass

    def assemble(self, clientes: pd.DataFrame, transactional_features: pd.DataFrame) -> pd.DataFrame:
        merged = clientes.merge(transactional_features, on="customer_id", how="left")
        for col in transactional_features.columns:
            if col == "customer_id":
                continue
            if merged[col].isna().any():
                merged[col] = merged[col].fillna(0)
        return merged
