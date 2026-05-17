# Prueba técnica - Data Scientist Alicorp

Modelo predictivo de potencial de incremental de venta para clientes del canal bodega.

## Estructura

```
.
├── data_cliente.csv             5,254 clientes
├── data_transaccional.csv       392,442 transacciones
├── Prueba técnica - DS.pdf      enunciado original
├── src/                         módulos del pipeline (SOLID)
│   ├── config.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── model.py
│   ├── evaluation.py
│   ├── strategy.py
│   └── visualization.py
├── notebooks/
│   └── alicorp_modelo_potencial.ipynb
├── graficos/                    15 gráficos generados
├── outputs/                     scores, métricas y CSVs de resultados
├── assets/                      logo y foto usados en la presentación
├── run_pipeline.py              corre el pipeline end-to-end
├── generate_presentation.py     genera el HTML de la presentación
└── index.html                   presentación final (10 slides)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

Correr el pipeline (genera gráficos, métricas y predicciones):

```bash
python run_pipeline.py
```

Regenerar la presentación:

```bash
python generate_presentation.py
```

Abrir la presentación:

```bash
xdg-open index.html
```

Abrir el notebook:

```bash
jupyter notebook notebooks/alicorp_modelo_potencial.ipynb
```

## Resultado

- Modelo final: Logistic Regression (mejor AUC en validación cruzada 5-fold).
- Uplift económico identificado: S/. 2.1M.
- Top 30% de clientes por score concentra el 42.5% del uplift.
- Segmentación operativa en 4 tiers para el equipo comercial.
