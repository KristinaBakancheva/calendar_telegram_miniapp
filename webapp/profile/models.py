from db import Base
from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime,
                        ForeignKey, Integer, String, Text, Time,
                        UniqueConstraint)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    telegram = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, index=True)
    description = Column(Text, nullable=False)
    gmt = Column(Time, nullable=False)
    gmt_sign = Column(String, nullable=False)
    mentors_blocked = Column(Boolean, default=False)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)


class UserRole(Base):
    __tablename__ = "users_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'role_id', name='unique_UserRole'),
                        )


class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)


class UserSpecialization(Base):
    __tablename__ = "users_specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization_id = Column(Integer, ForeignKey("specializations.id"))

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'specialization_id', name='unique_UserSpecialization'),
                        )
