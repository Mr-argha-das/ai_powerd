from sqlalchemy import DECIMAL, TIMESTAMP, BigInteger, Boolean, Column, String, Text, Date, DateTime, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from db.database import Base

class MatrimoniesUser(Base):
    __tablename__ = "matrimonies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)

    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    phone = Column(String(15), nullable=True)
    gender = Column(String(20), nullable=True)
    date_of_birth = Column(String(155), nullable=True)
    age = Column(String(100), nullable=True)
    marital_status = Column(String(255), nullable=True)
    religion = Column(String(255), nullable=True)
    caste = Column(String(255), nullable=True)
    mother_tongue = Column(String(255), nullable=True)
    height = Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    occupation = Column(String(255), nullable=True)
    income = Column(DECIMAL(10, 2), nullable=True)

    about_me = Column(Text, nullable=True)
    partner_preference = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    profile_photo = Column(String(255), nullable=True)

    is_profile_completed = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    bio = Column(Text, nullable=True)
    photos = Column(Text, nullable=True)

    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    living_status = Column(String(100), nullable=True)
    smoke = Column(String(50), nullable=True)
    drink = Column(String(50), nullable=True)
    interest = Column(Text, nullable=True)
    qualification = Column(String(100), nullable=True)
    performance = Column(String(255), nullable=True)
    company = Column(String(150), nullable=True)
    annual_income = Column(String(100), nullable=True)
    income_private = Column(String(20), nullable=True)

    father_occupation = Column(String(100), nullable=True)
    mother_occupation = Column(String(100), nullable=True)
    family_type = Column(String(100), nullable=True)

    partner_age_range = Column(String(50), nullable=True)
    partner_height_range = Column(String(50), nullable=True)
    partner_education = Column(String(100), nullable=True)
    partner_location = Column(String(150), nullable=True)
    partner_note = Column(Text, nullable=True)

    status = Column(String(255), default="pending")
    plan_status = Column(String(255), default="Unpaid")