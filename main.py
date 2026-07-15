from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, StudentDB

class Student(BaseModel):
    name: str
    age: int

app = FastAPI()

students_db = []



@app.get("/students/all")
def list_all_students(db: Session = Depends(get_db)):
    return db.query(StudentDB).all()


@app.get("/students/{student_id}/grades")
def get_student_grades(student_id: int, subject: str = "all", db: Session = Depends(get_db)):
    return db.query(StudentDB).filter(StudentDB.id == student_id).first()

@app.post("/students")
def create_student(student: Student, db: Session = Depends(get_db)):
    new_student = StudentDB(name=student.name, age=student.age)
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
