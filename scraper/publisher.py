import json
import pika
import sys
sys.path.append("../shared")
from rabbitmq import connection_queue, FILA
from extractor import raspar_todos

def publicar_scps(limite: int = None):
    """
    Raspa os SCPs e publica cada um como mensagem na fila RabbitMQ.
    Use o parâmetro limite para testar com poucos SCPs primeiro.
    Ex: publicar_scps(limite=5)
    """
    channel = connection_queue()

    dtos = raspar_todos(limite=limite)

    if not dtos:
        print("[PUBLISHER] Nenhum SCP encontrado para publicar")
        return

    for dto in dtos:
        channel.basic_publish(
            exchange='',
            routing_key=FILA,
            body=json.dumps(dto, ensure_ascii=False),
            properties=pika.BasicProperties(delivery_mode=2)  # mensagem persistente
        )
        print(f"[PUBLISHER] Publicado na fila: {dto['itemNumber']}")

    print(f"[PUBLISHER] Concluído — {len(dtos)} mensagens publicadas na fila")


if __name__ == "__main__":
    publicar_scps(limite=15)