import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLALCHEMY_DB_URL= 'postgresql://<username>:<password>@ip-address/hostname>/<databasename>'

#SQLALCHEMY_DB_URL= 'postgresql://postgres:22441084@localhost/rainwise_db'
SQLALCHEMY_DB_URL='postgresql://postgres:YrBGDCvsYwewpioYTeEykseYwXjhpvBB@trolley.proxy.rlwy.net:57196/railway'


engine=create_engine(SQLALCHEMY_DB_URL)
Sessionlocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally: 
        db.close()
        
Base= declarative_base()

