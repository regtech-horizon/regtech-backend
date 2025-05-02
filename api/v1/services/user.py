import random
from typing import Any, Optional, Annotated
import datetime as dt
from uuid import UUID
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.context import CryptContext

from api.core.base.services import Service
from api.db.database import get_db

from api.utils.db_validators import check_model_existence
from api.v1.models import User
from api.v1.schemas import user
from api.utils.settings import settings
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(Service):
    """User service"""

    def fetch_all(
        self,
        db: Session,
        page: int,
        per_page: int,
        **query_params: Optional[Any],
    ):
        """
        Fetch all users
        Args:
            db: database Session object
            page: page number
            per_page: max number of users in a page
            query_params: params to filter by
        """
        per_page = min(per_page, 10)

        # Enable filter by query parameter
        filters = []
        if all(query_params):
            # Validate boolean query parameters
            for param, value in query_params.items():
                if value is not None and not isinstance(value, bool):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid value for '{param}'. Must be a boolean.",
                    )
                if value == None:
                    continue
                if hasattr(User, param):
                    filters.append(getattr(User, param) == value)
        query = db.query(User)
        total_users = query.count()
        if filters:
            query = query.filter(*filters)
            total_users = query.count()

        all_users: list = (
            query.order_by(desc(User.created_at))
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )

        return self.all_users_response(all_users, total_users, page, per_page)

    def all_users_response(
        self, users: list, total_users: int, page: int, per_page: int
    ):
        """
        Generates a response for all users
        Args:
            users: a list containing user objects
            total_users: total number of users
        """
        if not users or len(users) == 0:
            return user.AllUsersResponse(
                message="No User(s) for this query",
                status="success",
                status_code=200,
                page=page,
                per_page=per_page,
                total=0,
                data=[],
            )
        all_users = [
            user.UserData.model_validate(usr, from_attributes=True)
            for usr in users
        ]
        return user.AllUsersResponse(
            message="Users successfully retrieved",
            status="success",
            status_code=200,
            page=page,
            per_page=per_page,
            total=total_users,
            data=all_users,
        )

    def fetch(self, db: Session, id):
        """Fetches a user by their id"""

        user = check_model_existence(db, User, id)

        # return user if user is not deleted
        if not user.is_deleted:
            return user

    def get_user_by_id(self, db: Session, id: str):
        """Fetches a user by their id"""

        user = check_model_existence(db, User, id)
        return user

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Fetches a user by their email address.

        Args:
            db: The database session.
            email: The email address of the user.

        Returns:
            The user object if found, otherwise None.
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return user

    def fetch_by_email(self, db: Session, email):
        """Fetches a user by their email"""

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    def create(self, db: Session, schema: user.UserCreate):
        """Creates a new user"""

        if db.query(User).filter(User.email == schema.email).first():
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Hash password
        schema.password = self.hash_password(password=schema.password)

        # Create user object with hashed password and other attributes from schema
        user = User(**schema.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    
    
    def update(
        self, db: Session, current_user: User, schema: user.UserUpdate, id=None
    ):
        """Function to update a User"""

        # Get user from access token if provided, otherwise fetch user by id
        user = (
            self.fetch(db=db, id=id)
            if current_user.is_superadmin and id is not None
            else self.fetch(db=db, id=current_user.id)
        )

        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "email":
                continue
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    def delete(
        self,
        db: Session,
        id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """Function to soft delete a user"""

        # Get user by id if provided, otherwise fetch user access token
        if id:
            user = check_model_existence(db, User, id)
        elif access_token:
            user = self.get_current_user(access_token, db)
        else:
            raise HTTPException(
                status_code=400, detail="User ID or access token required"
            )

        user.is_deleted = True
        db.commit()

        # return super().delete()

    def authenticate_user(self, db: Session, email: str, password: str):
        """Function to authenticate a user"""

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=400, detail="Invalid user credentials"
            )

        if not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=400, detail="Invalid user credentials"
            )

        return user

    def perform_user_check(self, user: User):
        """This checks if a user is active and verified and not a deleted user"""

        if not user.is_active:
            raise HTTPException(detail="User is not active", status_code=403)

    def hash_password(self, password: str) -> str:
        """Function to hash a password"""
        hashed_password = pwd_context.hash(secret=password)
        return hashed_password

    def verify_password(self, password: str, hash: str) -> bool:
        """Function to verify a hashed password"""
        return pwd_context.verify(secret=password, hash=hash)
    
    def verify_access_token(self, access_token: str, credentials_exception):
        try:
            payload = jwt.decode(
                access_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id = payload.get("user_id")  # Key in JWT payload
            token_type = payload.get("type")

            if user_id is None:
                raise credentials_exception

            if token_type == "refresh":
                raise HTTPException(
                    detail="Refresh token not allowed", status_code=400
                )

            token_data = user.TokenData(user_id=user_id, type=token_type)
        except JWTError as err:
            print(err)
            raise credentials_exception
        
        return token_data
    
    
    def get_current_user(
        self,
        access_token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = self.verify_access_token(access_token, credentials_exception)
        
        try:
            # Convert string `user_id` to UUID
            # user_uuid = UUID(token.user_id)  # <-- Use `user_id`
            user_uuid = (token.user_id)  # <-- Use `user_id`
        except ValueError:
            raise credentials_exception

        # user = db.query(User).filter(User.id == user_uuid).first()
        user = db.query(User).filter(User.id == str(user_uuid)).first()
        # user = db.query(User).filter(User.id == user_uuid).first()

        if not user:
            raise credentials_exception

        return user
    
    def create_access_token(self, user_id: str) -> str:
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {"user_id": user_id, "exp": expires, "type": "access"}  # Key: `user_id`
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Function to create access token"""

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            days=settings.JWT_REFRESH_EXPIRY
        )
        data = {"user_id": user_id, "exp": expires, "type": "refresh"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt


    def create_admin(self, db: Session, schema: user.UserCreate):
        """Creates a new admin"""

        if db.query(User).filter(User.email == schema.email).first():
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Hash password
        schema.password = self.hash_password(password=schema.password)

        # Create user object with hashed password and other attributes from schema
        user = User(**schema.model_dump())

        user.is_superadmin = True
        db.add(user)
        db.commit()

        # create data privacy setting

        db.refresh(user)

        return user

    def change_password(
        self,
        new_password: str,
        user: User,
        db: Session,
        current_password: Optional[str] = None,
    ):
        """Endpoint to change the user's password"""
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Current Password and New Password cannot be the same",
            )
        if current_password is None:
            if user.password is None:
                user.password = self.hash_password(new_password)
                db.commit()
                return
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Current Password must not be empty, unless setting password for the first time.",
                )
        elif not self.verify_password(current_password, user.password):
            raise HTTPException(
                status_code=400, detail="Incorrect current password"
            )
        else:
            user.password = self.hash_password(new_password)
            db.commit()

    def get_current_super_admin(
        self,
        access_token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """Function to get current logged in superadmin user"""
        user = self.get_current_user(access_token, db)
        
        if not user.is_superadmin:
            raise HTTPException(
                status_code=403,
                detail="Access denied. Super admin privileges required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user


user_service = UserService()
