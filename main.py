from sklearn.datasets import make_classification
import pandas as pd
import numpy as np

X, y = make_classification(
    n_samples=1000,
    n_features=5,
    n_informative=3,
    n_redundant=1,
    class_sep=0.5,
    weights=[0.7, 0.3],
    random_state=42
)

df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
df["target"] = y

print(df.head())
print(f"\nDistribuição do target:\n{df['target'].value_counts()}")

def gerar_dataset_restaurante(n_samples: int = 1000, seed: int = 42, dias_corte_churn: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Churn: 1 = Cliente parou de pedir (Inativo), 0 = Cliente Ativo
    churn = rng.integers(0, 2, size=n_samples)

    # 1. RECÊNCIA: Dias desde o último pedido/reserva
    dias_desde_ultimo_pedido = np.where(
        churn, 
        rng.integers(dias_corte_churn, dias_corte_churn + 180, n_samples),
        rng.integers(1, dias_corte_churn - 1, n_samples)
    )

    # 2. FREQUÊNCIA: Quantidade de pedidos/reservas no último semestre ativo
    pedidos_ultimo_semestre = np.where(
        churn, 
        rng.integers(1, 4, n_samples),
        rng.integers(4, 25, n_samples)
    )

    # 3. ATRITO: Quantidade de reservas canceladas
    reservas_canceladas = np.where(
        churn, 
        rng.integers(1, 5, n_samples),
        rng.integers(0, 2, n_samples)
    )

    # 4. MONETÁRIO: Ticket médio combinando pratos e bebidas
    ticket_medio = rng.uniform(40.0, 350.0, n_samples).round(2)

    # 5. SATISFAÇÃO: Nota média deixada nos pedidos (1.0 a 5.0)
    avaliacao_media = np.where(
        churn, 
        rng.uniform(1.0, 3.8, n_samples).round(1), 
        rng.uniform(3.5, 5.0, n_samples).round(1) 
    )

    return pd.DataFrame({
        "dias_desde_ultimo_pedido": dias_desde_ultimo_pedido,
        "pedidos_ultimo_semestre": pedidos_ultimo_semestre,
        "reservas_canceladas": reservas_canceladas,
        "ticket_medio": ticket_medio,
        "avaliacao_media": avaliacao_media,
        "churn": churn
    })

df_restaurante = gerar_dataset_restaurante()
print(df_restaurante.head())