import logging
import os
import tempfile
from pathlib import Path

import joblib
from huggingface_hub import hf_hub_download, login

logger = logging.getLogger(__name__)

REPO_ID = "jujumiranda/mlops-churn-prediction"
FILENAME = "model.pkl"


def _resolve_cache_dir() -> Path:
    candidates = []

    for env_name in ("HF_HOME", "HF_HUB_CACHE", "HUGGINGFACE_HUB_CACHE"):
        value = os.environ.get(env_name)
        if value:
            candidates.append(Path(value).expanduser())

    if os.environ.get("XDG_CACHE_HOME"):
        candidates.append(Path(os.environ["XDG_CACHE_HOME"]).expanduser() / "huggingface")

    home_dir = Path(os.environ.get("HOME") or str(Path.home())).expanduser()
    candidates.append(home_dir / ".cache" / "huggingface")
    candidates.append(Path(tempfile.gettempdir()) / "huggingface-cache")

    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except (PermissionError, OSError):
            continue

    raise RuntimeError("Não foi possível criar um diretório de cache do Hugging Face acessível.")


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

    cache_dir = _resolve_cache_dir()

    os.environ["HF_HOME"] = str(cache_dir)
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
