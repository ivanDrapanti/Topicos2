import json
import requests
from flask import Flask, Response, request
import bson.json_util as json_util
from datetime import datetime

app = Flask(__name__)
url_mongo = "http://host.docker.internal:5001"
headers = {"Content-Type": "application/json"}


def log_mongo(token, data):
    # Cuerpo del JSON para obtener el usuario
    body = {'token': token, 'data': data, 'date': datetime.now().isoformat()}
    response = requests.post(url_mongo + "/log", data=json.dumps(body), headers=headers)
    return response.text


@app.route("/log", methods=['POST'])
def log():
    try:

        request_body = request.get_json()
        token = request_body.get('token')
        data = request_body.get('data')

        log_mongo(token=token, data=data)

        return Response(response=json_util.dumps("successfully logged"), status=200, mimetype="application/json")

    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/ping", methods=['GET'])
def ping():
    return Response(response=json_util.dumps("successfully"), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
