import uvicorn
from fastapi import FastAPI,Path, HTTPException
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
def view_patient(patient_name : str = Path(..., description="Name of the patient", example="John Doe")):
    data = load_data();
    for patient in data:
        if patient["name"] == patient_name:
            return patient
    else:
       raise HTTPException(status_code=404, detail="Patient not found")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)