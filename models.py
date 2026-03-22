from sqlalchemy import Column, Integer, String, Float
from db import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="pending")