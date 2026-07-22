from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware


from database import get_db, StudentDB
from auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


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


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name = payload.get("sub")
        if name is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    student = db.query(StudentDB).filter(StudentDB.name == name).first()
    if student is None:
        raise HTTPException(status_code=401, detail="User not found")
    return student


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.name == form_data.username).first()
    if not student:
        return {"error": "User not found"}
    if not verify_password(form_data.password, student.hashed_password):
        return {"error": "Incorrect password"}

    access_token = create_access_token(data={"sub": student.name})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/students/all", response_model=list[StudentResponse])
def list_all_students(db: Session = Depends(get_db), current_user: StudentDB = Depends(get_current_user)):
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


@app.put("/students/{student_id}", response_model=StudentResponse)
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