from fastapi import FastAPI # pyright: ignore[reportMissingImports]

app = FastAPI()

@app.get("/")
def hello():
    return {"message":"Hello from FASTAPI"}

@app.get("/about")
def about():
    return {"message" : "FASTAPI is a Api framework which is used to build the robust api for backend"}