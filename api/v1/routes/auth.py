import logging
from datetime import timedelta
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from api.v1.models.mail import create_message, mail

from fastapi import (
    BackgroundTasks,
    Depends,
    status,
    APIRouter,
    Response,
    Request,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated

from api.core.dependencies.email_sender import send_email
from api.utils.success_response import auth_response, success_response
from api.v1.models import User
from api.v1.schemas.mail import EmailModel
from api.v1.schemas.user import AdminCreate, Token, UserEmailSender
from api.v1.schemas.user import (
    LoginRequest,
    UserCreate,
)
# from api.v1.services.login_notification import send_login_notification
from api.db.database import get_db
from api.v1.services.user import user_service
from api.utils.settings import settings

auth = APIRouter(prefix="/auth", tags=["Authentication"])



  
@auth.post("/register", status_code=status.HTTP_201_CREATED, response_model=auth_response)
def register(
    request: Request,
    background_tasks: BackgroundTasks,
    response: Response,
    user_schema: UserCreate,
    db: Session = Depends(get_db),
):
    """Endpoint for a user to register their account"""

    # Create user account
    user = user_service.create(db=db, schema=user_schema)


    # verification_token = user_service.create_verification_token(user.id)

    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)


    response = auth_response(
        status_code=201,
        message="User created successfully",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "updated_at"]
            )
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )
    return response


@auth.post(path="/register-admin", status_code=status.HTTP_201_CREATED, response_model=auth_response)
def register_as_super_admin(
    request: Request, user: AdminCreate, db: Session = Depends(get_db)
):
    """Endpoint for super admin creation"""

    user = user_service.create_admin(db=db, schema=user)
    # create an organization for the user
    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=201,
        message="User created successfully",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "updated_at"]
            ),
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/login", status_code=status.HTTP_200_OK, response_model=auth_response)
def login(request: Request, login_request: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    """Endpoint to log in a user"""

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )
    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=200,
        message="Login successful",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "updated_at"]
            )
        },
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to log a user out of their account"""

    response = success_response(status_code=200, message="User logged put successfully")

    # Delete refresh token from cookies
    response.delete_cookie(key="refresh_token")

    return response

@auth.post('/send-mail')
async def send_mail(emails: EmailModel):
    emails = emails.email_addresses
    html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <title>Regtech Horizon Email</title>
        <style>
            body {
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #000000;
            }
            .container {
            max-width: 600px;
            margin: auto;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(173, 0, 0, 0.2);
            }
            .header {
            background-color: #AD0000;
            color: #ffffff;
            text-align: center;
            padding: 24px 20px;
            }
            .header h1 {
            margin: 0;
            font-size: 26px;
            letter-spacing: 1px;
            }
            .body {
            padding: 24px 20px;
            background-color: #ffffff;
            }
            .body h2 {
            color: #AD0000;
            margin-top: 0;
            }
            .footer {
            background-color: #f7f7f7;
            text-align: center;
            font-size: 12px;
            padding: 16px 20px;
            color: #555555;
            }
            .button {
            display: inline-block;
            background-color: #AD0000;
            color: #ffffff !important;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 20px;
            }
            @media (max-width: 600px) {
            .body, .header, .footer {
                padding: 16px;
            }
            }
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
            <h1>Welcome to Regtech Horizon</h1>
            </div>
            <div class="body">
            <h2>Hello,</h2>
            <p>We're thrilled to have you on board at <strong>Regtech Horizon</strong> – where innovation meets compliance.</p>
            <p>This is your gateway to the future of regulatory technology. Whether you're here to streamline processes, ensure compliance, or explore powerful insights — you've just taken a giant leap forward.</p>
            <p>Stay tuned. The horizon just got closer.</p>
            <a href="https://app.regtechhorizon.com" class="button">Get Started</a>
            </div>
            <div class="footer">
            &copy; 2025 Regtech Horizon. All rights reserved.<br>
            This is an automated email. Please do not reply.
            </div>
        </div>
        </body>
        </html>
        """
    message = create_message(
        recipients=emails,
        subject="Welcome to Regtech Horizon",
        body=html
    )

    await mail.send_message(message)

    return {"message": "Email sent successfully"}