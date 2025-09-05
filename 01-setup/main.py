from fastapi import FastAPI # pyright: ignore[reportMissingImports]
import json

app = FastAPI()


def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    return data

@app.get("/")
def hello():
    return {"message":"Hello from FASTAPI"}

@app.get("/about")
def about():
    return {"message" : "FASTAPI is a Api framework which is used to build the robust api for backend"}

@app.get("/patients")
def patients():
    data = load_data()
    return data 