""" User data model
"""

from sqlalchemy import Column, String, text, Boolean, Index
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import validates, relationship


class User(BaseTableModel):
    __tablename__ = "users"
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    
    is_active = Column(Boolean, server_default=text("true"))
    is_superadmin = Column(Boolean, server_default=text("false"))
    is_deleted = Column(Boolean, server_default=text("false"))
    # is_verified = Column(Boolean, server_default=text("false"))
    role = Column(String, nullable=False, default="user")
    status = Column(String, nullable=False, default="active")
    subscription = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    companies = relationship("Company", back_populates="creator", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")
    favorite_companies = relationship("FavoriteCompany", back_populates="user", cascade="all, delete-orphan")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    news_articles = relationship("News", back_populates="author", cascade="all, delete-orphan")
    audit_trails = relationship("AuditTrail", back_populates="admin", cascade="all, delete-orphan")

    @validates("is_superadmin")
    def update_role(self, key, value):
        """ Update role whenever is_superadmin changes """
        self.role = "admin" if value else "user"
        return value

    @validates("is_active")
    def update_status(self, key, value):
        """ Update status whenever is_active changes """
        self.status = "active" if value else "inactive"
        return value

    # Defining indexes for frequently queried columns
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_is_active', 'is_active'),
        Index('ix_users_is_deleted', 'is_deleted'),
        Index('ix_users_is_superadmin', 'is_superadmin'),
        Index('ix_users_first_name_last_name', 'first_name', 'last_name'),
    )

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict

    def __str__(self):
        return self.email
