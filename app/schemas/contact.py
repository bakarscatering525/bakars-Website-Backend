from pydantic import BaseModel, EmailStr, Field


class ContactMessage(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str = Field(..., max_length=30)
    message: str = Field(..., max_length=2000)


class ContactResponse(BaseModel):
    success: bool = True
    message: str = "Thank you! Your message has been sent."
