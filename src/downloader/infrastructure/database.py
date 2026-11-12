from sqlmodel import SQLModel, create_engine
from downloader.config.settings import env

MYSQL_USER = env.MYSQL_USERNAME
MYSQL_PASSWORD = env.MYSQL_PASSWORD
MYSQL_HOST = env.MYSQL_HOST
MYSQL_PORT = env.MYSQL_PORT
MYSQL_DB = env.MYSQL_DATABASE

mysql_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(mysql_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
