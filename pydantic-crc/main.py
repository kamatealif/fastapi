from pydantic import BaseModel, EmailStr, AnyUrl, Field
from typing import List, Dict, Optional, Annotated
class Patient(BaseModel):
    name : Annotated[str, Field(max_length=50, title="Patient Name", description="Name of the patient", examples=['John Doe', 'Jane Doe'])]
    email: EmailStr
    github_url : AnyUrl
    age : int = Field(gt=0, le=120)
    weight : Annotated[float, Field(gt=0, lt=120, strict=True)]
    married : Annotated[bool, Field(default=False, description="Is the patient married?")]
    alergies : Annotated[ Optional[List[str]] ,Field(max_length=50, default=None)]
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

# patient_info = {"name": "John Doe", "age": 30, "weight": 75.5, "married": True, "alergies": ["penicillin", "aspirin"], "contact_info": {"email": "GZBb2@example.com", "phone": "123-456-7890"}}
# patient_info = {"name": "John Doe", "age": "30"} # this is also good because pydantic convert it to int
# patient1 = Patient(**patient_info)
# insert_data(patient1)
# update_data(patient1)


patient_info={"name": "Jane Doe", 'email': "janedoe@gmail.com", 'github_url':"https://github.com/janedoe", "age": 23, "weight": 50.2, "contact_info" : {"email": "GZBb2@example.com", "phone": "123-456-7890"}}
patient2 = Patient(**patient_info)
insert_data(patient2)
