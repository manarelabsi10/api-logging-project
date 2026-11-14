from decimal import Decimal

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .database import get_connection
from .logging_config import configure_logging


logger = configure_logging()

app = FastAPI(
    title="API Logging Project",
    description="A learning API for input validation and application logging.",
    version="0.1.0",
)


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)


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


@app.get("/items")
def list_items():
    with get_connection() as conn:
        items = conn.execute(
            "SELECT id, name, price, quantity FROM items ORDER BY id"
        ).fetchall()

    return {"items": items}


@app.post("/items", status_code=201)
def create_item(item: ItemCreate):
    with get_connection() as conn:
        saved_item = conn.execute(
            """
            INSERT INTO items (name, price, quantity)
            VALUES (%s, %s, %s)
            RETURNING id, name, price, quantity
            """,
            (item.name, item.price, item.quantity),
        ).fetchone()

    logger.info("Item created: %s (id=%d)", item.name, saved_item["id"])

    return {
        "message": "Item created successfully",
        "id": saved_item["id"],
        "item": saved_item,
    }


@app.put("/items/{item_id}")
def update_item(
    item: ItemCreate,
    item_id: int = Path(gt=0),
):
    with get_connection() as conn:
        updated_item = conn.execute(
            """
            UPDATE items
            SET name = %s, price = %s, quantity = %s
            WHERE id = %s
            RETURNING id, name, price, quantity
            """,
            (item.name, item.price, item.quantity, item_id),
        ).fetchone()

    if updated_item is None:
        logger.warning("Update failed: item not found (id=%d)", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    logger.info("Item updated: %s (id=%d)", item.name, item_id)

    return {
        "message": "Item updated successfully",
        "id": item_id,
        "item": updated_item,
    }


@app.delete("/items/{item_id}")
def delete_item(item_id: int = Path(gt=0)):
    with get_connection() as conn:
        deleted_item = conn.execute(
            """
            DELETE FROM items
            WHERE id = %s
            RETURNING id, name, price, quantity
            """,
            (item_id,),
        ).fetchone()

    if deleted_item is None:
        logger.warning("Delete failed: item not found (id=%d)", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    logger.info("Item deleted: %s (id=%d)", deleted_item["name"], item_id)

    return {
        "message": "Item deleted successfully",
        "id": item_id,
    }