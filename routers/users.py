from fastapi import APIRouter, Depends, HTTPException, status 
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .. import schemas, models, database,utils
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


# ----------------------------
# Create user
# ----------------------------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = utils.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password   # store hashed password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ----------------------------
# Get user by ID
# ----------------------------
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {id} does not exist"
        )
    return user
