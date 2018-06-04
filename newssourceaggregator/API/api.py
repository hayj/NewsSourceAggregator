# This API should be able to :
# - Connect to any mongoDB collection
# - Register researcher teams => OAuth2
# - Allow researchers to pull truckloads of data from the news_db
# - What to watch for ?
#   - Credentials
#   - Deny of Service (request timer for each puller ID ? » Credentials)
#   -

import json
from flask import Flask, request
from sqlalchemy import create_engine
from flask_restful import Resource, Api
from databasetools.mongo import MongoCollection

__version__ = '0.0.1'


host='localhost'
collection = MongoCollection("news_db", "news", indexOn=['url'],
                                        host=host, user=None, password=None, version=__version__)


class Show(Resource):
    def get(self, limit):
        for i, entry in collection:
            print(entry['url'])
            if i >= limit:
                break


class ShowUrl(Resource):
    def get(self, url):
        if url in collection:
            print("FOUND IT !")


app = Flask(__name__)
api = Api(app)
api.add_resource(Show, '/show<maxurls>')  # Route_1
api.add_resource(ShowUrl, '/show_url<url>')  # Route_1

# api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3 Model

if __name__ == '__main__':
    app.run(port=4242)
