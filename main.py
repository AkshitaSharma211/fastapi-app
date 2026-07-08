from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello"}

@app.get("/students/{student_id}")
def get_student(student_id: int):
    return {"student_id": student_id}

@app.get("/students")
def list_students(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/students/{student_id}/grades")
def get_student_grades(student_id: int, subject: str = "all"):
    return {"student_id": student_id, "subject": subject}