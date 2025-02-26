from db import Base
from sqlalchemy import (Column, DateTime, Integer, String, Text, ForeignKey,
                        Boolean, BigInteger)


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_id = Column(Integer, ForeignKey("time_slots.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    request = Column(Text, nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False)


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    telegram = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_blocked = Column(Boolean, default=False)


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class TimeSlots(Base):
    __tablename__ = "time_slots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date_utc = Column(DateTime, nullable=False)
    end_date_utc = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
