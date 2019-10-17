import numpy as np
import os
import json

from azureml.core.model import Model

from sklearn.linear_model import Ridge

import joblib


def init():
    global model

    model_root = Model.get_model_path('sklearn-diabetes-regr')
    # Load our saved model
    model = joblib.load(model_root)


# note you can pass in multiple rows for scoring
def run(raw_data):
    try:
        data = json.loads(raw_data)['data']
        data = np.array(data)
        result = model.predict(data)

        # you can return any data type as long as it is JSON-serializable
        return result.tolist()
    except Exception as e:
        result = str(e)
        return result
