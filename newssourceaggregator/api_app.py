from flask import Flask
from flask_restful import Resource, Api
from databasetools.mongo import MongoCollection
import string
import random

# What we need :
# - A database for all user data. Scrolling, reading, urls and all.
# - Either another db or the same for user login/passwd to be authentified then a token to be used in each request
# -

__version__ = "0.0.2"
__verbose__ = False


def generateToken():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))


class AuthenticationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Auth(Resource):
    def get(self, email):
        if not email:
            return None
        if email in authDB:
            if authDB[email]['token']:
                return authDB[email]['token']
            print("User was wrongfully initialized")
            return None
        return None


class Register(Resource):
    def put(self, email):
        if email:
            if email in authDB:
                return
            authDB.insert({'email': email, 'token': generateToken()})
            return authDB[email]['token']
        return None


if __name__ == "__main__":
    host = '129.175.25.243'
    authDB = MongoCollection('auth_db', "auth", indexOn=['email'],
                             host='localhost', user="Ajod", password="8kp^U_R3", version='0.0.1')

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Auth, '/auth/<string:email>')
    api.add_resource(Register, '/register/<string:email>')

    app.run(port=4242, debug=False, host=host)
