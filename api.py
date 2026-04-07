# All imports together at the top
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from psycopg2 import errors as pg_errors
from database_pg import Database
from auth import hash_password, verify_password, create_access_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI()


def get_db():
    db = Database()
    db.connect()
    return db


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    return payload


class ProductCreate(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    supplier_id: int = None


@app.get("/")
def read_root():
    return {"message": "Inventory API is running"}


@app.post("/auth/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    try:
        existing = db.get_user(form_data.username)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        hashed = hash_password(form_data.password)
        db.create_users_table()
        result = db.create_user(form_data.username, hashed)
        return {"message": result}
    finally:
        db.disconnect()


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    try:
        user = db.get_user(form_data.username)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        if not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        token = create_access_token({"sub": user["username"]})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.disconnect()


@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["sub"]}


@app.get("/products")
def get_all_products(current_user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        return db.get_all_products()
    finally:
        db.disconnect()


@app.get("/products/low-stock")
def get_low_stock(current_user: dict = Depends(get_current_user)):
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
def get_product(product_id: int, current_user: dict = Depends(get_current_user)):
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
def add_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
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
    
    except pg_errors.UniqueViolation:
        raise HTTPException(
        status_code=409,
        detail=f"Product ID {product.id} already exists"
    )
    finally:
        db.disconnect()

