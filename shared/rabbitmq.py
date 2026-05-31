import pika

RABBIT_HOST = "localhost"
FILA = "SCPs"

def connection_queue():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=FILA, durable=True)
    print("[RABBITMQ] Conexão estabelecida")
    return channel