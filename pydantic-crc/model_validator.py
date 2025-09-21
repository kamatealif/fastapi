from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional, Annotated, Dict

class Patient(BaseModel):
    name: str
    age: int
    weight: float
    married: Annotated[bool, Field(default=False, description="Is the patient married?")]
    alergies: Annotated[Optional[List[str]], Field(max_length=50, default=None)]
    email: Annotated[EmailStr, Field(title="Email Address", description="Email address of the patinet")]
    contact_info : Dict[str, str]
    
    # now we have to check if the age > 60 then in contact_info email and phone both are mandatory
    @model_validator(mode='after')
    def check_contact_info(cls, model):
        if model.age > 60: 
            if 'email' not in model.contact_info or 'phone' not in model.contact_info or 'address' not in model.contact_info:
                raise ValueError("For patients older than 60, both email and phone must be provided in contact_info.")
        return model
    
def update_data(patient: Patient):
    for key, value in patient.model_dump().items():
        print(f"{key} : {value}")
    print("Updated...")
patient_info = {"name": "John Doe", "age": 67, "weight": 75.5, "married": True, "alergies": ["penicillin", "aspirin"], "email": "GZBb2@example.com", "contact_info" : {"email": "GZBb2@example.com", "phone": "123-456-7890", "address": "123 Main St"}}

pateint = Patient(**patient_info)

update_data(pateint)