from pydantic import BaseModel
from typing import List, Dict, Optional
class Patient(BaseModel):
    name : str
    age : int
    weight : float
    married : bool
    alergies : Optional[List[str]] = None;
    contact_info : Dict[str, str]

def insert_data(patient : Patient):
    for k, v in patient.model_dump().items():
        print(f"{k} : {v}");
    print("Inserted....")
    print()


# now i can also use this to update the data 
def update_data (patient : Patient):
    print(patient.name)
    print(patient.age)
    print("Updated....")
    print()

patient_info = {"name": "John Doe", "age": 30, "weight": 75.5, "married": True, "alergies": ["penicillin", "aspirin"], "contact_info": {"email": "GZBb2@example.com", "phone": "123-456-7890"}}
# patient_info = {"name": "John Doe", "age": "30"} # this is also good because pydantic convert it to int
patient1 = Patient(**patient_info)
insert_data(patient1)
update_data(patient1)


patient_info={"name": "Jane Doe", "age": 23, "weight": 50.2, "married":True, "contact_info" : {"email": "GZBb2@example.com", "phone": "123-456-7890"}}
patient2 = Patient(**patient_info)
insert_data(patient2)
