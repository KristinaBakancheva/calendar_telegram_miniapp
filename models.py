from sqlalchemy import (Column, Integer, String, Date, Text, ForeignKey,
                        Boolean, UniqueConstraint, Time, DateTime, BigInteger)
from db import Base, engine


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

    def __repr__(self):
        return f"User {self.id} - {self.name}"


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

    def __repr__(self):
        return f"UserRole {self.user_id} , {self.role_id}"


class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    def __repr__(self):
        return f"Specialization {self.id} "


class UserSpecialization(Base):
    __tablename__ = "users_specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization_id = Column(Integer, ForeignKey("specializations.id"))

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'specialization_id', name='unique_UserSpecialization'),
                        )

    def __repr__(self):
        return f"UserSpecialization {self.user_id} , {self.specialization_id}"


class Requests(Base):
    __tablename__ = "requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, index=True)
    telegram = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    date = Column(Date, nullable=False)
    in_db = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"Requests {self.id} - {self.name}"


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

    def __repr__(self):
        return f"User {self.id} - {self.start_date_utc}"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    telegram = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    client_blocked = Column(Boolean, default=False)

    def __repr__(self):
        return f"User {self.id} "


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slot_id = Column(Integer, ForeignKey("time_slots.id"))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    request = Column(Text, nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
