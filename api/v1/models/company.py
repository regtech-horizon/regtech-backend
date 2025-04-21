from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, text, Boolean, Index, ForeignKey, Numeric, ARRAY, JSON

class Company(BaseTableModel):
    __tablename__ = "companies"
    creator_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_type = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_email = Column(String, nullable=False)
    company_phone = Column(String, nullable=False)
    company_website = Column(String, nullable=True)
    company_size = Column(String, nullable=True)
    year_founded = Column(Numeric, nullable=True)
    headquarters = Column(String, nullable=True)
    country = Column(String, nullable=True)
    description = Column(String, nullable=True)
    social_media_linkedIn = Column(String, nullable=True)
    social_media_ig = Column(String, nullable=True)
    social_media_X = Column(String, nullable=True)
    status = Column(String, nullable=False, default="active")
    logo = Column(String, nullable=True)
    services = Column(String, nullable=True)
    last_funding_date = Column(String, nullable=True)
    niche = Column(String, nullable=True)
    company_password = Column(String, nullable=True)
    founders = Column(ARRAY(String), nullable=True)

    creator = relationship("User", back_populates="companies")

    reviews = relationship("Review", back_populates="company", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="company", cascade="all, delete-orphan")
    advertisements = relationship("Advertisement", back_populates="company", cascade="all, delete-orphan")
    favorite_by = relationship("FavoriteCompany", back_populates="company", cascade="all, delete-orphan")
    profile = relationship("CompanyProfile", back_populates="company", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_companies_name', 'company_name'),
        Index('ix_companies_status', 'status'),
        Index('ix_companies_creator_id', 'creator_id'),
    )
    
    def __str__(self):
        return self.name