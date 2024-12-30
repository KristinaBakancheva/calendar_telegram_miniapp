from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean, UniqueConstraint
from db import Base, engine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, index=True)
    telegram = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, unique=True, index=True)
    birthday = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))

    def __repr__(self):
        return f"User {self.id} - {self.name}"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)


class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    def __repr__(self):
        return f"Specialization {self.id} "


class User_specialization(Base):
    __tablename__ = "users_specializations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization_id = Column(Integer, ForeignKey("specializations.id"))

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'specialization_id', name='unique_user_specialization'),
                        )

    def __repr__(self):
        return f"User {self.user_id} , {self.specialization_id}"


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)