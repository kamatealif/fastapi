from pydantic import BaseModel, EmailStr, Field, field_validator

from typing import List, Dict, Optional, Annotated


class Patient(BaseModel):
    name : str
    age: int
    weight : float
    married: Annotated[bool, Field(default=False,description="Is the patient married?")]
    alergies: Annotated[ Optional[List[str]] ,Field(max_length=50, default=None)]
    email: Annotated[EmailStr, Field(title="Email Address", description="Email address of the patient", examples=['GZBb2@example.com'])]
    
    
    # here goes the field_validator Example
    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        valid_domains = ['hdfc.com', 'sbi.com', 'icici.com']
        
        domain_name = value.split("@")[-1]
        
        if domain_name not in valid_domains:
            raise ValueError(f"Email domain must be one of the following: {', '.join(valid_domains)}")
        return value
    
def update_data(patient: Patient):
    for key, value in patient.model_dump().items():
        print(f"{key} : {value}")
    
patient_info = {"name": "John Doe", "age": 30, "weight": 75.5, "married": True, "alergies": ["penicillin", "aspirin"], "email": "GZBb2@hdfc.com"}

patient =Patient(**patient_info)

update_data(patient)