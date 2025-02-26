from sqlalchemy import (Column, Integer, String, Date, Text, ForeignKey,
                        Boolean, BigInteger)
from db import Base


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