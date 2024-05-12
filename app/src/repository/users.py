from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

async def get_user_by_email(email: str, db: Session) -> User:
    """
    Fetch a user from the database by their email.

    Args:
        email (str): The email of the user to fetch.
        db (Session): The database session.

    Returns:
        User: The user object if found, else None.
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user in the database.

    Args:
        body (UserModel): The user data.
        db (Session): The database session.

    Returns:
        User: The created user object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email of a user.

    Args:
        email (str): The email of the user to confirm.
        db (Session): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token of a user.

    Args:
        user (User): The user object.
        token (str | None): The new refresh token.
        db (Session): The database session.
    """
    user.refresh_token = token
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar of a user.

    Args:
        email (str): The email of the user.
        url (str): The new avatar URL.
        db (Session): The database session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
