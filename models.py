from sqlalchemy import Column, Integer, String, Date, JSON, ForeignKey, Boolean
from db import Base, engine

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    nick = Column(String, nullable = False, unique = True)
    birthdate = Column(Date, nullable = False)
    description = Column(JSON, nullable = False)
    role_id = Column(Integer, ForeignKey("roles.id"))

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    description = Column(String, nullable = False)
    active = Column(Boolean, nullable = False)

class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    description = Column(String, nullable = False)
    start_date = Column(Date, nullable = False)
    end_date = Column(Date, nullable = False)

class User_specialization(Base):
    __tablename__ = "users_specializations"

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization_id = Column(Integer, ForeignKey("specializations.id"))

if __name__ == "__main__":
    Base.metadata.create_all(bind = engine)