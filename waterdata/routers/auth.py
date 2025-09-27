from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import database, models, utils, schemas
from . import oauth2

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):  # ✅ fixed here
    # check if user exists
    user = db.query(schemas.User).filter(schemas.User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    # verify password
    if not utils.verify(user_credentials.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    # create JWT token
    access_token = oauth2.create_access_token(data={"id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

