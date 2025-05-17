import dns.resolver
from typing import Optional, Annotated, List
from pydantic import BaseModel, EmailStr, StringConstraints, model_validator
from email_validator import validate_email, EmailNotValidError

class EmailModel(BaseModel):
    email_addresses: List[str]