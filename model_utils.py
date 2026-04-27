import os
import logging
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
    if token:
        login(token=token)

    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        force_download=force_download,
    )
    return joblib.load(local_path)