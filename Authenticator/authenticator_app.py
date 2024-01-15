import hashlib
import requests
import json
from flask import Flask, Response, request
import bson.json_util as json_util

app = Flask(__name__)
url_mongo = "http://host.docker.internal:5001"
url_logger = "http://host.docker.internal:5002"
headers = {"Content-Type": "application/json"}


# Utility method to generate a token
def generar_token(username, password):
    # Se concatena usuario y contraseña para generar un string único
    input_string = "Salt" + str(username) + str(password)
    # Se utiliza el algoritmo SHA-256 para generar el hash del string único
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()

    return sha256_hash.upper()


def get_user_by_username_token(username, token):
    # Cuerpo del JSON para obtener el usuario
    data = {'username': username, 'token': token}
    response = requests.post(url_mongo + "/login", data=json.dumps(data), headers=headers)
    return response.text


def get_user_by_token(token):
    headers_token = {"Authorization": token}
    response = requests.post(url_mongo + "/validate", headers=headers_token)
    return response.text


def log_mongo(username, token, descr):
    # Cuerpo del JSON para obtener el usuario
    if username is not None:
        data = {'username': username, 'token': token, 'descr': descr}
    else:
        data = {'token': token, 'descr': descr}
    mongodata = {'data': data, 'token': token}
    response = requests.post(url_logger + "/log", data=json.dumps(mongodata), headers=headers)
    return response.text


@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        token = generar_token(username, password)

        user = get_user_by_username_token(username, token)
        if user is not None:
            log_mongo(username=username, token=token, descr="successfully logged")
            if "_id" in user:
                del user["_id"]  # No quiero mostrar el ID de la base de datos
            # return json.dumps(products)
            response = Response(response=user, status=200, mimetype="application/json")
            return response
        else:
            return Response(response="user not found", status=404, mimetype="application/json")
    except Exception as e:
        return json.dumps({'error': str(e)})


# headers = {'Content-Type': 'application/json', 'Authentication': token}
@app.route("/validate", methods=['POST'])
def validate():
    try:
        token = request.headers.get('Authorization')

        user = get_user_by_token(token)
        if user is not None:
            log_mongo(username=user, token=token, descr="successfully validated")
            response = Response(response=user, status=200, mimetype="application/json")
            return response
        else:
            return Response(response="invalid access", status=404, mimetype="application/json")

    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/ping", methods=['GET'])
def ping():
    return Response(response=json_util.dumps("successfully"), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
