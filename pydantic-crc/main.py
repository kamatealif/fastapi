from pydantic import BaseModel

class Patient(BaseModel):
    name : str
    age : int

def insert_data(patient : Patient):
    print(patient.name)
    print(patient.age)
    print("Inserted....")


# now i can also use this to update the data 
def update_data (patient : Patient):
    print(patient.name)
    print(patient.age)
    print("Updated....")

patient_info = {"name": "John Doe", "age": 30}
patient1 = Patient(**patient_info)

update_data(patient1)