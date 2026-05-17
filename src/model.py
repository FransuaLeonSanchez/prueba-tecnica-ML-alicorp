from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from xgboost import XGBClassifier
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    _LGB_AVAILABLE = True
except ImportError:
    _LGB_AVAILABLE = False


@dataclass
class TrainResult:
    name: str
    pipeline: Pipeline
    cv_auc_mean: float
    cv_auc_std: float
    test_predictions: np.ndarray = field(default_factory=lambda: np.array([]))
    test_probabilities: np.ndarray = field(default_factory=lambda: np.array([]))


class ModelTrainer:
    def __init__(
        self,
        categorical_features: List[str],
        numeric_features: List[str],
        random_state: int = 42,
        test_size: float = 0.2,
        cv_folds: int = 5,
    ) -> None:
        self._cat_features = categorical_features
        self._num_features = numeric_features
        self._random_state = random_state
        self._test_size = test_size
        self._cv_folds = cv_folds

    def split(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        return train_test_split(
            X, y, test_size=self._test_size, random_state=self._random_state, stratify=y
        )

    def _preprocessor(self) -> ColumnTransformer:
        return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), self._num_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), self._cat_features),
            ],
            remainder="drop",
        )

    def candidate_models(self) -> Dict[str, object]:
        models: Dict[str, object] = {
            "LogisticRegression": LogisticRegression(
                max_iter=2000, class_weight="balanced", random_state=self._random_state
            ),
            "RandomForest": RandomForestClassifier(
                n_estimators=400,
                max_depth=10,
                min_samples_leaf=10,
                class_weight="balanced",
                n_jobs=-1,
                random_state=self._random_state,
            ),
            "GradientBoosting": GradientBoostingClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                random_state=self._random_state,
            ),
        }
        if _XGB_AVAILABLE:
            models["XGBoost"] = XGBClassifier(
                n_estimators=400,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_lambda=1.0,
                scale_pos_weight=5.0,
                eval_metric="auc",
                n_jobs=-1,
                random_state=self._random_state,
                tree_method="hist",
            )
        if _LGB_AVAILABLE:
            models["LightGBM"] = LGBMClassifier(
                n_estimators=500,
                max_depth=-1,
                num_leaves=63,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                class_weight="balanced",
                n_jobs=-1,
                random_state=self._random_state,
                verbosity=-1,
            )
        return models

    def build_pipeline(self, estimator) -> Pipeline:
        return Pipeline(
            steps=[
                ("preprocessor", self._preprocessor()),
                ("model", estimator),
            ]
        )

    def cross_validate_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Tuple[float, float]]:
        cv = StratifiedKFold(n_splits=self._cv_folds, shuffle=True, random_state=self._random_state)
        results: Dict[str, Tuple[float, float]] = {}
        for name, est in self.candidate_models().items():
            pipe = self.build_pipeline(est)
            scores = cross_val_score(pipe, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
            results[name] = (float(scores.mean()), float(scores.std()))
        return results

    def fit_final(self, name: str, X_train: pd.DataFrame, y_train: pd.Series) -> Pipeline:
        estimators = self.candidate_models()
        if name not in estimators:
            raise KeyError(f"Modelo desconocido: {name}")
        pipe = self.build_pipeline(estimators[name])
        pipe.fit(X_train, y_train)
        return pipe
