import pika
import json

def callback(ch, method, properties, body):
    data = json.loads(body)
    print " [x] Received: %s" % str(data)


credentials = pika.PlainCredentials('alma', 'guest')
host = 'ariadne.osf.alma.cl'
port = 5672
parameters = pika.ConnectionParameters(host, port, '/', credentials)
connection = pika.BlockingConnection(parameters)


channel = connection.channel()
channel.queue_declare(queue='alarm')

# ## Only one log
# method_frame, header_frame, body = channel.basic_get(queue='alarm')
#
# print(' [*] Waiting for messages. To exit press CTRL+C')
# while method_frame == None:
#     method_frame, header_frame, body = channel.basic_get(queue='alarm')
#
# if method_frame.NAME == 'Basic.GetEmpty':
#     connection.close()
# else:
#     channel.basic_ack(delivery_tag=method_frame.delivery_tag)
#     connection.close()
#     print json.loads(body)


## Fast consume
channel.basic_consume(callback, no_ack=True, queue='alarm')
channel.start_consuming()