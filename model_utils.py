import os
import logging
from pathlib import Path
import joblib
from huggingface_hub import hf_hub_download, login

logger = logging.getLogger(__name__)

REPO_ID = "jujumiranda/mlops-churn-prediction"
FILENAME = "model.pkl"


def load_model(
    repo_id: str = REPO_ID,
    filename: str = FILENAME,
    force_download: bool = False,
):
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN não configurado. Defina a variável de ambiente HF_TOKEN "
            f"para baixar o modelo {repo_id}/{filename}."
        )

    cache_dir = Path(os.environ.get("HF_HOME", "/home/app/.cache/huggingface"))
    cache_dir.mkdir(parents=True, exist_ok=True)

    os.environ["HF_HUB_CACHE"] = str(cache_dir)
    os.environ["HUGGINGFACE_HUB_CACHE"] = str(cache_dir)

    login(token=token)

    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        force_download=force_download,
        token=token,
        cache_dir=str(cache_dir),
    )
    return joblib.load(local_path)
