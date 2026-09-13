import pika
import sys

sys.stdout.reconfigure(encoding="utf-8")

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