from typing import List
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from datetime import datetime, timedelta
from src.schemas import ContactBase, ContactUpdate, ContactResponse


async def get_contacts(filter: str | None, skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Asynchronous function that retrieves a list of contacts for a specific user from the database.

    This function queries the database for contacts associated with a specific user. It supports pagination and filtering.

    Args:
        filter (str | None): A string representing the filter criteria. If None, no filtering is applied.
        skip (int): The number of records to skip from the start. Used for pagination.
        limit (int): The maximum number of records to return. Used for pagination.
        user (User): The user object for which contacts are to be retrieved.
        db (Session): The SQLAlchemy session object.

    Returns:
        List[Contact]: A list of Contact objects that match the query.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/contacts/")
        >>> async def read_contacts(filter: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        >>>     contacts = await get_contacts(filter, skip, limit, current_user, db)
        >>>     return contacts
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)
    filters = parse_filter(filter)
    for attr, value in filters.items():
        query = query.filter(getattr(Contact, attr) == value)
    query = query.offset(skip).limit(limit)
    return query.all()


# name::Alan|surname::Brown
def parse_filter(filter: str | None) -> dict:
    """
    Function to parse a filter string into a dictionary.

    This function takes a filter string as input, splits it into key-value pairs, and returns a dictionary. The filter string should be in the format "key::value|key::value|...". If the filter is None or an empty string, an empty dictionary is returned.

    Args:
        filter (str | None): The filter string to parse. Each filter is in the format "key::value". Multiple filters are separated by "|".

    Returns:
        dict: A dictionary where the keys are the filter keys and the values are the filter values.

    Example:
        >>> filter = "name::John|age::30|city::New York"
        >>> parse_filter(filter)
        >>> {'name': 'John', 'age': '30', 'city': 'New York'}
    """
    if filter:
        lst = filter.split("|")
        dct = {}
        for f in lst:
            key, value = f.split("::")
            dct[key] = value
        return dct
    return {}


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Asynchronous function that retrieves a specific contact for a user from the database.

    This function queries the database for a specific contact associated with a user. It returns the first contact that matches the user and contact_id criteria.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        user (User): The user object for which the contact is to be retrieved.
        db (Session): The SQLAlchemy session object.

    Returns:
        Contact: The Contact object that matches the query.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/contacts/{contact_id}")
        >>> async def read_contact(contact_id: int, db: Session = Depends(get_db)):
        >>>     contact = await get_contact(contact_id, current_user, db)
        >>>     return contact
    """
    return db.query(Contact).filter(Contact.user_id == user.id).filter(Contact.id == contact_id).first()


async def get_contacts_by_birthdays(skip: int, limit: int, user: User, db: Session) -> Contact:
    """
    Asynchronous function that retrieves contacts for a user from the database whose birthdays are within the next week.

    This function queries the database for contacts associated with a user. It filters contacts whose birthdays are within the next 7 days from today.

    Args:
        skip (int): The number of records to skip from the start. Used for pagination.
        limit (int): The maximum number of records to return. Used for pagination.
        user (User): The user object for which contacts are to be retrieved.
        db (Session): The SQLAlchemy session object.

    Returns:
        Contact: The Contact objects that match the query.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.get("/contacts/birthdays")
        >>> async def read_contacts_by_birthdays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        >>>     contacts = await get_contacts_by_birthdays(skip, limit, current_user, db)
        >>>     return contacts
    """
    from_date = datetime.today()
    to_date = datetime.today() + timedelta(days=7)
    query = db.query(Contact).filter(Contact.user_id == user.id)
    query = query.filter(
        and_(
            func.extract("month", Contact.birthday) == func.extract("month", from_date),
            func.extract("day", Contact.birthday) >= func.extract("day", from_date),
            func.extract("day", Contact.birthday) < func.extract("day", to_date)
        )
    )
    return query.all()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    """
    Asynchronous function that creates a new contact for a user in the database.

    This function takes a ContactBase object, a User object, and a SQLAlchemy session as input. It creates a new Contact object, adds it to the session, commits the session, refreshes the contact object, and returns it.

    Args:
        body (ContactBase): The ContactBase object containing the details of the contact to be created.
        user (User): The User object for which the contact is to be created.
        db (Session): The SQLAlchemy session object.

    Returns:
        Contact: The newly created Contact object.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.post("/contacts/")
        >>> async def create_new_contact(body: ContactBase, db: Session = Depends(get_db)):
        >>>     contact = await create_contact(body, current_user, db)
        >>>     return contact
    """
    contact = Contact(
        name=body.name, 
        surname=body.surname, 
        email=body.email, 
        phone=body.phone, 
        birthday=body.birthday, 
        address=body.address,
        user=user
        )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Asynchronous function that removes a specific contact for a user from the database.

    This function queries the database for a specific contact associated with a user. If the contact exists, it deletes the contact from the database and commits the changes.

    Args:
        contact_id (int): The ID of the contact to be removed.
        user (User): The user object for which the contact is to be removed.
        db (Session): The SQLAlchemy session object.

    Returns:
        Contact | None: The removed Contact object if it exists, otherwise None.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.delete("/contacts/{contact_id}")
        >>> async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
        >>>     contact = await remove_contact(contact_id, current_user, db)
        >>>     return contact
    """
    contact = db.query(Contact).filter(Contact.user_id == user.id).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    Asynchronous function that updates a specific contact for a user in the database.

    This function queries the database for a specific contact associated with a user. If the contact exists, it updates the contact's details with the provided information and commits the changes.

    Args:
        contact_id (int): The ID of the contact to be updated.
        body (ContactUpdate): The ContactUpdate object containing the updated details of the contact.
        user (User): The user object for which the contact is to be updated.
        db (Session): The SQLAlchemy session object.

    Returns:
        Contact | None: The updated Contact object if it exists, otherwise None.

    Example:
        >>> from fastapi import Depends
        >>> from .database import get_db
        >>> 
        >>> @app.put("/contacts/{contact_id}")
        >>> async def update_existing_contact(contact_id: int, body: ContactUpdate, db: Session = Depends(get_db)):
        >>>     contact = await update_contact(contact_id, body, current_user, db)
        >>>     return contact
    """
    contact = db.query(Contact).filter(Contact.user_id == user.id).filter(Contact.id == contact_id).first()
    if contact:
        contact.name=body.name or contact.name, 
        contact.surname=body.surname or contact.surname, 
        contact.email=body.email or contact.email, 
        contact.phone=body.phone or contact.phone, 
        contact.birthday=body.birthday or contact.birthday, 
        contact.address=body.address or contact.address
        contact.updated_at = func.now() if body.is_dirty else contact.updated_at
        db.add(contact)
        db.commit()
    return contact
