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
class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
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

# @app.get('/sort')
# def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

#     valid_fields = ['height', 'weight', 'bmi']

#     if sort_by not in valid_fields:
#         raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
#     if order not in ['asc', 'desc']:
#         raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
#     data = load_data()

#     sort_order = True if order=='desc' else False

#     sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

#     return sorted_data

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