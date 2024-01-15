from pymongo import MongoClient
import json
from flask import Flask, Response, request
import bson.json_util as json_util

app = Flask(__name__)


# Utility method to find user by username and token for a client in MongoDB
def find_user_for_client(username, token):
    query = {'user': username, 'token': token}
    return db.users.find_one(query)


# Utility method to find user by username and token for a client in MongoDB
def find_user_for_client_by_token(token):
    query = {'token': token}
    return db.users.find_one(query)


def post_log(data):
    return db.metrics.insert_one(data).inserted_id


@app.route("/login", methods=['POST'])
def get_token():
    # client_id = request.args.get('id')
    # filter = {} if client_id is None else {"_id": client_id}
    try:
        data = request.get_json()
        username = data.get('username')
        token = data.get('token')

        user = find_user_for_client(username, token)
        if user is not None:
            if "_id" in user:
                del user["_id"]  # No quiero mostrar el ID de la base de datos
            # return json.dumps(products)
            response = Response(response=json_util.dumps(user), status=200, mimetype="application/json")
            return response
        else:
            return Response(response="user not found", status=404, mimetype="application/json")
    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/validate", methods=['POST'])
def validate():
    # client_id = request.args.get('id')
    # filter = {} if client_id is None else {"_id": client_id}
    try:
        token = request.headers.get('Authorization')

        user = find_user_for_client_by_token(token)
        if user is not None:
            if "_id" in user:
                del user["_id"]
            if "user" in user:
                del user["user"]
            if "token" in user:
                del user["token"]
            response = Response(response=json_util.dumps(user), status=200, mimetype="application/json")
            return response
        else:
            return Response(response="invalid access", status=404, mimetype="application/json")

    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/log", methods=['POST'])
def login():
    # client_id = request.args.get('id')
    # filter = {} if client_id is None else {"_id": client_id}
    try:
        data = request.get_json()

        login = post_log(data)
        return Response(response=json_util.dumps(login), status=200, mimetype="application/json")

    except Exception as e:
        return json.dumps({'error': str(e)})


@app.route("/ping", methods=['GET'])
def ping():
    return Response(response=json_util.dumps("successfully"), status=200, mimetype="application/json")


if __name__ == "__main__":
    # 2) Create a new client and connect to the cloud MongoDB instance (local)
    client = MongoClient(host="host.docker.internal", port=27017)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db = client['tpfinal']
    app.run(host='0.0.0.0', port=5000, debug=True)
