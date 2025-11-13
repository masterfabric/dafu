"""
Customer analytics modeling workflows.

Provides interactive pipelines for:
- Multi-class churn propensity using `target_class`
- Binary churn scoring derived from last-month activity (`final_churn`)
- Customer lifetime value (CLV) regression
- RFM & behavioural segmentation
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

try:
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression, PoissonRegressor
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
        f1_score,
        mean_absolute_percentage_error,
        mean_squared_error,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.mixture import GaussianMixture
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "scikit-learn is required for customer analytics modeling. "
        "Install with `pip install scikit-learn`."
    ) from exc

try:
    import xgboost as xgb

    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False

try:
    import lightgbm as lgb

    _HAS_LGB = True
except ImportError:
    _HAS_LGB = False

try:
    from catboost import CatBoostClassifier, CatBoostRegressor

    _HAS_CATBOOST = True
except ImportError:
    _HAS_CATBOOST = False

try:
    import hdbscan

    _HAS_HDBSCAN = True
except ImportError:
    _HAS_HDBSCAN = False


NUMERIC_FEATURES = [
    "ses_rec",
    "ses_rec_avg",
    "ses_rec_sd",
    "ses_rec_cv",
    "user_rec",
    "ses_n",
    "ses_n_r",
    "int_n",
    "int_n_r",
    "tran_n",
    "tran_n_r",
    "rev_sum",
    "rev_sum_r",
    "major_spend_r",
    "int_cat_n_avg",
    "int_itm_n_avg",
    "ses_mo_avg",
    "ses_mo_sd",
    "ses_ho_avg",
    "ses_ho_sd",
    "ses_wknd_r",
    "ses_len_avg",
    "time_to_int",
    "time_to_tran",
]

DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass
class ClassificationResult:
    model_name: str
    metrics: Dict[str, float]
    report: str
    confusion: np.ndarray
    predictions: pd.DataFrame


@dataclass
class RegressionResult:
    model_name: str
    metrics: Dict[str, float]
    predictions: pd.DataFrame


@dataclass
class SegmentationResult:
    algorithm: str
    params: Dict[str, float]
    assignments: pd.DataFrame


def _safe_float(value: float) -> float:
    """Format floats for printing; tolerate NaNs."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return float("nan")
    return float(f"{value:.4f}")


def _prompt_yes_no(message: str, default: bool = True) -> bool:
    """Prompt user for a yes/no answer."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        response = input(f"{message}{suffix}").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def _ensure_results_dir(path: Optional[str]) -> Path:
    """Resolve and ensure output directory."""
    if path:
        resolved = Path(path).expanduser()
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resolved = DEFAULT_RESULTS_DIR / f"analytics_run_{timestamp}"
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


class CustomerAnalyticsModeler:
    """Interactive runner for churn, CLV, and segmentation analytics."""

    def __init__(
        self,
        default_dataset_path: Optional[str] = None,
        classification_data: Optional[pd.DataFrame] = None,
    ) -> None:
        self.default_dataset_path = (
            Path(default_dataset_path).expanduser()
            if default_dataset_path
            else None
        )
        self.dataset: Optional[pd.DataFrame] = classification_data
        self.dataset_path: Optional[Path] = self.default_dataset_path
        self.feature_columns: List[str] = []
        self.has_target: bool = False
        self.has_final_churn: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Entry point for interactive modeling."""
        self._display_intro()
        if not self._ensure_dataset_loaded():
            print("❌ Modeling aborted (dataset not loaded).")
            return

        while True:
            choice = self._prompt_pipeline_choice()
            if choice == "1":
                self._run_multiclass_churn()
            elif choice == "2":
                self._run_binary_churn()
            elif choice == "3":
                self._run_clv_regression()
            elif choice == "4":
                self._run_segmentation()
            else:
                print("Returning to main menu.")
                break

            if not _prompt_yes_no(
                "\nRun another pipeline on the same dataset?", default=False
            ):
                break

        print("\n✅ Modeling session finished.")

    # ------------------------------------------------------------------
    # Dataset Handling
    # ------------------------------------------------------------------
    def _ensure_dataset_loaded(self) -> bool:
        """Load dataset if not already available."""
        if self.dataset is not None:
            if not self.feature_columns:
                self._validate_required_columns()
            return True

        print("\n📁 DATASET SELECTION")
        print("-" * 60)
        print("Provide a classification dataset produced by feature engineering.")
        if self.default_dataset_path and self.default_dataset_path.exists():
            use_default = _prompt_yes_no(
                f"Use recent dataset at {self.default_dataset_path}? "
            )
            if use_default:
                self.dataset_path = self.default_dataset_path
            else:
                self.dataset_path = None

        while self.dataset is None:
            if not self.dataset_path:
                path_input = (
                    input("Enter dataset path (CSV): ")
                    .strip()
                    .strip('"')
                    .strip("'")
                )
                if not path_input:
                    print("Path is required.")
                    continue
                self.dataset_path = Path(path_input).expanduser()

            if not self.dataset_path.exists():
                print(f"❌ File not found: {self.dataset_path}")
                if _prompt_yes_no("Try another path?"):
                    self.dataset_path = None
                    continue
                return False

            try:
                self.dataset = pd.read_csv(self.dataset_path)
                print(f"✅ Loaded dataset with shape {self.dataset.shape}")
                self._validate_required_columns()
                self._describe_labels()
            except Exception as exc:  # pragma: no cover - interactive
                print(f"❌ Failed to load dataset: {exc}")
                self.dataset = None
                self.dataset_path = None
                if not _prompt_yes_no("Try another path?"):
                    return False

        return True

    def _validate_required_columns(self) -> None:
        """Ensure dataset has necessary columns and derive churn labels."""
        missing = [col for col in ["visitorid"] if col not in self.dataset.columns]
        if missing:
            raise ValueError(
                f"Dataset missing required columns: {', '.join(missing)}."
            )

        # Determine label availability
        self.has_target = "target_class" in self.dataset.columns
        if self.has_target:
            target_vals = self.dataset["target_class"].fillna(-1)
            final_churn = pd.Series(1, index=target_vals.index, dtype=int)
            final_churn[target_vals.isin([1, 2])] = 0
            final_churn[target_vals == 0] = 1
            # Treat unknown/negative values as churn risk
            final_churn[target_vals < 0] = 1
            self.dataset["final_churn"] = final_churn
            self.has_final_churn = True
        else:
            self.has_final_churn = "final_churn" in self.dataset.columns
            if self.has_final_churn:
                self.dataset["final_churn"] = (
                    self.dataset["final_churn"].fillna(1).astype(int)
                )

        # Feature list
        cat_columns = sorted(
            [
                col
                for col in self.dataset.columns
                if col.startswith("int_") and col.endswith("_n")
            ]
        )
        base_features = [col for col in NUMERIC_FEATURES if col in self.dataset.columns]
        self.feature_columns = [
            col
            for col in base_features + cat_columns
            if col not in {"target_class", "final_churn"}
        ]

        if not self.feature_columns:
            raise ValueError(
                "No feature columns available. Ensure feature engineering completed successfully."
            )

    def _describe_labels(self) -> None:
        """Log label availability for user clarity."""
        status = []
        if self.has_target:
            target_counts = (
                self.dataset["target_class"]
                .value_counts(dropna=False)
                .sort_index()
                .to_dict()
            )
            status.append(f"target_class detected (distribution: {target_counts})")
        if self.has_final_churn:
            churn_counts = (
                self.dataset["final_churn"]
                .value_counts(dropna=False)
                .sort_index()
                .to_dict()
            )
            status.append(f"final_churn available (distribution: {churn_counts})")
        if not status:
            status.append("no churn labels detected")
        print("  - " + " | ".join(status))

    # ------------------------------------------------------------------
    # Pipeline Selection
    # ------------------------------------------------------------------
    def _display_intro(self) -> None:
        """Display modeling overview."""
        print("\n" + "=" * 80)
        print("🤖 CUSTOMER ANALYTICS MODELING HUB")
        print("=" * 80)
        print("Three-layer analytics approach:")
        print("  1) Multi-class churn propensity (target_class)")
        print("  2) Binary churn scoring (final_churn)")
        print("  3) Customer lifetime value regression")
        print("  4) RFM & behavioural segmentation")
        print("Press any other key at menu to return.\n")

    def _prompt_pipeline_choice(self) -> str:
        """Prompt user for pipeline selection."""
        print("\n" + "-" * 60)
        print("Available pipelines:")
        if self.has_target:
            print("  1. Multi-class churn propensity (XGBoost, LightGBM, CatBoost, RF, Logistic)")
        else:
            print("  1. Multi-class churn propensity [requires target_class]")

        if self.has_final_churn:
            print("  2. Binary churn scoring (XGBoost, CatBoost, Logistic)")
        else:
            print("  2. Binary churn scoring [requires final_churn]")

        print("  3. CLV regression (GBM, XGBoost, CatBoost, Poisson)")
        print("  4. Segmentation (KMeans, GMM, HDBSCAN)")
        print("-" * 60)
        return input("Choose pipeline [1-4, other to exit]: ").strip()

    # ------------------------------------------------------------------
    # Multi-class churn
    # ------------------------------------------------------------------
    def _run_multiclass_churn(self) -> None:
        """Train and evaluate multi-class churn propensity models."""
        if not self.has_target:
            print("⚠️  target_class not found. Multi-class churn unavailable.")
            return

        df = self.dataset.dropna(subset=["target_class"]).copy()
        features = df[self.feature_columns].fillna(0)
        target = df["target_class"].astype(int)

        (
            x_train,
            x_test,
            y_train,
            y_test,
            _,
            visitors_test,
        ) = train_test_split(
            features,
            target,
            df["visitorid"],
            test_size=0.2,
            stratify=target,
            random_state=42,
        )

        models = self._available_multiclass_models()
        self._print_model_choices(models)
        selected = self._prompt_model_selection(models)

        results: List[ClassificationResult] = []
        for model_name in selected:
            print(f"\n▶ Training {model_name}...")
            estimator, needs_scaler = self._build_multiclass_model(model_name)
            steps: List[Tuple[str, object]] = []
            if needs_scaler:
                steps.append(("scaler", StandardScaler()))
            steps.append(("model", estimator))
            pipeline = Pipeline(steps)
            pipeline.fit(x_train, y_train)
            probas = pipeline.predict_proba(x_test)
            preds = np.argmax(probas, axis=1)

            metrics = {
                "accuracy": _safe_float(accuracy_score(y_test, preds)),
                "f1_macro": _safe_float(f1_score(y_test, preds, average="macro")),
                "f1_weighted": _safe_float(
                    f1_score(y_test, preds, average="weighted")
                ),
            }
            try:
                metrics["roc_auc_ovr"] = _safe_float(
                    roc_auc_score(y_test, probas, multi_class="ovr")
                )
            except Exception:
                metrics["roc_auc_ovr"] = float("nan")

            prob_df = pd.DataFrame(
                probas,
                columns=[f"prob_class_{c}" for c in sorted(target.unique())],
            )
            predictions = pd.DataFrame(
                {
                    "visitorid": visitors_test.values,
                    "true_class": y_test.values,
                    "predicted_class": preds,
                }
            ).reset_index(drop=True)
            predictions = pd.concat([predictions, prob_df], axis=1)

            results.append(
                ClassificationResult(
                    model_name=model_name,
                    metrics=metrics,
                    report=classification_report(y_test, preds, digits=4),
                    confusion=confusion_matrix(y_test, preds),
                    predictions=predictions,
                )
            )

        self._display_classification_summary(results)
        self._save_classification_results(results, pipeline_name="multiclass_churn")

    def _available_multiclass_models(self) -> List[str]:
        models = ["Random Forest", "Logistic Regression"]
        if _HAS_XGB:
            models.insert(0, "XGBoost")
        if _HAS_LGB:
            models.insert(1 if _HAS_XGB else 0, "LightGBM")
        if _HAS_CATBOOST:
            models.insert(len(models) - 1, "CatBoost")
        return models

    def _build_multiclass_model(self, name: str):
        lname = name.lower()
        if lname.startswith("xgboost"):
            return (
                xgb.XGBClassifier(
                    objective="multi:softprob",
                    num_class=3,
                    eval_metric="mlogloss",
                    learning_rate=0.1,
                    max_depth=6,
                    subsample=0.9,
                    colsample_bytree=0.8,
                    reg_lambda=1.0,
                    random_state=42,
                ),
                False,
            )
        if lname.startswith("lightgbm"):
            return (
                lgb.LGBMClassifier(
                    objective="multiclass",
                    num_class=3,
                    learning_rate=0.05,
                    n_estimators=400,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                ),
                False,
            )
        if lname.startswith("catboost"):
            return (
                CatBoostClassifier(
                    loss_function="MultiClass",
                    iterations=500,
                    learning_rate=0.1,
                    depth=6,
                    random_seed=42,
                    verbose=False,
                ),
                False,
            )
        if lname.startswith("random"):
            return (
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=None,
                    class_weight="balanced",
                    random_state=42,
                    n_jobs=-1,
                ),
                False,
            )
        return (
            LogisticRegression(
                multi_class="multinomial",
                solver="lbfgs",
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            ),
            True,
        )

    # ------------------------------------------------------------------
    # Binary churn
    # ------------------------------------------------------------------
    def _run_binary_churn(self) -> None:
        """Train and evaluate churn vs. active models."""
        if not self.has_final_churn:
            print("⚠️  final_churn column not found. Binary churn unavailable.")
            return

        df = self.dataset.copy()
        df["final_churn"] = df["final_churn"].fillna(1).astype(int)
        features = df[self.feature_columns].fillna(0)
        target = df["final_churn"]

        (
            x_train,
            x_test,
            y_train,
            y_test,
            _,
            visitors_test,
        ) = train_test_split(
            features,
            target,
            df["visitorid"],
            test_size=0.2,
            stratify=target,
            random_state=42,
        )

        models = self._available_binary_models()
        self._print_model_choices(models)
        selected = self._prompt_model_selection(models)

        results: List[ClassificationResult] = []
        for model_name in selected:
            print(f"\n▶ Training {model_name}...")
            estimator, needs_scaler = self._build_binary_model(model_name)
            steps: List[Tuple[str, object]] = []
            if needs_scaler:
                steps.append(("scaler", StandardScaler()))
            steps.append(("model", estimator))
            pipeline = Pipeline(steps)
            pipeline.fit(x_train, y_train)
            probs = pipeline.predict_proba(x_test)[:, 1]
            preds = (probs >= 0.5).astype(int)

            metrics = {
                "accuracy": _safe_float(accuracy_score(y_test, preds)),
                "precision": _safe_float(
                    precision_score(y_test, preds, zero_division=0)
                ),
                "recall": _safe_float(
                    recall_score(y_test, preds, zero_division=0)
                ),
                "f1": _safe_float(f1_score(y_test, preds, zero_division=0)),
            }
            try:
                metrics["roc_auc"] = _safe_float(roc_auc_score(y_test, probs))
            except Exception:
                metrics["roc_auc"] = float("nan")

            results.append(
                ClassificationResult(
                    model_name=model_name,
                    metrics=metrics,
                    report=classification_report(y_test, preds, digits=4),
                    confusion=confusion_matrix(y_test, preds),
                    predictions=pd.DataFrame(
                        {
                            "visitorid": visitors_test.values,
                            "true_churn": y_test.values,
                            "predicted_churn": preds,
                            "prob_churn": probs,
                        }
                    ),
                )
            )

        self._display_classification_summary(results)
        self._save_classification_results(results, pipeline_name="binary_churn")

    def _available_binary_models(self) -> List[str]:
        models = ["Logistic Regression"]
        if _HAS_XGB:
            models.insert(0, "XGBoost")
        if _HAS_CATBOOST:
            models.insert(1 if _HAS_XGB else 0, "CatBoost")
        return models

    def _build_binary_model(self, name: str):
        lname = name.lower()
        if lname.startswith("xgboost"):
            return (
                xgb.XGBClassifier(
                    objective="binary:logistic",
                    eval_metric="auc",
                    learning_rate=0.05,
                    max_depth=6,
                    subsample=0.9,
                    colsample_bytree=0.8,
                    reg_lambda=1.0,
                    random_state=42,
                ),
                False,
            )
        if lname.startswith("catboost"):
            return (
                CatBoostClassifier(
                    loss_function="Logloss",
                    iterations=500,
                    learning_rate=0.05,
                    depth=6,
                    class_weights=[1, 2],
                    random_seed=42,
                    verbose=False,
                ),
                False,
            )
        return (
            LogisticRegression(
                solver="liblinear",
                class_weight="balanced",
                random_state=42,
            ),
            True,
        )

    # ------------------------------------------------------------------
    # CLV regression
    # ------------------------------------------------------------------
    def _run_clv_regression(self) -> None:
        """Run regression models for CLV-type targets."""
        df = self.dataset.copy()
        num_cols = sorted(
            {
                *self.feature_columns,
                *[
                    col
                    for col in df.select_dtypes(include=[np.number]).columns
                    if col not in {"target_class", "final_churn"}
                ],
            }
        )

        print("\n💰 CLV REGRESSION")
        print("Numeric columns available as potential targets:")
        for col in num_cols:
            print(f"  - {col}")

        target_col = None
        while not target_col:
            candidate = input(
                "Enter target column for regression (e.g., future_revenue): "
            ).strip()
            if candidate in num_cols:
                target_col = candidate
            else:
                print("Column not found or not numeric. Please try again.")

        df = df.dropna(subset=[target_col])
        y = df[target_col].astype(float)
        X = df[self.feature_columns].fillna(0)

        (
            x_train,
            x_test,
            y_train,
            y_test,
            _,
            visitors_test,
        ) = train_test_split(
            X,
            y,
            df["visitorid"],
            test_size=0.2,
            random_state=42,
        )

        models = self._available_regression_models(target_col)
        self._print_model_choices(models)
        selected = self._prompt_model_selection(models)

        results: List[RegressionResult] = []
        for model_name in selected:
            print(f"\n▶ Training {model_name}...")
            estimator, needs_scaler = self._build_regression_model(
                model_name, target_col
            )
            steps: List[Tuple[str, object]] = []
            if needs_scaler:
                steps.append(("scaler", StandardScaler()))
            steps.append(("model", estimator))
            pipeline = Pipeline(steps)
            pipeline.fit(x_train, y_train)
            preds = pipeline.predict(x_test)

            results.append(
                RegressionResult(
                    model_name=model_name,
                    metrics={
                        "rmse": _safe_float(
                            math.sqrt(mean_squared_error(y_test, preds))
                        ),
                        "mape": _safe_float(
                            mean_absolute_percentage_error(y_test, preds)
                        ),
                    },
                    predictions=pd.DataFrame(
                        {
                            "visitorid": visitors_test.values,
                            "actual": y_test.values,
                            "predicted": preds,
                        }
                    ),
                )
            )

        self._display_regression_summary(results)
        self._save_regression_results(results, pipeline_name=f"clv_{target_col}")

    def _available_regression_models(self, target_col: str) -> List[str]:
        models = ["Gradient Boosting"]
        if _HAS_XGB:
            models.append("XGBoost Regressor")
        if _HAS_CATBOOST:
            models.append("CatBoost Regressor")
        if (self.dataset[target_col] >= 0).all():
            models.append("Poisson Regression")
        return models

    def _build_regression_model(self, name: str, target_col: str):
        lname = name.lower()
        if lname.startswith("gradient"):
            return (
                GradientBoostingRegressor(
                    learning_rate=0.05,
                    n_estimators=400,
                    max_depth=3,
                    random_state=42,
                ),
                False,
            )
        if lname.startswith("xgboost"):
            return (
                xgb.XGBRegressor(
                    objective="reg:squarederror",
                    learning_rate=0.05,
                    n_estimators=500,
                    max_depth=6,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_lambda=1.0,
                    random_state=42,
                ),
                False,
            )
        if lname.startswith("catboost"):
            return (
                CatBoostRegressor(
                    loss_function="RMSE",
                    iterations=600,
                    learning_rate=0.05,
                    depth=6,
                    random_seed=42,
                    verbose=False,
                ),
                False,
            )
        if lname.startswith("poisson"):
            return (
                PoissonRegressor(alpha=1e-4, max_iter=1000, warm_start=True),
                True,
            )

        raise ValueError(f"Unsupported regression model: {name}")

    # ------------------------------------------------------------------
    # Segmentation
    # ------------------------------------------------------------------
    def _run_segmentation(self) -> None:
        """Execute RFM & behavioural segmentation."""
        df = self.dataset.copy()
        default_rfm = [col for col in ["ses_rec", "ses_n", "rev_sum"] if col in df.columns]

        print("\n🧭 SEGMENTATION PIPELINES")
        include_behavioral = _prompt_yes_no(
            "Include behavioural intensities (int_* columns)?"
        )

        if include_behavioral:
            behavioural = [
                col for col in self.feature_columns if col.startswith("int_")
            ]
            feature_cols = sorted(set(default_rfm + behavioural))
        else:
            feature_cols = default_rfm

        if not feature_cols:
            print("❌ No segmentation features available.")
            return

        data = df[feature_cols].fillna(0)
        scaled = StandardScaler().fit_transform(data)

        algorithms = self._available_segmentation_algorithms()
        self._print_model_choices(algorithms)
        selected = self._prompt_model_selection(algorithms)

        results: List[SegmentationResult] = []
        for algo in selected:
            print(f"\n▶ Running {algo} segmentation...")
            if algo.startswith("K-Means"):
                k = self._prompt_int("Number of clusters (k)", default=4, minimum=2)
                model = KMeans(n_clusters=k, random_state=42, n_init="auto")
                labels = model.fit_predict(scaled)
                results.append(
                    SegmentationResult(
                        algorithm=f"KMeans_{k}",
                        params={"n_clusters": k, "inertia": float(model.inertia_)},
                        assignments=pd.DataFrame(
                            {"visitorid": df["visitorid"].values, "cluster": labels}
                        ),
                    )
                )
            elif algo.startswith("Gaussian Mixture"):
                comp = self._prompt_int(
                    "Number of mixture components", default=4, minimum=2
                )
                model = GaussianMixture(
                    n_components=comp, covariance_type="full", random_state=42
                )
                labels = model.fit_predict(scaled)
                results.append(
                    SegmentationResult(
                        algorithm=f"GMM_{comp}",
                        params={
                            "n_components": comp,
                            "avg_log_likelihood": float(model.score(scaled)),
                        },
                        assignments=pd.DataFrame(
                            {"visitorid": df["visitorid"].values, "cluster": labels}
                        ),
                    )
                )
            elif algo.startswith("HDBSCAN") and _HAS_HDBSCAN:
                min_cluster = self._prompt_int(
                    "Minimum cluster size", default=15, minimum=5
                )
                min_samples = self._prompt_int(
                    "Minimum samples", default=5, minimum=1
                )
                model = hdbscan.HDBSCAN(
                    min_cluster_size=min_cluster,
                    min_samples=min_samples,
                    metric="euclidean",
                )
                labels = model.fit_predict(scaled)
                results.append(
                    SegmentationResult(
                        algorithm=f"HDBSCAN_{min_cluster}_{min_samples}",
                        params={
                            "min_cluster_size": min_cluster,
                            "min_samples": min_samples,
                            "outlier_score": float(np.nanmean(model.outlier_scores_)),
                        },
                        assignments=pd.DataFrame(
                            {"visitorid": df["visitorid"].values, "cluster": labels}
                        ),
                    )
                )

        self._display_segmentation_summary(results)
        self._save_segmentation_results(results, feature_cols)

    def _available_segmentation_algorithms(self) -> List[str]:
        algos = ["K-Means", "Gaussian Mixture"]
        if _HAS_HDBSCAN:
            algos.append("HDBSCAN")
        return algos

    @staticmethod
    def _prompt_model_selection(options: List[str]) -> List[str]:
        if not options:
            return []
        selection = input("Select models (comma-separated, default: all): ").strip()
        if not selection:
            return options
        try:
            indices = [int(val) for val in selection.split(",")]
            return [options[i - 1] for i in indices if 1 <= i <= len(options)]
        except Exception:
            print("Invalid selection. Using all available models.")
            return options

    @staticmethod
    def _print_model_choices(options: List[str]) -> None:
        if not options:
            print("No options available.")
            return
        print("Models available:")
        for idx, name in enumerate(options, start=1):
            print(f"  {idx}. {name}")

    @staticmethod
    def _prompt_int(message: str, default: int, minimum: int = 1) -> int:
        suffix = f" (default {default}): "
        while True:
            value = input(f"{message}{suffix}").strip()
            if not value:
                return default
            try:
                num = int(value)
                if num < minimum:
                    print(f"Value must be ≥ {minimum}.")
                    continue
                return num
            except ValueError:
                print("Enter a valid integer.")

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def _display_classification_summary(
        self, results: Sequence[ClassificationResult]
    ) -> None:
        print("\n" + "=" * 60)
        print("CLASSIFICATION SUMMARY")
        print("=" * 60)
        for res in results:
            print(f"\nModel: {res.model_name}")
            for metric, value in res.metrics.items():
                print(f"  {metric}: {value}")
            print(res.report)
            print("Confusion matrix:")
            print(res.confusion)

    def _display_regression_summary(
        self, results: Sequence[RegressionResult]
    ) -> None:
        print("\n" + "=" * 60)
        print("REGRESSION SUMMARY")
        print("=" * 60)
        for res in results:
            print(f"\nModel: {res.model_name}")
            for metric, value in res.metrics.items():
                print(f"  {metric}: {value}")

    def _display_segmentation_summary(
        self, results: Sequence[SegmentationResult]
    ) -> None:
        print("\n" + "=" * 60)
        print("SEGMENTATION SUMMARY")
        print("=" * 60)
        for res in results:
            print(f"\nAlgorithm: {res.algorithm}")
            for key, value in res.params.items():
                print(f"  {key}: {value}")
            unique_clusters = res.assignments["cluster"].nunique()
            print(f"  Clusters discovered: {unique_clusters} (noise labeled -1)")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _save_classification_results(
        self, results: Sequence[ClassificationResult], pipeline_name: str
    ) -> None:
        if not results:
            print("No classification results to save.")
            return

        if not _prompt_yes_no("Save classification outputs?", default=True):
            return

        default_dir = (
            str(self.dataset_path.parent / "results")
            if self.dataset_path
            else None
        )
        save_dir_input = input(
            "Directory to save results (Enter for default results/): "
        ).strip()
        final_dir = _ensure_results_dir(save_dir_input or default_dir)

        summary_rows = []
        for res in results:
            slug = res.model_name.lower().replace(" ", "_")
            pred_path = final_dir / f"{pipeline_name}_{slug}_predictions.csv"
            res.predictions.to_csv(pred_path, index=False)

            report_path = final_dir / f"{pipeline_name}_{slug}_report.txt"
            with report_path.open("w", encoding="utf-8") as fh:
                fh.write(res.report)
                fh.write("\nConfusion Matrix:\n")
                fh.write(np.array2string(res.confusion))

            summary_rows.append(
                {
                    "model": res.model_name,
                    **res.metrics,
                    "predictions_path": str(pred_path),
                    "report_path": str(report_path),
                }
            )

        summary_df = pd.DataFrame(summary_rows)
        summary_path = final_dir / f"{pipeline_name}_summary.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"\n✅ Saved classification outputs to {final_dir}")

    def _save_regression_results(
        self, results: Sequence[RegressionResult], pipeline_name: str
    ) -> None:
        if not results:
            print("No regression results to save.")
            return

        if not _prompt_yes_no("Save regression outputs?", default=True):
            return

        save_dir_input = input(
            "Directory to save results (Enter for default results/): "
        ).strip()
        final_dir = _ensure_results_dir(save_dir_input or None)

        rows = []
        for res in results:
            slug = res.model_name.lower().replace(" ", "_")
            pred_path = final_dir / f"{pipeline_name}_{slug}_predictions.csv"
            res.predictions.to_csv(pred_path, index=False)
            rows.append(
                {**res.metrics, "model": res.model_name, "predictions_path": str(pred_path)}
            )

        summary_path = final_dir / f"{pipeline_name}_summary.csv"
        pd.DataFrame(rows).to_csv(summary_path, index=False)
        print(f"\n✅ Saved regression outputs to {final_dir}")

    def _save_segmentation_results(
        self, results: Sequence[SegmentationResult], feature_cols: Sequence[str]
    ) -> None:
        if not results:
            print("No segmentation results to save.")
            return

        if not _prompt_yes_no("Save segmentation assignments?", default=True):
            return

        save_dir_input = input(
            "Directory to save results (Enter for default results/): "
        ).strip()
        final_dir = _ensure_results_dir(save_dir_input or None)

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "features": list(feature_cols),
        }
        (final_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        for res in results:
            slug = res.algorithm.lower().replace(" ", "_")
            output_path = final_dir / f"{slug}_clusters.csv"
            res.assignments.to_csv(output_path, index=False)
            print(f"  - Saved {res.algorithm} assignments to {output_path}")

        print(f"\n✅ Segmentation outputs saved to {final_dir}")


def launch_modeling(
    default_dataset_path: Optional[str] = None,
    classification_data: Optional[pd.DataFrame] = None,
) -> None:
    """Convenience wrapper used by the interactive CLI."""
    try:
        CustomerAnalyticsModeler(
            default_dataset_path=default_dataset_path,
            classification_data=classification_data,
        ).run()
    except KeyboardInterrupt:  # pragma: no cover - interactive
        print("\nModeling interrupted by user.")
    except Exception as exc:  # pragma: no cover - interactive
        print(f"\n❌ Modeling error: {exc}")
        import traceback

        traceback.print_exc()

