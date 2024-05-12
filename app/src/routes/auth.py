from typing import List
from src.services.email import send_email
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that handles user signup.

    This function takes a UserModel object, BackgroundTasks object, Request object, and a SQLAlchemy session as input. It checks if a user with the provided email already exists. If not, it creates a new User object, adds it to the session, commits the session, and sends a confirmation email to the new user.

    Args:
        body (UserModel): The UserModel object containing the details of the user to be created.
        background_tasks (BackgroundTasks): The BackgroundTasks object for adding tasks to be performed in the background.
        request (Request): The Request object containing details about the client's request.
        db (Session): The SQLAlchemy session object.

    Returns:
        dict: A dictionary containing the newly created User object and a success message.

    Raises:
        HTTPException: An HTTPException is raised with a 409 status code if a user with the provided email already exists.

    Example:
        >>> from fastapi import Depends, BackgroundTasks
        >>> from .database import get_db
        >>> 
        >>> @app.post("/signup")
        >>> async def signup_endpoint(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
        >>>     return await signup(body, background_tasks, request, db)
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that confirms a user's email.

    This function takes a token string and a SQLAlchemy session as input. It retrieves the email associated with the token, queries the database for a User object whose email matches the retrieved email, and confirms the user's email if it hasn't been confirmed yet.

    Args:
        token (str): The token associated with the user's email.
        db (Session): The SQLAlchemy session object.

    Returns:
        dict: A dictionary containing a success message.

    Raises:
        HTTPException: An HTTPException is raised with a 400 status code if a user with the provided email does not exist or if there is a verification error.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/confirmed_email/{token}")
        >>> async def confirm_user_email(token: str, db: Session = Depends(get_db)):
        >>>     return await confirmed_email(token, db)
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that handles email confirmation requests.

    This function takes a RequestEmail object, BackgroundTasks object, Request object, and a SQLAlchemy session as input. It checks if a user with the provided email already exists and if their email is confirmed. If the user exists and their email is not confirmed, it sends a confirmation email to the user.

    Args:
        body (RequestEmail): The RequestEmail object containing the email of the user requesting confirmation.
        background_tasks (BackgroundTasks): The BackgroundTasks object for adding tasks to be performed in the background.
        request (Request): The Request object containing details about the client's request.
        db (Session): The SQLAlchemy session object.

    Returns:
        dict: A dictionary containing a success message.

    Example:
        >>> from fastapi import Depends, BackgroundTasks
        >>> from .database import get_db
        >>> 
        >>> @app.post("/request_email")
        >>> async def request_email_endpoint(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
        >>>     return await request_email(body, background_tasks, request, db)
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that handles user login.

    This function takes an OAuth2PasswordRequestForm object and a SQLAlchemy session as input. It checks if a user with the provided email exists, if their email is confirmed, and if the provided password is correct. If all checks pass, it generates access and refresh JWT tokens, updates the user's refresh token in the database, and returns the tokens.

    Args:
        body (OAuth2PasswordRequestForm): The OAuth2PasswordRequestForm object containing the user's email and password.
        db (Session): The SQLAlchemy session object.

    Returns:
        dict: A dictionary containing the access and refresh tokens, and the token type.

    Raises:
        HTTPException: An HTTPException is raised with a 401 status code if a user with the provided email does not exist, if their email is not confirmed, or if the provided password is incorrect.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/login")
        >>> async def login_endpoint(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        >>>     return await login(body, db)
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Asynchronous endpoint that handles access token refresh.

    This function takes an HTTPAuthorizationCredentials object and a SQLAlchemy session as input. It decodes the email from the provided refresh token, queries the database for a User object whose email matches the decoded email, and checks if the provided refresh token matches the one stored in the database. If all checks pass, it generates new access and refresh tokens, updates the user's refresh token in the database, and returns the new tokens.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTPAuthorizationCredentials object containing the refresh token.
        db (Session): The SQLAlchemy session object.

    Returns:
        dict: A dictionary containing the new access and refresh tokens, and the token type.

    Raises:
        HTTPException: An HTTPException is raised with a 401 status code if a user with the provided email does not exist or if the provided refresh token does not match the one stored in the database.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/refresh_token")
        >>> async def refresh_token_endpoint(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
        >>>     return await refresh_token(credentials, db)
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
