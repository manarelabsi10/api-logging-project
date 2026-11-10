from fastapi import FastAPI, HTTPException, Path, Request
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


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


# تخزين مؤقت للعناصر أثناء تشغيل التطبيق
items: dict[int, ItemCreate] = {}
next_item_id = 1


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


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    global next_item_id

    item_id = next_item_id
    items[item_id] = item
    next_item_id += 1

    logger.info("Item created: %s (id=%d)", item.name, item_id)

    return {
        "message": "Item created successfully",
        "id": item_id,
        "item": item,
    }


@app.put("/items/{item_id}")
def update_item(
    item: ItemCreate,
    item_id: int = Path(gt=0),
):
    if item_id not in items:
        logger.warning("Update failed: item not found (id=%d)", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    items[item_id] = item
    logger.info("Item updated: %s (id=%d)", item.name, item_id)

    return {
        "message": "Item updated successfully",
        "id": item_id,
        "item": item,
    }


@app.delete("/items/{item_id}")
def delete_item(item_id: int = Path(gt=0)):
    if item_id not in items:
        logger.warning("Delete failed: item not found (id=%d)", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = items.pop(item_id)
    logger.info("Item deleted: %s (id=%d)", deleted_item.name, item_id)

    return {
        "message": "Item deleted successfully",
        "id": item_id,
    }