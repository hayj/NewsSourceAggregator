import sys, os
sys.path.append("/".join(os.path.abspath(__file__).split("/")[0:-2]))

import string
import random
import pymongo
from datetime import timedelta
from bson.json_util import dumps
from flask import Flask, request
from bson.objectid import ObjectId
from datetime import datetime as dt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_restful import Resource, Api
from passlib.context import CryptContext
from sqlalchemy_declarative import Base, User
from databasetools.mongo import MongoCollection

__version__ = '0.0.4' # Includes timestamp range request
MAX_PACKAGE_SIZE = 1000

# We define a default time range to pull news from at 24h from current UTC time
DEFAULT_DATE_FORMAT = "%Y-%m-%d_%H:%M"
DEFAULT_TIME_RANGE = timedelta(days=1)
DEFAULT_TIME_OLDEST = dt.strftime(dt.utcnow() - DEFAULT_TIME_RANGE, DEFAULT_DATE_FORMAT)
DEFAULT_TIME_RECENT = dt.utcnow().strftime(DEFAULT_DATE_FORMAT)


def generateToken():
    """
        Generates the authentication token to be return to a user for easy connection.
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))


# Start of the Authentication part of the API

class AuthenticationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PasswordHasher:
    def __init__(self):
        self.password_hash = None
        self.myctx = CryptContext(schemes=["sha256_crypt"])

    def hash_password(self, password):
        self.password_hash = self.myctx.hash(password)
        return self.password_hash

    def verify_password(self, password, user):
        """
            :param:
                password: the user's unencrypted password
                user: an instance of a "Base" class from the database. Returned from session.query

            :return:
                True/False by comparing password with ciphered password from the database
        """
        return self.myctx.verify(password, user.password)


class Auth(Resource):
#    def get(self, email, password):
#        """
#        Endpoint for basic authentication of an already registered user
#        :param email: The user's email address
#        :param password: The user's unciphered password
#        :return: User token from database, which can be subsequently sent to auth/token for next authentications
#        """
#        if not email:
#            return "ERROR: User not found", 404
#        usr = session.query(User).filter(User.email == email).first()
#        if not usr or psswdhash.verify_password(password, usr) is False:
#            return "ERROR: Incorrect password", 403
#
#        return session.query(User).filter(User.email == email).first().token, 201

    def get(self, email, sn, id):
        # Check if everything is present and viable before checking if it matches the Database
        if not email:
            return {"error_type": "AuthenticationError(ERROR: User not found)", "status_code": 400}
        if not sn:
            return {"error_type": "AuthenticationError(ERROR: No auth method defined)", "status_code": 400}
        if not id:
            return {"error_type": "AuthenticationError(ERROR: No password/id given)", "status_code": 400}
        usr = session.query(User).filter(User.email == email).first()
        if usr is None:
            return {"error_type": "AuthenticationError(ERROR: User not found)",
                    "status_code": 400}

        # Checks with the database according to authentication method
        if sn == "email":
            if psswdhash.verify_password(id, usr) is False:
                return {"error_type": "AuthenticationError(ERROR: Incorrect Password)",
                        "status_code": 400}
        elif sn == "fb":
            if usr.fb_id is None or usr.fb_id != id:
                return {"error_type": "AuthenticationError(ERROR: Incorrect Facebook id)",
                        "status_code": 400}
            elif usr.fb is False:
                return {"error_type": "AuthenticationError(Error: User did not subscribe using Facebook)",
                        "status_code": 400}
        elif sn == "google":
            pass
        return usr.token

    def put(self, email, sn, id):
        if not email:
            return {"error_type": "AuthenticationError(ERROR: User not found)", "status_code": 404}
        if not sn:
            return {"error_type": "AuthenticationError(ERROR: No auth method defined)", "status_code": 404}
        if not id:
            return {"error_type": "AuthenticationError(ERROR: No password/id given)", "status_code": 404}

        print("Got args : email = " + email + " sn = " + sn + " id = " + id)
        if session.query(User).filter(User.email == email).first() is not None:
            return {"error_type": "AuthenticationError(ERROR: Email already in use)",
                    "status_code": 400}

        if sn == "email":
            new_user = User(email=email, password=psswdhash.hash_password(id), token=generateToken())
            session.add(new_user)
            session.commit()

        elif sn == "fb":
            new_user = User(email=email, password=None, token=generateToken(), fb=True, fb_id=id)
            session.add(new_user)
            session.commit()
        elif sn == "google":
            pass
        else:
            return {"error_type": "AuthenticationError(ERROR: Invalid query)",
                    "status_code": 400}
        return {"user_token": session.query(User).filter(User.email == email).first().token,
                "status_code": 200}

    class Test(Resource):
        """
            Basic ping test
        """
        def get(self):
            return "OK", 203

    class Register(Resource):
        def put(self, email, password):
            """
            Endpoint for registering a new user
            :param email: The user's email address
            :param password: The user's unciphered password
            :return: User token from database, which can be subsequently sent to auth/token for next authentications
            """
            if email and password:
                if session.query(User).filter(User.email == email).first() is not None:
                    return {"error_type": "AuthenticationError(ERROR: Email already in use)",
                            "status_code": 400}
                new_user = User(email=email, password=psswdhash.hash_password(password), token=generateToken())
                session.add(new_user)
                session.commit()
                return session.query(User).filter(User.email == email).first().token, 200

        def get(self, email, password):
            return self.put(email, password)

# END Authentication API
# Start of news data API

def updateTime():
    global DEFAULT_TIME_OLDEST
    DEFAULT_TIME_OLDEST = dt.strftime(dt.utcnow() - DEFAULT_TIME_RANGE, DEFAULT_DATE_FORMAT)
    global DEFAULT_TIME_RECENT
    DEFAULT_TIME_RECENT = dt.utcnow().strftime(DEFAULT_DATE_FORMAT)


class News(Resource):
    class ID(Resource):
        def get(self, id):
            if collection.find({"_id": ObjectId(id)}):
                return dumps(collection.find({"_id": ObjectId(id)}))
            else:
                return None

    class RangeTimestamp(Resource):
        def get(self, recent, oldest):
            updateTime()
            try:
                dt.strptime(recent, DEFAULT_DATE_FORMAT)
            except ValueError:
                recent = DEFAULT_TIME_RECENT
            try:
                dt.strptime(oldest, DEFAULT_DATE_FORMAT)
            except ValueError:
                oldest = DEFAULT_TIME_OLDEST

            package = []
            limit = 0
            for item in collection.find().sort('timestamp', pymongo.DESCENDING):
                itemtimestamp = dt.strftime(dt.utcfromtimestamp(item['timestamp']),
                                            DEFAULT_DATE_FORMAT)

                # Dirty but necessary
                if dt.strptime(itemtimestamp, DEFAULT_DATE_FORMAT) <= dt.strptime(recent, DEFAULT_DATE_FORMAT)\
                        and dt.strptime(itemtimestamp, DEFAULT_DATE_FORMAT) > dt.strptime(oldest, DEFAULT_DATE_FORMAT):
                    package.append(item)
                    limit += 1
                    if limit >= MAX_PACKAGE_SIZE:
                        break
            return dumps({'data': package})

    class URL(Resource):
        def get(self, url):
            data = collection.find({'url': url})
            if data:
                return dumps(data)

        class Bulk(Resource):
            def get(self, amount):
                if amount is not None:
                    amount = int(amount)
                if amount > MAX_PACKAGE_SIZE:
                    amount = MAX_PACKAGE_SIZE
                package = []
                i = 0
                current = random.randint(0, MAX_PACKAGE_SIZE - amount)
                idx = 0
                for news in collection.find():
                    if i == current:
                        package.append(news['source']['link'])
                        current += 1
                        idx += 1
                        if idx == amount:
                            break
                    i += 1
                return {'data': package}

    class LastUrl(Resource):
        def get(self, lasturl):
            data = collection.find(lasturl)
            if data:
                return dumps(data)


class AppUser(Resource):
    def get(self, user_id):
        pass

    class Events(Resource):
        def post(self, user_id, data):
            eventcollection.insert({'user_id':user_id, 'event_data':data})
            pass

# eventcollection.insert {user_id:1, data: {axaxaxa}}

if __name__ == '__main__':
    # We create a context for SSL certification
    engine = create_engine('sqlite:///sqlalchemy_example_auth.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    psswdhash = PasswordHasher()

    host = '129.175.25.243'
    collection = MongoCollection("news_db", "news", indexOn=['url'],
                                 host='localhost', user="Ajod", password="8kp^U_R3", version=__version__)
    eventcollection = MongoCollection("news_db", "events", indexOn=['user_id'],
                                      host='localhost', user='Ajod', password="8kp^U_R3", version=__version__)

    # We define an entry point for the API
    app = Flask(__name__)
    api = Api(app)
    # /user/events/token/data
    api.add_resource(News.ID, '/news/id/<id>')
    api.add_resource(News.URL, '/news/url/<path:url>')
    api.add_resource(News.LastUrl, '/news/lasturl/<path:lasturl>')
    api.add_resource(News.RangeTimestamp, '/news/range_timestamp/<recent>/<oldest>')
    api.add_resource(News.URL.Bulk, '/news/url/bulk/<amount>')

    #api.add_resource(Auth, '/auth/<string:email>/<string:password>')
    api.add_resource(Auth, "/auth/<string:email>/<string:sn>/<string:id>")
    api.add_resource(Auth.Register, '/auth/register/<string:email>/<string:password>')
    api.add_resource(Auth.Test, '/auth/test')

    api.add_resource(AppUser.Events, '/user/events/<int:user_id>/<data>')
    #api.add_resource(User.Events, '/user/<string:token>/events/<data>')
    app.run(port=4243, debug=False, host=host)
