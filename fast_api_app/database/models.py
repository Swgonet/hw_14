from sqlalchemy import Column, Integer, String, Date, Boolean

from connect_db import Base, engine


class UserAuth(Base):
    __tablename__ = 'users_auth'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    birthday_date = Column(Date)
    email = Column(String, nullable=False, index=True)
    phone_numbers = Column(String, nullable=False, index=True)
    other_description = Column(String, nullable=True, default=None)


Base.metadata.create_all(bind=engine)
