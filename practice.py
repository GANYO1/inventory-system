from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def greeting():
    return {"message": "Hello from Ghana. "}

@app.get("/square/{number}")
def square_of_a_num(number: int):
    square = number ** 2
    return {"number": number, "square": square}
