from dataclasses import dataclass
from typing import List
import numpy as np
import pandas as pd


@dataclass
class ActionTier:
    name: str
    score_min: float
    score_max: float
    accion_recomendada: str
    descripcion: str


class StrategyBuilder:
    def __init__(self) -> None:
        self._tiers: List[ActionTier] = [
            ActionTier(
                name="Tier A - Activacion premium",
                score_min=0.70,
                score_max=1.01,
                accion_recomendada="Cliente Perfecto + Mercaderismo + Linea de credito",
                descripcion="Maxima inversion comercial: 15% incremental esperado.",
            ),
            ActionTier(
                name="Tier B - Activacion estandar",
                score_min=0.40,
                score_max=0.70,
                accion_recomendada="Asignar 1 iniciativa (Perfecto o Mercaderismo)",
                descripcion="Inversion media: incremental esperado entre 10% y 15%.",
            ),
            ActionTier(
                name="Tier C - Nurturing",
                score_min=0.20,
                score_max=0.40,
                accion_recomendada="Comunicacion comercial + descuentos focalizados",
                descripcion="Test & learn antes de invertir en mercaderismo.",
            ),
            ActionTier(
                name="Tier D - Mantenimiento",
                score_min=0.0,
                score_max=0.20,
                accion_recomendada="Operacion regular, sin inversion adicional",
                descripcion="Bajo potencial: 0.5% incremental esperado.",
            ),
        ]

    def tiers(self) -> List[ActionTier]:
        return list(self._tiers)

    def assign_tier(self, scores: np.ndarray) -> np.ndarray:
        tier_names = np.array([self._lookup_tier(s) for s in scores])
        return tier_names

    def _lookup_tier(self, score: float) -> str:
        for tier in self._tiers:
            if tier.score_min <= score < tier.score_max:
                return tier.name
        return self._tiers[-1].name

    def tier_summary(
        self, clientes: pd.DataFrame, score_col: str, amount_col: str = "total_amount"
    ) -> pd.DataFrame:
        df = clientes.copy()
        df["tier"] = self.assign_tier(df[score_col].values)
        agg = (
            df.groupby("tier")
            .agg(
                clientes=(score_col, "size"),
                score_promedio=(score_col, "mean"),
                ventas_periodo=(amount_col, "sum"),
                ticket_promedio=(amount_col, "mean"),
                target_real_rate=("target", "mean"),
            )
            .reset_index()
            .sort_values("score_promedio", ascending=False)
        )
        return agg
