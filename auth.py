# # datetime gives us the current time
# # timedelta represents a duration of time like "30 minutes"
# # We need both to calculate when a token should expire
# from datetime import datetime, timedelta

# # JWTError is the exception thrown when a token is invalid or expired
# # jwt is the tool that creates and reads JWT tokens
# from jose import JWTError, jwt

# # CryptContext is the hashing tool — we configure it to use bcrypt
# from passlib.context import CryptContext

# # os lets us read environment variables — used to get the SECRET_KEY
# import os


# # Read the SECRET_KEY from environment variables
# # This is the private key your server uses to sign tokens
# # Only your server knows this — if someone else knows it they can create fake tokens
# # The second argument is the default value if the environment variable is not set
# # In production you must change this to a long random string and never share it
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# # The algorithm used to sign the JWT
# # HS256 means HMAC with SHA-256 — the industry standard for this use case
# ALGORITHM = "HS256"

# # How long a token stays valid after it is created
# # After 30 minutes the token expires and the user must login again
# # This limits damage if a token is stolen — the attacker only has 30 minutes
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Create the hashing tool configured to use bcrypt
# # bcrypt is a one-way hashing algorithm — you can hash a password
# # but you can never reverse a hash back to the original password
# # deprecated="auto" means passlib automatically handles older hash formats
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def hash_password(password: str) -> str:
#     # Takes a plain text password like "mypassword123"
#     # Returns a bcrypt hash like "$2b$12$xxx..."
#     # The hash is what gets stored in the database
#     # The original password is thrown away after this — never stored anywhere
#     return pwd_context.hash(password)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     # Takes two things:
#     # plain_password — what the user typed when logging in
#     # hashed_password — what is stored in your database
#     # bcrypt rehashes the plain password and compares it to the stored hash
#     # Returns True if they match, False if they don't
#     # This is how login works — you never decrypt the hash, you just compare
#     return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict) -> str:
#     # data is a dictionary containing what you want to store inside the token
#     # For example: {"sub": "richee"} where "sub" means subject — who owns this token

#     # Make a copy so you don't modify the original dictionary that was passed in
#     to_encode = data.copy()

#     # Calculate the exact time the token should expire
#     # datetime.utcnow() gets the current time in UTC
#     # timedelta(minutes=30) adds 30 minutes to that time
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

#     # Add the expiry time into the token data
#     # "exp" is the standard JWT field name for expiry — jwt.decode checks this automatically
#     to_encode.update({"exp": expire})

#     # Create and sign the JWT string using your secret key and algorithm
#     # The result looks like: eyJhbGc...
#     # Anyone can read the payload but only your server can create a valid signature
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def verify_token(token: str) -> dict:
#     # Takes a JWT string sent by the client
#     # Returns the payload dictionary if valid, returns None if invalid

#     try:
#         # jwt.decode does three things automatically:
#         # 1. Checks the signature — confirms the token was created by your server
#         # 2. Checks the expiry — rejects tokens older than 30 minutes
#         # 3. Extracts and returns the payload — the data stored inside the token
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

#         # Token is valid — return the payload
#         # The payload contains {"sub": "richee", "exp": 1234567890}
#         return payload

#     except JWTError:
#         # Token is invalid for any reason:
#         # - Wrong signature (token was tampered with)
#         # - Expired (older than 30 minutes)
#         # - Malformed (not a valid JWT format)
#         # Return None — the caller will use this to send a 401 response
#         return None
    




from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None