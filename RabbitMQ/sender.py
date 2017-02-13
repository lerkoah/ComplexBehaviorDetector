import pika
import json

credentials = pika.PlainCredentials('alma', 'guest')
host = 'ariadne.osf.alma.cl'
port = 5672
parameters = pika.ConnectionParameters(host, port, '/', credentials)
connection = pika.BlockingConnection(parameters)


channel = connection.channel()
channel.queue_declare(queue='alarm')

message = json.dumps({'key 1': 1, 'key 2': '2'})
channel.basic_publish(exchange='',
                      routing_key='alarm',
                      body=message)
print(" [x] Sent: %s" % message)