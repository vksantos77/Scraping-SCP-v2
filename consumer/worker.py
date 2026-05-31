import json
import requests
import sys
sys.path.append("../shared")
from rabbitmq import connection_queue, FILA

API = 'http://localhost:8000/scp'

def processar_mensagem(ch, method, properties, body):
    dados = json.loads(body)
    print(f"[CONSUMER] Mensagem recebida: {dados}")
    
    response = requests.post(API, json=dados)

    if response.status_code == 200:
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)   
    
def main():
    channel = connection_queue()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=FILA,
        on_message_callback=processar_mensagem,
    )
    print(f"[CONSUMER] Aguardando mensagens na fila '{FILA}'...\n")
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CONSUMER] Encerrando...")