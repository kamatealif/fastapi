from pydantic import BaseModel, EmailStr, Field

from typing import List, Dict, Optional, Annotated


class Patient(BaseModel):
    name : str
    age: int
    weight : float
    married: Annotated[bool, Field(default=False,description="Is the patient married?")]
    alergies: Annotated[ Optional[List[str]] ,Field(max_length=50, default=None)]
    email: Annotated[EmailStr, Field(title="Email Address", description="Email address of the patient", examples=['GZBb2@example.com'])]
    
def update_data(patient: Patient):
    for key, value in patient.model_dump().items():
        print(f"{key} : {value}")
    
patient_info = {"name": "John Doe", "age": 30, "weight": 75.5, "married": True, "alergies": ["penicillin", "aspirin"], "email": "GZBb2@example.com"}

patient =Patient(**patient_info)

update_data(patient)