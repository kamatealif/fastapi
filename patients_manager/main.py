import uvicorn
from fastapi import FastAPI,Path, HTTPException, Query
import json

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
