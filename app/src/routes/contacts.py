from typing import List
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter
from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi import APIRouter, HTTPException, Depends, status
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.conf.config import settings


router = APIRouter(prefix='/contacts', tags=["contacts"])
rl_times = settings.rate_limiter_times
rl_seconds = settings.rate_limiter_seconds


@router.get("/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def read_contacts(filter: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that retrieves a list of contacts for the current user from the database.

    This function takes a filter string, skip and limit integers for pagination, a SQLAlchemy session, and the current user as input. It queries the database for contacts associated with the current user, applies the filter if provided, and returns a paginated list of contacts.

    Args:
        filter (str, optional): A string representing the filter criteria. If None, no filtering is applied. Defaults to None.
        skip (int, optional): The number of records to skip from the start. Used for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Used for pagination. Defaults to 100.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which contacts are to be retrieved.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects that match the query.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/contacts/")
        >>> async def read_contacts_endpoint(filter: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        >>>     return await read_contacts(filter, skip, limit, db, current_user)
    """
    contacts = await repository_contacts.get_contacts(filter, skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that retrieves a specific contact for the current user from the database.

    This function takes a contact ID, a SQLAlchemy session, and the current user as input. It queries the database for a Contact object whose ID matches the provided contact ID and is associated with the current user. If the contact exists, it returns the contact. Otherwise, it raises an HTTPException.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which the contact is to be retrieved.

    Returns:
        ContactResponse: The ContactResponse object that matches the query, if it exists. Otherwise, None.

    Raises:
        HTTPException: An HTTPException is raised with a 404 status code if a contact with the provided ID does not exist.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/contacts/{contact_id}")
        >>> async def read_contact_endpoint(contact_id: int, db: Session = Depends(get_db)):
        >>>     return await read_contact(contact_id, db, current_user)
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def retrieve_birthdays(skip: int = 0, limit: int = 20, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that retrieves a list of contacts for the current user from the database whose birthdays are within the next week.

    This function takes skip and limit integers for pagination, a SQLAlchemy session, and the current user as input. It queries the database for contacts associated with the current user whose birthdays are within the next week, and returns a paginated list of contacts.

    Args:
        skip (int, optional): The number of records to skip from the start. Used for pagination. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Used for pagination. Defaults to 20.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which contacts are to be retrieved.

    Returns:
        List[ContactResponse]: A list of ContactResponse objects that match the query.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/birthdays/")
        >>> async def retrieve_birthdays_endpoint(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
        >>>     return await retrieve_birthdays(skip, limit, db, current_user)
    """
    contacts = await repository_contacts.get_contacts_by_birthdays(skip, limit, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that creates a new contact for the current user in the database.

    This function takes a ContactBase object, a SQLAlchemy session, and the current user as input. It creates a new Contact object associated with the current user and adds it to the database.

    Args:
        body (ContactBase): The ContactBase object containing the details of the contact to be created.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which the contact is to be created.

    Returns:
        ContactResponse: The newly created ContactResponse object.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/contacts/")
        >>> async def create_contact_endpoint(body: ContactBase, db: Session = Depends(get_db)):
        >>>     return await create_contact(body, db, current_user)
    """
    return await repository_contacts.create_contact(body, current_user, db)



@router.patch("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that updates a specific contact for the current user in the database.

    This function takes a ContactUpdate object, a contact ID, a SQLAlchemy session, and the current user as input. It queries the database for a Contact object whose ID matches the provided contact ID and is associated with the current user. If the contact exists, it updates the contact's details with the provided information and returns the updated contact. Otherwise, it raises an HTTPException.

    Args:
        body (ContactUpdate): The ContactUpdate object containing the updated details of the contact.
        contact_id (int): The ID of the contact to be updated.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which the contact is to be updated.

    Returns:
        ContactResponse: The updated ContactResponse object if it exists, otherwise None.

    Raises:
        HTTPException: An HTTPException is raised with a 404 status code if a contact with the provided ID does not exist.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.patch("/contacts/{contact_id}")
        >>> async def update_contact_endpoint(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db)):
        >>>     return await update_contact(body, contact_id, db, current_user)
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Asynchronous endpoint that removes a specific contact for the current user from the database.

    This function takes a contact ID, a SQLAlchemy session, and the current user as input. It queries the database for a Contact object whose ID matches the provided contact ID and is associated with the current user. If the contact exists, it removes the contact from the database and returns the removed contact. Otherwise, it raises an HTTPException.

    Args:
        contact_id (int): The ID of the contact to be removed.
        db (Session): The SQLAlchemy session object.
        current_user (User): The User object for which the contact is to be removed.

    Returns:
        ContactResponse: The removed ContactResponse object if it exists, otherwise None.

    Raises:
        HTTPException: An HTTPException is raised with a 404 status code if a contact with the provided ID does not exist.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.delete("/contacts/{contact_id}")
        >>> async def remove_contact_endpoint(contact_id: int, db: Session = Depends(get_db)):
        >>>     return await remove_contact(contact_id, db, current_user)
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
