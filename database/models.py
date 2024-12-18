from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(String)
    name = Column(String)
    contact_info = Column(String)
    loyalty_points = Column(Integer)
    account_status = Column(String)
    state = Column(String)
