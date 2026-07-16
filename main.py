from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, StudentDB
from auth import hash_password, verify_password

class Student(BaseModel):
    name: str
    age: int
    password: str

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        from_attributes = True

app = FastAPI()

students_db = []


@app.post("/login")
def login(name: str, password: str, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.name == name).first()
    if not student:
        return {"error": "User not found"}
    if not verify_password(password, student.hashed_password):
        return {"error": "Incorrect password"}
    return {"message": "Login successful"}


@app.get("/students/all",response_model=list[StudentResponse])
def list_all_students(db: Session = Depends(get_db)):
    return db.query(StudentDB).all()


@app.get("/students/{student_id}/grades", response_model=StudentResponse)
def get_student_grades(student_id: int, subject: str = "all", db: Session = Depends(get_db)):
    return db.query(StudentDB).filter(StudentDB.id == student_id).first()

@app.post("/students", response_model=StudentResponse)
def create_student(student: Student, db: Session = Depends(get_db)):
    hashed_pw = hash_password(student.password)
    new_student = StudentDB(name=student.name, age=student.age, hashed_password=hashed_pw)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student
    


@app.put("/students/{student_id}")
def update_student(student_id: int, student: Student, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student:
        db_student.name = student.name
        db_student.age = student.age
        db.commit()
        db.refresh(db_student)
        return db_student
    return {"error": "Student not found"}

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if db_student:
        db.delete(db_student)
        db.commit()
        return {"deleted": db_student}
    return {"error": "Student not found"}
