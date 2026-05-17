from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Config:
    project_root: Path = Path(__file__).resolve().parents[1]
    data_clientes_path: Path = field(init=False)
    data_transaccional_path: Path = field(init=False)
    graficos_dir: Path = field(init=False)
    outputs_dir: Path = field(init=False)
    reports_dir: Path = field(init=False)

    target_col: str = "target"
    id_col: str = "customer_id"

    excel_date_origin: str = "1899-12-30"

    random_state: int = 42
    test_size: float = 0.2

    incremental_potencial: float = 0.10
    incremental_potencial_iniciativa: float = 0.15
    incremental_no_potencial: float = 0.005

    business_categorical: List[str] = field(
        default_factory=lambda: ["territory_id", "segment"]
    )
    business_binary: List[str] = field(
        default_factory=lambda: [
            "has_credit_line",
            "has_perfect_customer",
            "has_marketing_impulse",
        ]
    )
    business_numeric: List[str] = field(default_factory=lambda: ["age_alicorp"])

    figure_dpi: int = 130
    figure_size: tuple = (10, 6)
    palette_primary: str = "#C8102E"
    palette_secondary: str = "#1F1F1F"
    palette_accent: str = "#F2A900"

    def __post_init__(self):
        object.__setattr__(self, "data_clientes_path", self.project_root / "data_cliente.csv")
        object.__setattr__(self, "data_transaccional_path", self.project_root / "data_transaccional.csv")
        object.__setattr__(self, "graficos_dir", self.project_root / "graficos")
        object.__setattr__(self, "outputs_dir", self.project_root / "outputs")
        object.__setattr__(self, "reports_dir", self.project_root / "reports")
        for d in (self.graficos_dir, self.outputs_dir, self.reports_dir):
            d.mkdir(parents=True, exist_ok=True)

    @property
    def model_features(self) -> List[str]:
        return self.business_categorical + self.business_binary + self.business_numeric

    @property
    def incremental_by_segment(self) -> Dict[str, float]:
        return {
            "potencial_con_iniciativa": self.incremental_potencial_iniciativa,
            "potencial_sin_iniciativa": self.incremental_potencial,
            "no_potencial": self.incremental_no_potencial,
        }
