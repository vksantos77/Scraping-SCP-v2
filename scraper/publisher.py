import requests
from extractor import main

API = 'http://localhost:8000/scp'

def enviar_dto_scp():
    SCPExtracted = main()
    response = requests.post(API, json=SCPExtracted)
    print(response.status_code)
    print(response.json())  # aqui vai mostrar exatamente o que o Pydantic rejeitou


if __name__ == "__main__":
    enviar_dto_scp()
