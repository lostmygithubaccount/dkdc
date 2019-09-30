# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import pickle
import numpy as np
import pandas as pd
import azureml.train.automl
from sklearn.externals import joblib
from azureml.core.model import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType


input_sample = pd.DataFrame(data=[{'usaf': 720735, 'wban': 73805, 'datetime': '2019-01-01T00:00:00.000Z', 'latitude': 30.349, 'longitude': -85.788, 'elevation': 21.0, 'windSpeed': 5.1, 'temperature': 21.1, 'seaLvlPressure': None, 'cloudCoverage': '', 'presentWeatherIndicator': None, 'pastWeatherIndicator': '', 'precipTime': None, 'precipDepth': None, 'snowDepth': None, 'stationName': 'NORTHWEST FLORIDA BEACHES INTL ARPT', 'countryOrRegion': 'US', 'p_k': '720735-73805', 'year': 2019, 'day': 1, 'version': 1.0}])
output_sample = np.array([0])


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = Model.get_model_path(model_name = 'AutoML998f7e4ba21')
    model = joblib.load(model_path)


@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        result = model.predict(data)
        return result.tolist()
    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})
    return json.dumps({"result": result.tolist()})
