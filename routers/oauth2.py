from jose import JWTError, jwt
from datetime import datetime, timedelta
from .. import models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme= OAuth2PasswordBearer(tokenUrl='login')
#secret key
#algorithm hs256
#expiration time
#for a string like this command 
# openssl rand -hex 32
SECRET_KEY="1b6283b98781d26340a9dd4890cd67440fffac1367d6a6af031e27bb6d1be09c"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token (token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id:str=payload.get("id")
        if id is None:
            raise credentials_exception
        token_data=models.Token_Data(id=id)
    except JWTError:
        raise credentials_exception
    return token_data
    
def get_current_user (token:str=Depends (oauth2_scheme)):
    credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"couldnt validate credentials",headers={"WWW-Authenticate":"Bearer"})

    return verify_access_token(token,credentials_exception)



