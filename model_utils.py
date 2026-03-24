import joblib
from huggingface_hub import hf_hub_download

# Configurações do seu Repositório
REPO_ID = "jujumiranda/mlops-churn-prediction"
FILENAME = "model.pkl"

def load_model(force_download: bool = False):
    """Carrega o modelo do Hugging Face Hub com suporte a cache."""
    try:
        local_path = hf_hub_download(
            repo_id=REPO_ID,
            filename=FILENAME,
            force_download=force_download
        )
        model = joblib.load(local_path)
        return model
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        return None