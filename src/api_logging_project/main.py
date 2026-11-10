from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .logging_config import configure_logging



logger = configure_logging()

app = FastAPI(
    title="API Logging Project",
    description="A learning API for input validation and application logging.",
    version="0.1.0",
)

@app.exception_handler(RequestValidationError)
async def log_validation_error(request: Request, exc: RequestValidationError):
    logger.warning(
        "Request validation failed: %s %s (%d field error(s))",
        request.method,
        request.url.path,
        len(exc.errors()),
    )

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    logger.info("Item created: %s", item.name)
    return {
        "message": "Item created successfully",
        "item": item,
    }