from typing import List
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from datetime import datetime, timedelta
from src.schemas import ContactBase, ContactUpdate, ContactResponse


async def get_contacts(filter: str | None, skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    query = db.query(Contact).filter(Contact.user_id == user.id)
    filters = parse_filter(filter)
    for attr, value in filters.items():
        query = query.filter(getattr(Contact, attr) == value)
    query = query.offset(skip).limit(limit)
    return query.all()


# name::Alan|surname::Brown
def parse_filter(filter: str | None) -> dict:
    if filter:
        lst = filter.split("|")
        dct = {}
        for f in lst:
            key, value = f.split("::")
            dct[key] = value
        return dct
    return {}


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.user_id == user.id).filter(Contact.id == contact_id).first()


async def get_contacts_by_birthdays(skip: int, limit: int, user: User, db: Session) -> Contact:
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
    contact = db.query(Contact).filter(Contact.user_id == user.id).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
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
