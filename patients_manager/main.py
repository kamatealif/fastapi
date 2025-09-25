import uvicorn
from fastapi import FastAPI,Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal


import json

# pydantic model to data validation 
class Patient(BaseModel):
    # Unique identifier for the patient
    patient_id: Annotated[str, Field(..., description="Unique identifier for the patient", examples=['p001'])]
    
    # Name of the patient
    name: Annotated[str, Field(..., description="Name of the patient", examples=['John Doe'])]
    
    # Weight of the patient in kilograms
    weight: Annotated[float, Field(..., description="Weight of the patient in kilograms", examples=[70.0])]
    
    # Height of the patient in centimeters
    height: Annotated[float, Field(..., description="Height of the patient in centimeters", examples=[170.0])]
    
    # City of the patient
    city: Annotated[str, Field(..., description="City of the patient", examples=['New York'])]
    
    # Email of the patient
    email: Annotated[str, Field(..., description="Email of the patient", examples=['john.doe@example.com'])]
    
    # Phone number of the patient
    phone: Annotated[str, Field(..., description="Phone number of the patient", examples=['123-456-7890'])]
    
    # Age of the patient
    age: Annotated[int, Field(..., description="Age of the patient", examples=[25])]
    
    # Gender of the patient
    gender: Annotated[Literal['male','female'], Field(..., description="Gender of the Patient", examples=['male'])]
    
    # calculating bim
    @computed_field
    @property
    def bmi(self)-> float:
        height = self.height/ 100
        bmi = round(self.weight/ (height**2),2)
        return bmi

    @computed_field
    @property
    def verdict_prediction(self) -> str:
        if self.bmi < 18.5:
            return "Under weight"
        elif  self.bmi >= 18.5 and self.bmi <= 25:
            return "Normal"
        elif self.bmi >= 25 and self.bmi <= 29.9:
            return "Over weight"
        elif self.bmi >= 30 and self.bmi <= 34.9:
            return "class I obesity"
        elif self.bmi <= 35 and self.bmi <= 39.9:
            return "class II obesity"
        elif self.bmi >= 40:
            return "class III obesity"
    
    
app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

@app.get("/")
def home():
    return {"message": "Hello World"}

@app.get("/patients")
def patients(): 
    data = load_data()
    return data 


@app.get("/patient/{patient_name}")
def view_patient(patient_name : str = Path(..., description="Name of the patient", examples="John Doe")):
    data = load_data();
    for patient in data:
        if patient["name"] == patient_name:
            return patient
    else:
        raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_by(sort_by: str = Query(..., description="Sort by name, age, height, weight, bmi", examples="name"), order: str = Query('asc', description="Order by asc or desc", examples="asc")):
    valid_fields = ['name','age,','height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field, select from {valid_fields}")

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, details=f"Invalid order, select from asc or desc")
    data = load_data()

    sorted_data = sorted(data, key=lambda x: x[sort_by], reverse=(order == 'desc'))


    return sorted_data
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
