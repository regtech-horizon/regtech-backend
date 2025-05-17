from email_validator import validate_email, EmailNotValidError
import dns.resolver
from datetime import datetime
from typing import (Optional, Union,
                    List, Annotated, Dict,
                    Literal)

from pydantic import (BaseModel, EmailStr,
                      field_validator, ConfigDict,
                      StringConstraints,
                      model_validator)
                      
from pydantic import Field  # Added this import
from enum import Enum

def validate_mx_record(domain: str):
    """
    Validate mx records for email
    """
    try:
        # Try to resolve the MX record for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True if mx_records else False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

class UserBase(BaseModel):
    """Base user schema"""

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None

class UserEmailSender(BaseModel):
    email: EmailStr

    
class UserCreate(BaseModel):
    """Schema to create a user"""

    email: EmailStr
    subscription: str
    phone_number: Optional[str] = None
    password: Annotated[
        str, StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    """Added the confirm_password field to UserCreate Model"""
    confirm_password: Annotated[
        str, 
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        ),
        Field(exclude=True)  # exclude confirm_password field
    ]
    first_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]
    last_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        password = values.get('password')
        confirm_password = values.get('confirm_password') # gets the confirm password
        email = values.get("email")

        # constraints for password
        if not any(c.islower() for c in password):
            raise ValueError("password must include at least one lowercase character")
        if not any(c.isupper() for c in password):
            raise ValueError("password must include at least one uppercase character")
        if not any(c.isdigit() for c in password):
            raise ValueError("password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in password):
            raise ValueError("password must include at least one special character")

        """Confirm Password Validation"""

        if not confirm_password:
            raise ValueError("Confirm password field is required")
        elif password != confirm_password:
            raise ValueError("Passwords do not match")
        
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        
        return values

class UserUpdate(BaseModel):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None

class UserData(BaseModel):
    """
    Schema for users to be returned to superadmin
    """
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_deleted: bool
    subscription: str
    phone_number: Optional[str] = None
    role: str
    status: str
    is_superadmin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# class UserData(BaseModel):
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     email: EmailStr
#     subscription: str
#     phone_number: Optional[str] = None
    
#     class Config:
#         from_attributes = True

class UserData2(BaseModel):
    """
    Schema for users to be returned to superadmin
    """
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_deleted: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProfileData(BaseModel):
    """
    Pydantic model for a profile.
    """
    id: str
    created_at: datetime
    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    recovery_email: Optional[EmailStr]

    model_config = ConfigDict(from_attributes=True)

class OrganisationData(BaseModel):
    """Base organisation schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    email: Optional[EmailStr] = None
    industry: Optional[str] = None
    user_role: List[str]
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuthMeResponse(BaseModel):
    """
    Auth response
    """
    message: str
    status_code: int
    data: Dict[Literal["user", "organisations", "profile"],
               Union[UserData2, List[OrganisationData], ProfileData]]


class AllUsersResponse(BaseModel):
    """
    Schema for all users
    """
    message: str
    status_code: int
    status: str
    page: int
    per_page: int
    total: int
    data: Union[List[UserData], List[None]]    

class AdminCreateUser(BaseModel):
    """
    Schema for admin to create a users
    """
    email: EmailStr
    first_name: str
    last_name: str
    password: str = ''
    is_active: bool = False
    is_deleted: bool = False
    is_verified: bool = False
    is_superadmin: bool = False

    model_config = ConfigDict(from_attributes=True)


class AdminCreateUserResponse(BaseModel):
    """
    Schema response for user created by admin
    """
    message: str
    status_code: int
    status: str
    data: UserData

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        if not isinstance(values, dict):
            return values
        password = values.get('password')
        email = values.get("email")

        # constraints for password
        if not any(c.islower() for c in password):
            raise ValueError("password must include at least one lowercase character")
        if not any(c.isupper() for c in password):
            raise ValueError("password must include at least one uppercase character")
        if not any(c.isdigit() for c in password):
            raise ValueError("password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in password):
            raise ValueError("password must include at least one special character")
        
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        
        return values


class EmailRequest(BaseModel):
    email: EmailStr

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validates email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class Token(BaseModel):
    token: str

class TokenData(BaseModel):
    user_id: str
    type: Optional[str] = "access"


class DeactivateUserSchema(BaseModel):
    """Schema for deactivating a user"""

    reason: Optional[str] = None
    confirmation: bool


# schemas/user.py
from pydantic import BaseModel, Field, field_validator

class ChangePasswordSchema(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    confirm_new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    def validate_password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letters')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain numbers')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        if self.new_password != self.confirm_new_password:
            raise ValueError('Passwords do not match')
        return self

class ChangePwdRet(BaseModel):
    """schema for returning change password response"""

    status_code: int
    message: str


class MagicLinkRequest(BaseModel):
    """Schema for magic link creation"""

    email: EmailStr

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validate email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class MagicLinkResponse(BaseModel):
    """Schema for magic link respone"""

    message: str

class UserRoleSchema(BaseModel):
    """Schema for user role"""

    role: str
    user_id: str
    org_id: str

    @field_validator("role")
    @classmethod
    def role_validator(cls, value):
        """
        Validate role
        """
        if value not in ["admin", "user", "guest", "owner"]:
            raise ValueError("Role has to be one of admin, guest, user, or owner")
        return value


class AdminCreate(BaseModel):
    """Schema to create an admin user"""

    email: EmailStr
    phone_number: Optional[str] = None
    password: Annotated[
        str, StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    confirm_password: Annotated[
        str, 
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        ),
        Field(exclude=True)  # exclude confirm_password field
    ]
    first_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]
    last_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        password = values.get('password')
        confirm_password = values.get('confirm_password') # gets the confirm password
        email = values.get("email")

        # constraints for password
        if not any(c.islower() for c in password):
            raise ValueError("password must include at least one lowercase character")
        if not any(c.isupper() for c in password):
            raise ValueError("password must include at least one uppercase character")
        if not any(c.isdigit() for c in password):
            raise ValueError("password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in password):
            raise ValueError("password must include at least one special character")

        """Confirm Password Validation"""

        if not confirm_password:
            raise ValueError("Confirm password field is required")
        elif password != confirm_password:
            raise ValueError("Passwords do not match")
        
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        
        return values
    
class UserStatus(BaseModel):
    active: str = "active"
    inactive: str = "inactive"
    pending: str = "pending"
    completed: str = "completed"