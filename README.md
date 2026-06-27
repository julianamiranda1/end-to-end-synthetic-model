---
language: pt
tags:
  - fastapi
  - mlops
  - restaurant-api
  - churn-prediction
  - testes
---

# Santo Garfo API + Churn Predictor

Projeto completo de aplicação que une uma API de restaurante com um serviço de inferência de machine learning. Desenvolvido com base nos cadernos da disciplina de **MLOps**, o repositório mostra como estruturar uma aplicação realista com:

- API REST para **pratos**, **bebidas**, **pedidos** e **reservas**
- Modelo de churn criado e treinado pelo autor
- Integração com o **Hugging Face Hub** para versionamento do artefato
- Validações de negócio com **Pydantic**
- Tratamento customizado de erros e respostas JSON consistentes
- Testes unitários, de contrato e de integração com **pytest**

## Objetivo

Construir uma aplicação que simule um restaurante e, ao mesmo tempo, permita:

- expor serviços de domínio via API
- consumir um modelo de churn em produção
- garantir contratos de dados e validação de entrada
- manter cobertura de testes e qualidade de código

## Arquitetura do projeto

A solução é organizada em camadas claras:

- `main.py`
  - instância a aplicação FastAPI
  - define `lifespan` para carregar o modelo no startup
  - utiliza handlers customizados para erros 422 e HTTP
  - registra routers por domínio
- `config.py`
  - configurações de ambiente via `pydantic-settings`
  - parâmetros de negócio como número máximo de mesas e pessoas por mesa
- `model_utils.py`
  - baixa e carrega o modelo do Hugging Face Hub
  - permite autenticação via `HF_TOKEN`
- `routers/`
  - organiza rotas em módulos específicos de recurso
- `models/`
  - schemas Pydantic para request e response
  - regras de validação de domínio
- `tests/`
  - casos de teste que asseguram comportamento esperado e contratos

## Estrutura do repositório

```text
.
├── config.py
├── main.py
├── model_utils.py
├── models
│   ├── bebidas.py
│   ├── pedidos.py
│   ├── pratos.py
│   └── reservas.py
├── routers
│   ├── bebidas.py
│   ├── pedidos.py
│   ├── pratos.py
│   ├── predict.py
│   └── reservas.py
├── tests
│   ├── test_bebidas.py
│   ├── test_contratos.py
│   ├── test_main.py
│   ├── test_modelo.py
│   ├── test_pedidos.py
│   ├── test_pratos.py
│   └── test_saude.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Recursos implementados

### API de restaurante

- Cadastro e consulta de **pratos**
- Filtros por categoria, preço e disponibilidade
- Cadastro e consulta de **bebidas**
- Filtros por tipo e teor alcoólico
- Criação de **pedidos** com cálculo de valor total
- Criação e gerenciamento de **reservas** com checagem de conflito por mesa

### Serviço de machine learning

- Endpoint `/ml/predict` para inferência de churn
- Modelo treinado pelo autor e hospedado no Hugging Face Hub
- Inferência com retorno de probabilidade e label amigável
- Health check que confirma se o modelo está carregado

## Endpoints detalhados

### Informações gerais

- `GET /`
  - retorna informações estáticas sobre o restaurante
- `GET /health`
  - retorna estado da aplicação e saúde do modelo

### Machine Learning

- `POST /ml/predict`
  - entrada: dados de cliente
  - saída: `prediction`, `probability`, `label`, `model_version`

### Pratos

- `GET /pratos`
  - lista todos os pratos
  - aceita filtros: `categoria`, `preco_max`, `apenas_disponiveis`
- `GET /pratos/{prato_id}`
  - busca prato por ID
- `POST /pratos`
  - cria um novo prato
- `POST /pratos/{prato_id}/disponibilidade`
  - atualiza disponibilidade do prato

### Bebidas

- `GET /bebidas`
  - lista bebidas
  - aceita filtros: `tipo`, `alcoolica`
- `GET /bebidas/{bebida_id}`
  - busca bebida por ID
- `POST /bebidas`
  - cria bebida nova

### Pedidos

- `POST /pedidos`
  - cria pedido e calcula total
  - valida se o prato existe e está disponível

### Reservas

- `POST /reservas`
  - cria reserva com verificação de conflito por mesa
- `GET /reservas`
  - lista reservas ativas e filtra por data
- `GET /reservas/mesa/{numero}`
  - retorna reservas por número de mesa
- `GET /reservas/{reserva_id}`
  - busca reserva específica
- `DELETE /reservas/{reserva_id}`
  - cancela reserva

## Modelo de churn

O modelo foi criado pelo autor como parte do desenvolvimento do projeto e depois publicado em `jujumiranda/mlops-churn-prediction`.

### Objetivo do modelo

Prever se um cliente do restaurante está em risco de churn (evasão) com base em características de comportamento e satisfação.

### Features utilizadas

- `dias_desde_ultimo_pedido`
- `pedidos_ultimo_semestre`
- `reservas_canceladas`
- `ticket_medio`
- `avaliacao_media`

### Interpretação dos campos

- `dias_desde_ultimo_pedido`: recência em dias desde a última visita
- `pedidos_ultimo_semestre`: frequência de pedidos no último semestre
- `reservas_canceladas`: número de cancelamentos de reserva
- `ticket_medio`: gasto médio por pedido
- `avaliacao_media`: nota média dada pelo cliente

### Exemplo de payload

```json
{
  "dias_desde_ultimo_pedido": 95,
  "pedidos_ultimo_semestre": 2,
  "reservas_canceladas": 2,
  "ticket_medio": 42.0,
  "avaliacao_media": 2.5
}
```

### Exemplo de resposta

```json
{
  "prediction": 1,
  "probability": 0.9245,
  "label": "Inativo/Risco",
  "model_version": "1.0.0"
}
```

### Observações sobre o modelo

- Criado e treinado como parte do projeto
- Publicado no Hugging Face Hub para versionamento e carregamento dinâmico
- Ideal para demonstração; precisa de retreinamento com dados reais para uso em produção
- O endpoint usa `model.predict` e `model.predict_proba`

## Regras de validação de domínio

- `PratoInput`
  - valida nome, categoria, preço e opção de preço promocional
  - garante desconto máximo de 50%
- `BebidaInput`
  - valida nome, tipo, preço, teor alcoólico e volume
- `PedidoInput`
  - valida `quantidade` > 0
  - só aceita pedido se o prato existir e estiver disponível
- `ReservaInput`
  - valida mesa e número de pessoas
  - exige antecedência mínima de 1 hora
  - verifica conflito de reserva por mesa

## Como rodar localmente

### Configuração do ambiente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Executar o servidor

```powershell
uvicorn main:app --reload
```

### Documentação automática

A documentação interativa estará disponível em `http://127.0.0.1:8000/docs`.

### Variáveis de ambiente

- `HF_TOKEN`
  - token de autenticação Hugging Face (opcional)

## Testes

### Executar testes

```powershell
pytest
```

### O que é testado

- existência das rotas principais
- respostas e contratos JSON
- cenários de validação de entradas
- lógica de criação de pedidos e reservas
- integração com o modelo de churn

## Dependências

Dependências principais:

- `fastapi`
- `uvicorn[standard]`
- `pydantic`
- `pydantic-settings`
- `scikit-learn`
- `numpy`
- `joblib`
- `huggingface_hub`

Dependências de desenvolvimento:

- `pytest`
- `httpx`
- `black`
- `autoflake`

## Melhorias futuras

- persistência de dados em banco
- autenticação e autorização
- CI/CD para deploy automático
- monitoramento e métricas
- versionamento completo do modelo e rollback
- suporte a múltiplos ambientes (dev/staging/prod)

## Observações finais

Este repositório demonstra uma aplicação end-to-end que mistura APIs de domínio e inferência de machine learning. A estrutura está pronta para evoluir em direção a um serviço de produção mais completo e escalável.
