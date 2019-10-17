import pickle
import json
import numpy as np
from sklearn.externals import joblib
from azureml.core.model import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType

from azureml.monitoring import ModelDataCollector


def init():
    global model
    global inputs_dc
    # blah
    inputs_dc = ModelDataCollector('elevation-regression-model.pkl', designation='inputs',
                                   feature_names=['latitude', 'longitude', 'temperature', 'windAngle', 'windSpeed'])
    # note here "elevation-regression-model.pkl" is the name of the model registered under
    # this is a different behavior than before when the code is run locally, even though the code is the same.
    model_path = Model.get_model_path('elevation-regression-model.pkl')
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)


input_sample = np.array([[30, -85, 21, 150, 6]])
output_sample = np.array([8.995])


@input_schema('data', NumpyParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        inputs_dc.collect(data)
        result = model.predict(data)
        # you can return any datatype as long as it is JSON-serializable
        return result.tolist()
    except Exception as e:
        error = str(e)
        return error
