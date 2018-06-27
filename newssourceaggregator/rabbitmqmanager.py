from pyrabbit.api import Client


# This should allow for an easy and controllable interface to add/delete queues and register teams to rabbit MQ
# Also, maybe we should generate passwords. Or unique ID. Or whatever.
# todo: Make it all API-able ==> Fixed using PyRabbit

__version__ = "0.0.1"
__verbose__ = False


class RabbitMQManager:
    def __init__(self):
        pass

    # This should create both receiving and sending queues when a team registers
    def createQueue(self):
        name = "testqueue"
        host = 'localhost:15672'
        c = Client(host=host, user='guest', passwd='guest')
        c.create_vhost('example_vhost')
        print(c.get_vhost_names())
        c.set_vhost_permissions('example_vhost', 'guest', '.*', '.*', '.*')
        #c.create_queue('example_vhost', name, durable=True)

    def deleteQueue(self, user, passwd):
        pass
    # This should register a team and their algorithm to the rabbitMQ local server and provide a unique ID
    # Note : the algorithmName is only for queue-naming purposes and may disappear

    def registerTeam(self, user, passwd):
        pass


if __name__ == '__main__':
    rm = RabbitMQManager()
    rm.createQueue()


# import requests
# import json
#
#
#
#
# def get_queue_name(json_list):
#     res = []
#     for json in json_list:
#         res.append(json["name"])
#     return res
#
#
# if __name__ == '__main__':
#     host = 'localhost'
#     port = 15672
#     user = 'guest'
#     passwd = 'guest'
#     res = call_rabbitmq_api(host, port, user, passwd)
#     print("--- dump json ---")
#     print(json.dumps(res.json(), indent=4))
#     print("--- get queue name ---")
#     q_name = get_queue_name(res.json())
#     print(q_name)
