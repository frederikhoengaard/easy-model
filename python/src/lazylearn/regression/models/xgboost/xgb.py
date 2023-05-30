from models.models import Dataset
from pipeline.pipeline import RegressionPipeline
from preprocessing.encoding.encoders import OrdinalConverter
from regression.models.xgboost.xgb_regressor_steps.hpo_step import (  # noqa
    HyperParameterOptimizationStep,
)
from regression.models.xgboost.xgb_regressor_steps.regressor_step import (
    XGBRegressorStep,
)


class XGBRegressionRunner:
    def __init__(self, target, dataset, random_state=None):
        self.name = "XGBRegressor"
        self.target = target
        self.dataset: Dataset = dataset
        self.random_state = random_state
        self.pipeline = RegressionPipeline()
        self.pipeline.target = target

        self.pipeline.train_features_df = self.dataset.partitions[
            "train"
        ].copy()  # noqa
        self.pipeline.train_targets = self.dataset.partitions["train"][target]
        self.pipeline.holdout_features_df = self.dataset.partitions[
            "test"
        ].copy()  # noqa
        self.pipeline.holdout_targets = self.dataset.partitions["test"][target]

    def fit(self):
        # preprocess numeric vars
        cat_vars = self.dataset.type_collections["categorical"]
        num_vars = self.dataset.type_collections["numeric"]
        self.pipeline.feature_list.extend(num_vars)

        self.pipeline.add(OrdinalConverter(cat_vars=cat_vars))

        self.pipeline.add(
            HyperParameterOptimizationStep(random_state=self.random_state)
        )

        self.pipeline.add(XGBRegressorStep())

        self.pipeline.fit()

    def predict(self, features):
        self.pipeline.tmp_test = features
        return self.pipeline.predict()
