import pickle
import json
import numpy as np
from sklearn.externals import joblib
from sklearn.linear_model import Ridge
from azureml.core.model import Model
from azureml.monitoring import ModelDataCollector
import os

def init():
    global input_dc
    global prediction_dc
    global model
    # load model
    model_path = Model.get_model_path('best_model')
    model = joblib.load(model_path)
    # init MDC
    input_dc = ModelDataCollector(
        model_name="best_model",
        designation='inputs',
        feature_names=['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6'])

    prediction_dc = ModelDataCollector(
        model_name="best_model",
        designation='predictions',
        feature_names=['prediction'])

    # input_dc = ModelDataCollector(
    #     model_name="best_model",
    #     identifier='inputs',
    #     feature_names=['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6'])

    # prediction_dc = ModelDataCollector(
    #     model_name="best_model",
    #     identifier='predictions',
    #     feature_names=['prediction'])


# note you can pass in multiple rows for scoring
def run(raw_data):
    try:
        data = json.loads(raw_data)['data']
        data = np.array(data)
        correlation = input_dc.collect(data)
        prediction = model.predict(data)

        # Augment prediction with input correlation
        aug = prediction_dc.add_correlations(prediction, correlation)
        prediction_dc.collect(aug)
        
        return prediction.tolist()
    except Exception as e:
        result = str(e)
        return result