from sqlite3 import IntegrityError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database_v2 import Database

app = FastAPI()


def get_db():
    db = Database()
    db.connect()
    return db


class ProductCreate(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    supplier_id: int = None


@app.get("/")
def read_root():
    return {"message": "Inventory API is running"}


@app.get("/products")
def get_all_products():
    db = get_db()
    try:
        return db.get_all_products()
    finally:
        db.disconnect()


@app.get("/products/low-stock")
def get_low_stock():
    db = get_db()
    try:
        rows = db.get_low_stock()
        return [
            {"id": r[0], "name": r[1], "price": r[2],
             "quantity": r[3], "supplier_id": r[4]}
            for r in rows
        ]
    finally:
        db.disconnect()


@app.get("/products/{product_id}")
def get_product(product_id: int):
    db = get_db()
    try:
        product = db.find_product(product_id)
        if product is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )
        return product
    finally:
        db.disconnect()


@app.post("/products")
def add_product(product: ProductCreate):
    db = get_db()
    try:
        result = db.add_product(
            product.id,
            product.name,
            product.price,
            product.quantity,
            product.supplier_id
        )
        db.conn.commit()
        return {"message": result}
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"Product ID {product.id} already exists"
        )
    finally:
        db.disconnect()