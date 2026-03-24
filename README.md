---
language: pt
tags:
  - sklearn
  - classification
  - customer-churn
  - restaurant-analytics
  - mlops
---

# Churn Predictor - Santo Garfo v1

Modelo de classificação binária desenvolvido para prever a probabilidade de **churn** (evasão) de clientes do restaurante Santo Garfo, em São Paulo. 

Este projeto faz parte do curso de MLOps (Semana 3) e foca na integração entre treinamento de modelos, serialização e serviço via API FastAPI.

## Uso Rápido

Para carregar o modelo e realizar uma predição em Python:

```python
from huggingface_hub import hf_hub_download
import joblib
import numpy as np

# Download do artefato
repo_id = "seu-usuario/churn-santo-garfo"
model_path = hf_hub_download(repo_id=repo_id, filename="modelo_churn_restaurante.pkl")
model = joblib.load(model_path)

# Feature: [recencia, pedidos, cancelamentos, ticket, nota]
data = np.array([[120, 1, 4, 85.50, 2.1]])
prediction = model.predict(data)
print(f"Resultado: {'Churn' if prediction[0] == 1 else 'Ativo'}")
```

## Features de entrada
| Feature                 | Tipo  | Descrição                                                   |
|-------------------------|-------|-------------------------------------------------------------|
| dias_desde_ultimo_pedido| int   | Recência: Dias desde a última visita (Churn > 90 dias).     |
| pedidos_ultimo_semestre | int   | Frequência: Total de pedidos realizados nos últimos 6 meses.|
| reservas_canceladas     | int   | Atrito: Quantidade de reservas não comparecidas/canceladas. |
| ticket_medio            | float | Monetário: Valor médio gasto por pedido (R$).               |
| avaliacao_media         | float | Satisfação: Nota média dada pelo cliente (1.0 a 5.0).       |


## Métricas (test set: 20%)
O modelo apresentou performance excelente no conjunto de teste:
- **Precision (Churn):** 1.00
- **Recall (Churn):** 1.00
- **F1-Score (Churn):** 1.00
- **Amostras de Teste:** 400
- **Nota Técnica:** O score perfeito (1.0) reflete a separabilidade clara das classes no dataset sintético gerado. Em dados reais, ruídos de mercado e comportamentos atípicos tenderiam a normalizar essas métricas.

## Dependências

- scikit-learn >= 1.0
- joblib
- huggingface_hub
- numpy

## Limitações e Ética
- **Dados Sintéticos:** Este modelo não deve ser utilizado em um ambiente de produção real sem retreinamento com dados históricos reais do estabelecimento.
- **Viés de Regra:** O modelo aprendeu regras rígidas de corte (ex: 90 dias). Comportamentos sazonais (ex: clientes que só vêm no Natal) podem ser classificados erroneamente como churn.
