from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that retrieves the current user's details.

    This function takes the current user as input and returns the user's details.

    Args:
        current_user (User): The User object for which the details are to be retrieved. This is obtained from the authentication service.

    Returns:
        UserDb: The UserDb object containing the current user's details.

    Example:
        >>> from fastapi import Depends
        >>> 
        >>> @app.get("/me/")
        >>> async def read_current_user_endpoint(current_user: User = Depends(auth_service.get_current_user)):
        >>>     return await read_users_me(current_user)
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that updates the avatar of the current user.

    This function takes an uploaded file, the current user, and a SQLAlchemy session as input. It uploads the file to Cloudinary, generates a URL for the uploaded image, and updates the user's avatar in the database with the generated URL.

    Args:
        file (UploadFile, optional): The uploaded file containing the new avatar. Defaults to File().
        current_user (User): The User object for which the avatar is to be updated.
        db (Session): The SQLAlchemy session object.

    Returns:
        UserDb: The updated UserDb object.

    Example:
        >>> from fastapi import Depends, File, UploadFile
        >>> from .database import get_db
        >>> 
        >>> @app.patch("/avatar")
        >>> async def update_avatar_endpoint(file: UploadFile = File(), db: Session = Depends(get_db)):
        >>>     return await update_avatar_user(file, current_user, db)
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
