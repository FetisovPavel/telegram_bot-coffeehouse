import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, User

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def get_user(user_id):
    session = Session()
    user = session.query(User).filter_by(tg_user_id=user_id).first()
    session.close()
    return user


def get_user_state(user_id):
    session = Session()
    user = session.query(User).filter_by(tg_user_id=str(user_id)).first()
    session.close()
    return user.state


def post_user(user_id):
    session = Session()
    user = User(tg_user_id=user_id)
    session.add(user)
    session.commit()
    session.close()


def update_user(user_id, dictionary):
    session = Session()
    session.query(User).filter_by(tg_user_id=user_id).update(dictionary)
    session.commit()
    session.close()












