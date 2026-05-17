from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass(frozen=True)
class RawDataset:
    clientes: pd.DataFrame
    transacciones: pd.DataFrame


class DataLoader:
    def __init__(self, clientes_path: Path, transaccional_path: Path) -> None:
        self._clientes_path = clientes_path
        self._transaccional_path = transaccional_path

    def load(self) -> RawDataset:
        clientes = self._read_csv(self._clientes_path)
        transacciones = self._read_csv(self._transaccional_path)
        return RawDataset(clientes=clientes, transacciones=transacciones)

    @staticmethod
    def _read_csv(path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {path}")
        return pd.read_csv(path, encoding="utf-8-sig")
