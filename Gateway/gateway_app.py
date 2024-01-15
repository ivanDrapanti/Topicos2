import json
import time
import requests
import requests_cache
from flask import Flask, Response, request
import bson.json_util as json_util
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from requests_cache import CachedSession

app = Flask(__name__)
url_mongo = "http://host.docker.internal:5001" # Not used
url_logger = "http://host.docker.internal:5002"
url_authenticator = "http://host.docker.internal:5003"
url_predictor = "http://host.docker.internal:5004"
base_headers = {"Content-Type": "application/json"}
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per second"],
    storage_uri="memory://")  # inicializacion por defecto
type_user = "FREEMIUN"
requests_cache.install_cache('predictor_cache')


def extract_key(request, *args, **kwargs):
    # Utiliza la URL + body como clave
    return request.url + str(request.body)


session = CachedSession(cache_name='predictor_cache', backend='sqlite', expire_after=60, key_fn=extract_key)
session.cache.clear()


def login_by_authenticator(username, password):
    data = {'username': username, 'password': password}
    return requests.post(url_authenticator + "/login", data=json.dumps(data), headers=base_headers)


def validate_client(token):
    header = {'Authorization': token}
    return requests.post(url_authenticator + "/validate", headers=header)


def log_mongo(token, data):
    body = {'token': token, 'data': data}
    return requests.post(url_logger + "/log", json=body, headers=base_headers)


@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        response = login_by_authenticator(username, password)
        if response is not None:
            response = Response(response=response.text, status=200, mimetype="application/json")
            return response
        else:
            return Response(response="Internal error", status=503, mimetype="application/json")
    except Exception as e:
        return json.dumps({'error': str(e)})


def generate_body_predictor(data):
    nivel_colesterol = float(data.get('nivel_colesterol'))
    presion_arterial = float(data.get('presion_arterial'))
    azucar = float(data.get('azucar'))
    edad = float(data.get('edad'))
    sobrepeso = float(data.get('sobrepeso'))
    tabaquismo = float(data.get('tabaquismo'))
    return {'nivel_colesterol': nivel_colesterol, 'presion_arterial': presion_arterial, 'azucar': azucar, 'edad': edad,
            'sobrepeso': sobrepeso, 'tabaquismo': tabaquismo}


def predict_by_predictor(data):
    return session.get(url=url_predictor + "/predict", json=data, headers=base_headers)


@limiter.limit("5 per second")
def predict_by_freemium(data):
    return predict_by_predictor(data)


@limiter.limit("50 per second")
def predict_by_preemium(data):
    return predict_by_predictor(data)


@app.route("/predict", methods=['GET'])
def predict():
    try:
        inicio = time.time()
        token = request.headers.get('Authorization')
        response = validate_client(token)
        if response.status_code != 200:
            return Response(response="invalid access", status=503, mimetype="application/json")

        body = generate_body_predictor(request.get_json())
        type = response.json()['type']
        if type == "FREEMIUM":
            response = predict_by_freemium(body)
        elif type == "PREMIUM":
            response = predict_by_preemium(body)
        else:
            Response(response="Invalid user", status=500, mimetype="application/json")
        fin = time.time()
        duration = fin - inicio
        data = {'params': body, 'duration': duration, 'result': response.text }
        log_mongo(token, data)
        if response is not None and response.status_code == 200:
            return Response(response=response.text, status=200, mimetype="application/json")
        else:
            Response(response="Internal error", status=500, mimetype="application/json")

    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/ping", methods=['GET'])
def ping():
    return Response(response=json_util.dumps("successfully"), status=200, mimetype="application/json")


if __name__ == "__main__":
    session.cache.clear()
    app.run(host='0.0.0.0', port=5000, debug=True)
