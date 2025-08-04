from pydantic import BaseModel

class OnboardingModel(BaseModel):
    fullname: str
    email: str
    department: str = "Software Engineering"