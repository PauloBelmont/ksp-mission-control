# KSP Mission Control

Dashboard de observabilidade para o Kerbal Space Program, composto por dois serviços containerizados:

- **API** (`fastapi/`) — conecta ao kRPC do KSP via TCP e expõe telemetria em REST
- **Dashboard** (`streamlit/`) — consome a API e exibe métricas em tempo real no browser

---

## Pré-requisitos

- Kerbal Space Program com o mod **kRPC** instalado e rodando
  - Portas padrão: RPC `5000`, Stream `5001`
  - No menu do kRPC dentro do jogo, marque *"Allow connections from other computers"*
- **Docker Desktop** instalado e rodando no Windows
- **Git** (opcional, para clonar o repositório)

---

## Configuração

Copie o arquivo de variáveis de ambiente:

```bash
cp .env.example .env
```

O `.env` padrão já está configurado para conectar ao KSP rodando no host Windows (`host.docker.internal`). Edite apenas se as portas do kRPC forem diferentes:

```env
KRPC_ADDRESS=host.docker.internal
KRPC_RPC_PORT=5000
KRPC_STREAM_PORT=5001
```

---

## Rodando o projeto

Com o KSP aberto e o kRPC ativo, suba os dois containers:

```bash
docker compose up --build
```

Aguarde o build na primeira execução. Quando os dois serviços estiverem de pé:

| Serviço    | URL                         |
|------------|-----------------------------|
| Dashboard  | http://localhost:8501       |
| API (raw)  | http://localhost:8000/telemetry |
| Health     | http://localhost:8000/health    |

Para parar:

```bash
docker compose down
```

---

## Estrutura do projeto

```
ksp-mission-control/
├── docker-compose.yml
├── .env.example
├── fastapi/
│   ├── Dockerfile
│   ├── main.py          # endpoints FastAPI
│   ├── krpc_client.py   # conexão e leitura via kRPC
│   └── requirements.txt
└── streamlit/
    ├── Dockerfile
    ├── dashboard.py     # interface de telemetria
    └── requirements.txt
```

---

## Resolução de problemas

**API retorna 503**
O kRPC não está acessível. Verifique se o KSP está aberto, se há uma nave ativa e se a opção *"Allow connections from other computers"* está habilitada no mod.

**`host.docker.internal` não resolve**
Certifique-se de que o Docker Desktop está atualizado. Em versões antigas do Docker no Windows, pode ser necessário adicionar `extra_hosts: ["host.docker.internal:host-gateway"]` no serviço `api` do `docker-compose.yml`.

**Dashboard não conecta à API**
O Streamlit depende da API estar respondendo. Aguarde alguns segundos após o `docker compose up` e recarregue o browser.
