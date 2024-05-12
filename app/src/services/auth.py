import redis
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies a password against a hashed password.

        This method takes a plain text password and a hashed password as input. It verifies the plain text password against the hashed password using the password context.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the password is verified, False otherwise.

        Example:
            >>> auth = Auth()
            >>> plain_password = "my_password"
            >>> hashed_password = auth.get_password_hash(plain_password)
            >>> auth.verify_password(plain_password, hashed_password)
            True
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hashed password.

        This method takes a plain text password as input and returns a hashed version of the password using the password context.

        Args:
            password (str): The plain text password to hash.

        Returns:
            str: The hashed password.

        Example:
            >>> auth = Auth()
            >>> plain_password = "my_password"
            >>> hashed_password = auth.get_password_hash(plain_password)
            >>> print(hashed_password)
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Asynchronous method that creates a JWT access token.

        This method takes a dictionary of data and an optional expiration time delta as input. It copies the data, sets the issue and expiration times, and encodes the data into a JWT access token using the secret key and algorithm.

        Args:
            data (dict): The data to encode into the access token.
            expires_delta (Optional[float], optional): The number of seconds until the token expires. If None, the token will expire in 15 minutes. Defaults to None.

        Returns:
            str: The encoded JWT access token.

        Example:
            >>> auth = Auth()
            >>> data = {"sub": "example@example.com"}
            >>> access_token = await auth.create_access_token(data)
            >>> print(access_token)
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(minutes=15)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token 
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Asynchronously creates a refresh token.

        This method creates a JWT-encoded refresh token with a payload that includes the provided data and an expiration time. The expiration time is either now plus the provided `expires_delta` (in seconds), or 7 days from now if `expires_delta` is not provided.

        :param data: A dictionary containing the data to be included in the token.
        :type data: dict
        :param expires_delta: The number of seconds from now until the token should expire. If not provided, the token will expire 7 days from now.
        :type expires_delta: float, optional
        :return: A JWT-encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Asynchronously decodes the provided refresh token.

        This method attempts to decode the given refresh token using the secret key and algorithm. If the scope of the payload is 'refresh_token', it returns the email from the payload. If the scope is not 'refresh_token' or if there is a JWTError, it raises an HTTPException with status code 401.

        :param str refresh_token: The refresh token to be decoded.
        :return: The email from the payload if the scope of the payload is 'refresh_token'.
        :rtype: str
        :raises HTTPException: If the scope of the payload is not 'refresh_token' or if there is a JWTError.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Asynchronously retrieves the current user based on the provided token.

        This method decodes the JWT from the provided token, checks the scope and the email in the payload.
        If the scope is 'access_token' and the email exists, it retrieves the user from the database.
        If any of these checks fail, it raises a credentials exception.

        Parameters
        ----------
        token : str
            The token to be decoded to get the user information. This is a dependency that defaults to oauth2_scheme.
        db : Session
            The database session for retrieving the user. This is a dependency that defaults to get_db.

        Raises
        ------
        HTTPException
            If the token cannot be validated or the user does not exist in the database.

        Returns
        -------
        User
            The user retrieved from the database.

        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user
    
    def create_email_token(self, data: dict):
        """
        Creates a JWT token for the provided data.

        This method creates a copy of the provided data, adds an issued at time (iat) and an expiration time (exp) to it, and then encodes it into a JWT token using the secret key and algorithm of the Auth class.

        Parameters
        ----------
        data : dict
            The data to be encoded into the token.

        Returns
        -------
        str
            The JWT token created from the data.

        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Asynchronously retrieves the email from the provided token.

        This method decodes the JWT from the provided token and extracts the email from the payload. If the token cannot be decoded, it raises an HTTPException with status code 422 (Unprocessable Entity).

        Parameters
        ----------
        token : str
            The token to be decoded to get the email.

        Raises
        ------
        HTTPException
            If the token cannot be decoded or is invalid for email verification.

        Returns
        -------
        str
            The email retrieved from the token.

        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")



auth_service = Auth()
