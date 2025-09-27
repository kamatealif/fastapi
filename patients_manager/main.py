from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

import sqlite3

def get_connection():
     # allow usage from multiple threads (typical for FastAPI)
    conn = sqlite3.connect('patients.db', check_same_thread=False)
     # return rows as sqlite3.Row (dict-like)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   create table if not exists patients(
                       patient_id int primary key,
                       name text not null,
                       city text not null,
                       age integer not null,
                       gender text not null check(gender in ('male', 'female', 'others')),
                       height real not null,
                       weight real not null,
                       bmi real not null,
                       verdict text not null);
                   """) 
    conn.commit()
    conn.close()
app = FastAPI()

@app.on_event('startup')
def on_startup():
    init_db()
    
#pydantic model for creating the patient
class Patient(BaseModel):

    id: Annotated[int, Field(..., description='ID of the patient', examples=['1'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"     
        else:
            return "Obese"

# pydantic model for updating the user info
class UpdatePatient(BaseModel):
    name: Annotated[Optional[str], Field(description='Name of the patient')] = None
    city: Annotated[Optional[str], Field(description='City where the patient is living')] = None
    age: Annotated[Optional[int], Field(gt=0, lt=120, description='Age of the patient')] = None
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(description='Gender of the patient')] = None
    height: Annotated[Optional[float], Field(gt=0, description='Height of the patient in mtrs')] = None
    weight: Annotated[Optional[float], Field(gt=0, description='Weight of the patient in kgs')] = None


def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)
        

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get('/view')
def view():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM patients''')
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

@app.get('/patient/{patient_id}')
def view_patient(patient_id: int = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patient
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'select * from patients where patient_id=\"{patient_id}\"')
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    result = [dict(row) for row in rows]
    conn.close()
    return result

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"""
                   SELECT * FROM patients
                   ORDER BY {sort_by} {order};
                   """)
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    
    return result

@app.post('/create')
def create_patient(patient: Patient):

    # load the data
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO patients (patient_id, name, city, age, gender, height, weight,bmi, verdict) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (patient.id, patient.name, patient.city, patient.age, patient.gender, patient.height, patient.weight, patient.bmi, patient.verdict))
        
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail='Patient already exists')
    finally:
        conn.close()
    
    # return statuscode to variafy patient created 
    return JSONResponse(status_code=201, content={'message': 'Patient created successfully'})


@app.put("/edit/{id}")
def update_patient(id: int, patch: UpdatePatient):
    conn = get_connection()
    cur = conn.cursor()

    # 1) fetch existing patient row (parameterized)
    cur.execute("SELECT * FROM patients WHERE patient_id = ?", (id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = dict(row)  # sqlite3.Row -> dict

    # 2) get only the fields the user sent
    changes = patch.model_dump(exclude_unset=True)   # only provided fields
    if not changes:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields provided to update")

    # 3) build a Patient instance from existing DB values (map patient_id -> id)
    patient_data = {
        "id": existing["patient_id"],
        "name": existing["name"],
        "city": existing["city"],
        "age": existing["age"],
        "gender": existing["gender"],
        "height": existing["height"],
        "weight": existing["weight"],
    }
    existing_patient = Patient(**patient_data)

    # 4) merge updates into the Patient model (validation applied)
    merged_patient = existing_patient.model_copy(update=changes)

    # 5) recompute computed fields
    new_bmi = merged_patient.bmi
    new_verdict = merged_patient.verdict

    # 6) prepare parameterized UPDATE (only changed fields + bmi & verdict)
    field_to_col = {
        "name": "name",
        "city": "city",
        "age": "age",
        "gender": "gender",
        "height": "height",
        "weight": "weight",
    }

    cols = []
    params = []

    for field, col in field_to_col.items():
        if field in changes:
            cols.append(f"{col} = ?")
            params.append(getattr(merged_patient, field))

    # always update bmi & verdict (depend on height/weight)
    cols.append("bmi = ?")
    params.append(new_bmi)
    cols.append("verdict = ?")
    params.append(new_verdict)

    params.append(id)  # WHERE clause parameter

    sql = f"UPDATE patients SET {', '.join(cols)} WHERE patient_id = ?"
    cur.execute(sql, tuple(params))
    conn.commit()

    # 7) return updated row
    cur.execute("SELECT * FROM patients WHERE patient_id = ?", (id,))
    updated_row = dict(cur.fetchone())
    conn.close()
    return JSONResponse(status_code=200, content={"message": "Patient updated", "patient": updated_row})

# delete route
@app.delete('/delete/{id}')
def delete_patient(id : int = Path(..., description='ID of the patient in the DB', example='1')):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT * FROM patients 
                   WHERE patient_id = ?
                   """,(id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    
    cursor.execute("""
                   DELETE FROM patients 
                   WHERE patient_id = ?
                   """,(id,))
    conn.commit()
    conn.close()
    return JSONResponse(status_code=200, content={'message': 'Patient deleted successfully'})