import numpy as np
import tensorflow as tf
import json
from flask import Flask, Response, request
import bson.json_util as json_util

app = Flask(__name__)
model = tf.keras.models.load_model('predictor.h5')


def normalize(data, min, max):
    return (data - min) / (max - min)


def predict_by_model(data):
    nivel_colesterol = normalize(float(data.get('nivel_colesterol')), 1.0, 3.0)
    presion_arterial = normalize(float(data.get('presion_arterial')), 0.6, 1.8)
    azucar = normalize(float(data.get('azucar')), 0.5, 2.0)
    edad = normalize(float(data.get('edad')), 0.0, 99.0)
    sobrepeso = float(data.get('sobrepeso'))
    tabaquismo = float(data.get('tabaquismo'))
    data_to_consume = np.array(
        [[nivel_colesterol, presion_arterial, azucar, edad, sobrepeso, tabaquismo]])
    return model.predict(data_to_consume)[0, 0]


@app.route("/predict", methods=['GET'])
def predict():
    try:
        data = request.get_json()
        value = predict_by_model(data)
        print(value)
        if 0.98 <= value <= 1.02:
            return Response(response=json_util.dumps("hay riesgo cardiaco"), status=200, mimetype="application/json")
        else:
            return Response(response=json_util.dumps("no hay riesgo cardiaco"), status=200, mimetype="application/json")
    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/ping", methods=['GET'])
def ping():
    return Response(response=json_util.dumps("successfully"), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
