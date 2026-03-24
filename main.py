from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from model_utils import load_model
from routers import predict

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: Carrega o modelo e armazena no state da app
    app.state.model = load_model()
    yield
    # Finalização: Limpeza se necessário
    app.state.model = None

app = FastAPI(title="Santo Garfo API - MLOps", lifespan=lifespan)

# Novo Router de Machine Learning
app.include_router(predict.router, prefix="/ml", tags=["ML"])

@app.get("/health", tags=["Monitoramento"])
async def health(request: Request):
    # Verifica se o objeto do modelo existe no estado da aplicação
    model_instance = getattr(request.app.state, "model", None)
    
    if model_instance is not None:
        return {
            "status": "healthy",
            "model": "ok",
            "details": "Modelo carregado e pronto para inferência"
        }
    else:
        # Se o modelo for None (erro no download ou carregamento)
        # Retornamos 200 ou 503 baseado na discussão abaixo
        return {
            "status": "unhealthy",
            "model": "degraded",
            "details": "API funcional, mas o artefato do modelo não foi encontrado"
        }