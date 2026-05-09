from sqlalchemy import Column, Integer, String, Float, Date, Text
from .database import Base
import datetime


class Wine(Base):
    __tablename__ = "wines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    varietal = Column(String, nullable=False)
    producer = Column(String)
    region = Column(String)
    country = Column(String)
    vintage = Column(Integer)
    rating = Column(Float)
    notes = Column(Text)
    date_tried = Column(Date, default=datetime.date.today)
    price = Column(Float)
