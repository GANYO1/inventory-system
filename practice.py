from fastapi import FastAPI, HTTPException # Path
# from typing import Optional
# from pydantic import BaseModel

app = FastAPI()

text_posts = {1: {"title": "New Post", "content": "cool test post"}}

@app.get("/posts")
def get_all_posts():
    return text_posts

# getting a specific value from the dic
@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found" )
    return text_posts.get(id)

''' learning programming
. have a clear specific goal - become a junior py backend develper by the end of the year
. everything i learn should serve this goal
. plan or roadmap - research / blog, articles, videos, summarise
. track my progress daily
. constantly challenging myself daily - let ai generate problems that push me just beyond my confort zone
. learn -> practice -> apply -> review
. continuously learning

'''



































# @app.get("/hello")
# def greeting():
#     return {"message": "Hello from Ghana. "}

# @app.get("/square/{number}")
# def square_of_a_num(number: int):
#     square = number ** 2
#     return {"number": number, "square": square}

# students = {
#     1: {
#         "name": "Vifah",
#         "age": 22,                  # dict
#         "class": "Electrical"
#     }
# }

# class Student(BaseModel):  # request body
#     name: str
#     age: int
#     year: str

# @app.get("/get-student/{student_id}") # {student_id} is a path parameter
# def get_students(student_id: int = Path(None, description="The ID of student you want to view", gt=0, lt=3)): # Adding more descriptions to our APi
#     return students[student_id]

# # gt -- greater than >
# # lt -- less than <
# # ge -- >=
# # le -- <=

# # Query Parameters
# # google.com/results?search=Python // search=Python
# @app.get("/get-by-name")
# def get_students(*, name: Optional[str] = None, age : int): # required
#     for student_id in students:
#         if students[student_id]["name"] == name:
#             return students[student_id]
#     return {"Data": "Not Found"}


# # Combining path and query parameters
# @app.get("/get-by-name/{student_id}")
# def get_students(*, student_id: int, name: Optional[str] = None, age : int): # required
#     for student_id in students:
#         if students[student_id]["name"] == name:
#             return students[student_id]
#     return {"Data": "Not Found"}

# # Request Body and The Post Method
# @app.post("/create-student/{student_id}")
# def create_student(student_id: int, student : Student):
#     if student_id in students:
#         return {"Error": "Student exists"}
    
#     students[student_id] = student
#     return students[student_id]

# # put method
# # @app.put("/update-student/{student_id}")
# # def update_student(student: int, student: Student):

# FastAPI
# # packages in Python
# pip & uv
# uv init .
# uv add fastapi
# installing
# uv add python-dotenv
# uv add fastapi-users[sqlalchemy]
# uv add imagekitio
# uv add uvicorn[standard]
# uv add aisqlite
# .env for secured information
