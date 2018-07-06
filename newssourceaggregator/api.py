import os
import ssl
import random
import pymongo
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask, request
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask_restful import Resource, Api
from databasetools.mongo import MongoCollection

__version__ = '0.0.4' # Includes timestamp range request
MAX_PACKAGE_SIZE = 1000

# We define a default date to pull news from at 24h from current UTC time
DEFAULT_DATE_FORMAT = "%Y-%m-%d_%H:%M"
DEFAULT_TIME_RANGE = timedelta(days=1)
DEFAULT_TIME_OLDEST = dt.strftime(dt.utcnow() - DEFAULT_TIME_RANGE, DEFAULT_DATE_FORMAT)
DEFAULT_TIME_RECENT = dt.utcnow().strftime(DEFAULT_DATE_FORMAT)


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

# TEMP:
#   https://renewal.com/api/
#   /url : /range /range_timestamp || Category ? Containing keyword ?
#   /user : /browsing_data /user_data /social_networks ?
#   /news : /id



if __name__ == '__main__':
    # We create a context for SSL certification
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(os.environ['HOME'] + '/NewsSourceAggregator/newssourceaggregator/certs/host.cert',
                            '$HOME' + '/NewsSourceAggregator/newssourceaggregator/certs/host.key')

    #host = '129.175.25.243'
    host = '0.0.0.0'
    collection = MongoCollection("news_db", "news", indexOn=['url'],
                                 host='localhost', user="Ajod", password="8kp^U_R3", version=__version__)

    # We define an entry point for the API
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(News.ID, '/news/id/<id>')
    api.add_resource(News.URL, '/news/url/<path:url>')
    api.add_resource(News.LastUrl, '/news/lasturl/<path:lasturl>')
    api.add_resource(News.RangeTimestamp, '/news/range_timestamp/<recent>/<oldest>')
    api.add_resource(News.URL.Bulk, '/news/url/bulk/<amount>')

    app.run(port=4243, debug=False, host=host, ssl_context=context)
