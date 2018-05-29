import pika


cr = pika.PlainCredentials(username='Ajod', password='hello')

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=cr))
channel = conn.channel()

channel.queue_declare(queue='news_data_queue', durable=True)


class NewsReceiver:
    def __init__(self, host='localhost', queue_name='news_data_queue'):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, credentials=cr))
        self.channel = self.connection.channel()
        self.host = host
        self.queue = self.channel.queue_declare(queue_name, durable=True)
        self.routing_key = queue_name

    def startListening(self, callback):
        if not callable(callback):
            raise AttributeError("callback object must be a callable function")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(callback, queue=self.routing_key, no_ack=False)
        self.channel.start_consuming()