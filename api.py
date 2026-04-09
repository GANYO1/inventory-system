# All imports together at the top

# FastAPI core — FastAPI creates the app, HTTPException sends error responses,
# Depends runs a function before an endpoint executes
from fastapi import FastAPI, HTTPException, Depends

# OAuth2PasswordBearer extracts the JWT token from incoming request headers
# OAuth2PasswordRequestForm reads username and password from a form submission
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# BaseModel is used to define and validate the shape of request body data
from pydantic import BaseModel

# pg_errors gives us access to PostgreSQL specific errors like duplicate key violations
from psycopg2 import errors as pg_errors

# Our Database class that handles all PostgreSQL operations
from database_pg import Database

# Our authentication functions from auth.py
from auth import hash_password, verify_password, create_access_token, verify_token

# Tells FastAPI where users get their tokens from
# This also adds the Authorize button to the /docs page automatically
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Create the FastAPI application instance
# Everything is registered on this object using decorators
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    # Create a fresh database connection for each request
    # This avoids threading issues — each request gets its own connection
    db = Database()
    db.connect()
    return db


def get_current_user(token: str = Depends(oauth2_scheme)):
    # This function runs before any protected endpoint
    # Depends(oauth2_scheme) extracts the JWT token from the request header automatically

    # Verify the token — checks signature and expiry
    payload = verify_token(token)

    if payload is None:
        # Token is missing, expired, or tampered with
        # Return 401 Unauthorized — the request is blocked here
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # Token is valid — return the payload which contains the username
    return payload


# Defines the expected shape of a product in a POST request body
# FastAPI uses this to validate incoming data automatically
# If any field is wrong type or missing, FastAPI returns 422 before your code runs
class ProductCreate(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    supplier_id: int = None  # Optional — defaults to None if not provided


# --- ROOT ENDPOINT ---

@app.get("/")
def read_root():
    # Simple health check — confirms the API is running
    return {"message": "Inventory API is running"}


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm reads username and password from the request body
    # Depends() tells FastAPI to handle this injection automatically

    db = get_db()
    try:
        # Check if username already exists in the database
        existing = db.get_user(form_data.username)
        if existing:
            # Username is taken — return 400 Bad Request
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

        # Hash the plain text password before storing
        # The original password is never saved anywhere
        hashed = hash_password(form_data.password)

        # Ensure users table exists before inserting
        db.create_users_table()

        # Insert the new user with hashed password into the database
        result = db.create_user(form_data.username, hashed)
        return {"message": result}
    finally:
        # Always disconnect after the request — runs even if an error occurred
        db.disconnect()


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    try:
        # Look up the user by username in the database
        user = db.get_user(form_data.username)

        if not user:
            # Username not found — return 401
            # We say "Invalid username or password" not "Username not found"
            # so attackers don't know which part was wrong
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        if not verify_password(form_data.password, user["hashed_password"]):
            # Password doesn't match the stored hash — return 401
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        # Both checks passed — create a JWT token with the username inside it
        # "sub" is the standard JWT field for the subject — who the token belongs to
        token = create_access_token({"sub": user["username"]})

        # Return the token — client stores this and sends it with future requests
        # "bearer" is the standard token type name
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.disconnect()


@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    # Protected endpoint — Depends(get_current_user) verifies the token first
    # If token is invalid, get_current_user raises 401 and this never runs

    # current_user contains the token payload — {"sub": "richee", "exp": ...}
    # Return the username from inside the token
    return {"username": current_user["sub"]}


# --- PRODUCT ENDPOINTS ---
# All product endpoints are protected
# current_user receives the token payload if valid
# The _ prefix convention means "received but not used inside this function"

@app.get("/products")
def get_all_products(current_user: dict = Depends(get_current_user)):
    # Return all products from the database as a list of dictionaries
    db = get_db()
    try:
        return db.get_all_products()
    finally:
        db.disconnect()


@app.get("/products/low-stock")
def get_low_stock(current_user: dict = Depends(get_current_user)):
    # Return only products where quantity is below the threshold (default 5)
    # This route must be defined BEFORE /products/{product_id}
    # Otherwise FastAPI would try to match "low-stock" as a product ID
    db = get_db()
    try:
        rows = db.get_low_stock()
        # Convert each tuple row into a readable dictionary
        return [
            {"id": r[0], "name": r[1], "price": r[2],
             "quantity": r[3], "supplier_id": r[4]}
            for r in rows
        ]
    finally:
        db.disconnect()


@app.get("/products/{product_id}")
def get_product(product_id: int, current_user: dict = Depends(get_current_user)):
    # {product_id} is a path parameter — FastAPI extracts it from the URL
    # : int tells FastAPI to validate it's an integer before calling this function
    db = get_db()
    try:
        product = db.find_product(product_id)

        if product is None:
            # No product with that ID — return 404 Not Found
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found"
            )

        return product
    finally:
        db.disconnect()


@app.post("/products")
def add_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    # product is validated against ProductCreate before this function runs
    # If id, name, price, or quantity are wrong types, FastAPI returns 422 automatically
    db = get_db()
    try:
        result = db.add_product(
            product.id,
            product.name,
            product.price,
            product.quantity,
            product.supplier_id
        )

        # Commit the insert to make it permanent in the database
        db.conn.commit()
        return {"message": result}

    except pg_errors.UniqueViolation:
        # A product with this ID already exists in the database
        # Return 409 Conflict instead of letting it crash with 500
        raise HTTPException(
            status_code=409,
            detail=f"Product ID {product.id} already exists"
        )
    finally:
        # Always runs — ensures connection is closed even if an error occurred
        db.disconnect()