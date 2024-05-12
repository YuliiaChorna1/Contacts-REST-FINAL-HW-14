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
    contacts = await repository_contacts.get_contacts(filter, skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/birthdays/", response_model=List[ContactResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def retrieve_birthdays(skip: int = 0, limit: int = 20, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts_by_birthdays(skip, limit, current_user, db)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, current_user, db)



@router.patch("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=rl_times, seconds=rl_seconds))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
