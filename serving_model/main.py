from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated
import pickle
import pandas as pd

# import the ml model
with open('./models/model.pk','rb') as f:
    model = pickle.load(f)
    
    
# fast api app object 
app = FastAPI()



tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

# pydantic model to validate incoming data 
class UserInput(BaseModel):
    age : Annotated[int, Field(..., gt=18, lt=120, description="Age of the person")]
    weight : Annotated[float, Field(..., gt=0, description="Weight of the person")]
    height : Annotated[float, Field(..., gt=0, lt=2.5 description="Height of the person")]
    income_lpa: Annotated[float, Field(..., gt=0, description="Income of the person")]
    smoker: Annotated[bool, Field(..., description="Smoking status of the person")]
    city:Annotated[str, Field(..., description="City of the person")] 
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job','business_owner', 'unemployed', 'private_job'], Field(..., description="Occupation of the person")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight/(self.height**2)
    
    
    @computed_field
    @property
    def life_style_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        
        elif self.smoker and self.bmi > 27:
            return "medium"
        else: 
            return "low"
        
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return 'adult'
        elif self.age < 68:
            return 'middle_aged'
        else:
            return 'old'
        
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3