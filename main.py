from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from config import settings
from model_utils import load_model
from routers import predict
from routers import pratos
from routers import bebidas
from routers import pedidos
from routers import reservas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização: Carrega o modelo e armazena no state da app
    app.state.model = load_model()
    yield
    # Finalização: Limpeza se necessário
    app.state.model = None


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.default_response_class = JSONResponse


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Dados de entrada inválidos",
            "status": 422,
            "path": str(request.url),
            "detalhes": [
                {
                    "campo": " -> ".join(str(loc) for loc in e["loc"]),
                    "mensagem": e["msg"],
                }
                for e in exc.errors()
            ],
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": exc.detail,
            "status": exc.status_code,
            "path": str(request.url),
            "detalhes": [],
        },
    )


# Novo Router de Machine Learning
app.include_router(predict.router, prefix="/ml", tags=["ML"])

app.include_router(pratos.router, prefix="/pratos", tags=["Pratos"])

app.include_router(bebidas.router, prefix="/bebidas", tags=["Bebidas"])

app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])

app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])


@app.get("/", tags=["Informações"])
async def root():
    return {
        "restaurante": "Santo Garfo",
        "mensagem": "Bem-vindo à nossa API",
        "chef": "Juliana Miranda",
        "cidade": "São Paulo",
        "especialidade": "Comida brasileira",
    }


@app.get("/health", tags=["Monitoramento"])
async def health(request: Request):
    # Verifica se o objeto do modelo existe no estado da aplicação
    model_instance = getattr(request.app.state, "model", None)

    if model_instance is not None:
        return {
            "status": "healthy",
            "model": "ok",
            "details": "Modelo carregado e pronto para inferência",
        }
    else:
        # Se o modelo for None (erro no download ou carregamento)
        # Retornamos 200 ou 503 baseado na discussão abaixo
        return {
            "status": "unhealthy",
            "model": "degraded",
            "details": "API funcional, mas o artefato do modelo não foi encontrado",
        }
