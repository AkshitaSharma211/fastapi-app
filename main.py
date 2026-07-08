from fastapi import FastAPI
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int

app = FastAPI()

students_db = []

@app.get("/")
def read_root():
    return {"message": "hello"}


@app.get("/students/all")
def list_all_students():
    return students_db

@app.get("/students/{student_id}")
def get_student(student_id: int):
    return {"student_id": student_id}

@app.get("/students")
def list_students(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/students/{student_id}/grades")
def get_student_grades(student_id: int, subject: str = "all"):
    return {"student_id": student_id, "subject": subject}

@app.post("/students")
def create_student(student: Student):
    students_db.append(student)
    return student
