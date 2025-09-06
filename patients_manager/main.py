from fastapi import FastAPI
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


@app.get("/patients/{patient_name : str}")
def view_patient(patient_name):
    data = load_data();
    for patient in data:
        if patient["name"] == patient_name:
            return patient
    else:
        return {"message": "Patient not found"}