# SCP Scraper — Projeto Didático de Web Scraping com Filas

Projeto educacional que demonstra na prática como integrar **web scraping**, **mensageria com filas** e **APIs REST**, usando como fonte de dados o [SCP Wiki em português](http://scp-pt-br.wikidot.com).

Os dados raspados são publicados em uma fila RabbitMQ, consumidos por um worker e persistidos em um banco MongoDB através de uma API FastAPI.

> ⚠️ Este projeto foi desenvolvido para fins didáticos. O objetivo é aprender as tecnologias envolvidas, não escalar em produção.

---

## Visão geral da arquitetura

```
[SCP Wiki] ──► [Scraper] ──► [RabbitMQ] ──► [Consumer] ──► [API FastAPI] ──► [MongoDB]
```

O projeto é um **monorepo** composto por três módulos independentes que se comunicam entre si:

| Módulo | Responsabilidade |
|---|---|
| `scraper/` | Raspa os dados do SCP Wiki e publica na fila |
| `consumer/` | Lê as mensagens da fila e envia para a API |
| `api/` | Recebe os dados e persiste no MongoDB |

Cada módulo pode ser desenvolvido, testado e executado de forma independente.

---

## Estrutura de pastas

```
scp-scraper/
│
├── scraper/
│   ├── main.py              # Orquestra o scraping (quais páginas raspar)
│   ├── extractor.py         # Lógica de extração do HTML
│   └── publisher.py         # Publica o DTO na fila
│
├── consumer/
│   └── worker.py            # Lê da fila e chama a API
│
├── api/
│   ├── main.py              # Inicializa o FastAPI
│   ├── routes/
│   │   └── scp.py           # Endpoints (POST /scp)
│   ├── models/
│   │   └── scp.py           # DTO com Pydantic
│   └── database/
│       └── connection.py    # Conexão com MongoDB
│
├── docker-compose.yml       # RabbitMQ + MongoDB
├── .env.example             # Exemplo de variáveis de ambiente
└── requirements.txt
```

---

## Pré-requisitos

Antes de qualquer coisa, certifique-se de ter instalado:

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/) e Docker Compose
- [pip](https://pip.pypa.io/en/stable/)

---

## Infraestrutura

O RabbitMQ e o MongoDB rodam via Docker. Para subir os dois:

```bash
docker-compose up -d
```

Após subir, os serviços ficam disponíveis em:

| Serviço | Endereço |
|---|---|
| RabbitMQ (broker) | `localhost:5672` |
| RabbitMQ (painel visual) | `localhost:15672` |
| MongoDB | `localhost:27017` |

Credenciais padrão do RabbitMQ: usuário `admin`, senha `admin` (configuráveis no `.env`).

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin
RABBITMQ_QUEUE=scp_dados

MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=scp_db

API_BASE_URL=http://localhost:8000
```

---

## Módulo 1 — Scraper

Responsável por acessar as páginas do SCP Wiki, extrair os dados e publicar na fila RabbitMQ como um DTO em JSON.

### O que ele extrai

De cada página SCP, o scraper monta o seguinte documento:

```json
{
  "item": "SCP-3516",
  "classe": "Seguro",
  "procedimentos_contencao": "...",
  "descricao": "...",
  "conteudos_adjacentes": [
    {
      "titulo": "Registro de Testes",
      "conteudo": "..."
    }
  ],
  "metadados": {
    "url_origem": "http://scp-pt-br.wikidot.com/scp-3516",
    "data_scraping": "2026-04-21T10:30:00"
  }
}
```

### Bibliotecas utilizadas

- `requests` — busca o HTML da página
- `beautifulsoup4` — extrai os elementos do HTML
- `pika` — publica a mensagem na fila RabbitMQ

### Como instalar

```bash
cd scraper
pip install requests beautifulsoup4 pika
```

### Como rodar

```bash
python main.py
```

---

## Módulo 2 — Consumer (Worker)

Fica escutando a fila RabbitMQ continuamente. A cada mensagem recebida, faz um `POST` para a API com o DTO do SCP. Confirma o processamento (`ack`) apenas se a API retornar sucesso — caso contrário, devolve a mensagem para a fila (`nack`).

### Bibliotecas utilizadas

- `pika` — consome mensagens do RabbitMQ
- `requests` — chama a API

### Como instalar

```bash
cd consumer
pip install pika requests
```

### Como rodar

```bash
python worker.py
```

> O consumer precisa que a API esteja de pé antes de ser iniciado.

---

## Módulo 3 — API

API REST construída com FastAPI. Expõe um endpoint `POST /scp` que recebe o DTO, valida com Pydantic e persiste no MongoDB.

A documentação interativa da API fica disponível automaticamente em `http://localhost:8000/docs` após subir o servidor.

### Bibliotecas utilizadas

- `fastapi` — framework da API
- `uvicorn` — servidor ASGI para rodar o FastAPI
- `pydantic` — validação e modelagem do DTO
- `motor` — driver assíncrono do MongoDB para Python

### Como instalar

```bash
cd api
pip install fastapi uvicorn pydantic motor
```

### Como rodar

```bash
uvicorn main:app --reload
```

---

## Ordem recomendada para desenvolvimento

1. Subir a infraestrutura com `docker-compose up -d`
2. Desenvolver e testar a **API** — use o `/docs` para enviar JSONs na mão
3. Desenvolver o **Scraper** — valide os dados extraídos no terminal antes de publicar na fila
4. Conectar o scraper à **fila** e verificar as mensagens no painel do RabbitMQ
5. Rodar o **Consumer** e ver o fluxo completo funcionando ponta a ponta

---

## Tecnologias utilizadas

| Tecnologia | Papel no projeto |
|---|---|
| Python 3.11+ | Linguagem principal dos três módulos |
| requests + BeautifulSoup | Scraping do HTML |
| RabbitMQ | Fila de mensagens entre scraper e API |
| pika | Cliente Python para RabbitMQ |
| FastAPI | Framework da API REST |
| Pydantic | Validação e modelagem do DTO |
| MongoDB | Banco de dados NoSQL orientado a documentos |
| Motor | Driver assíncrono do MongoDB |
| Docker | Infraestrutura local (RabbitMQ + MongoDB) |

---

## Licença

Projeto desenvolvido para fins educacionais. Livre para uso e modificação.