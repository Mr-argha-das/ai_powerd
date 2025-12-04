from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = "employers"   # change if your table name is different

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    phone = Column(String(15), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)


from sqlalchemy import Column, String, BigInteger, TIMESTAMP, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.mysql import BIGINT

Base = declarative_base()

class JobSekker(Base):
    __tablename__ = "job_seekers"   # Change if your table name is different

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=False)

    resume = Column(String(255), nullable=True)

    email_verified_at = Column(TIMESTAMP, nullable=True)

    remember_token = Column(String(100), nullable=True)

    status = Column(String(255), nullable=False, default="pending")

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)
