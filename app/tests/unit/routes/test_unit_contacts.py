import unittest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from unittest import TestCase
from datetime import datetime
from tests.unit.test_base import TestBase
from src.database.models import User, Contact
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service
from fastapi import APIRouter, HTTPException, Depends, status
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.conf.config import settings
from src.routes.contacts import (
    read_contacts,
    read_contact,
    retrieve_birthdays,
    create_contact,
    update_contact,
    remove_contact
)

class TestContactRoutes(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user.id = 1

        self.contacts = []
        for _ in range(3):
            self.contacts.append(MagicMock(spec=Contact))

    @patch('src.repository.contacts.get_contacts')
    async def test_read_contacts(self, mock_func): 
        mock_func.return_value = self.contacts
        result = await read_contacts(filter=None,skip=0, limit=10, db=self.session, current_user=self.user)
        self.assertEqual(result, self.contacts)  

    @patch('src.repository.contacts.get_contacts')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_read_contacts_unauthorized(self, mock_func, mock_auth_func): 
        mock_func.return_value = self.contacts
        mock_auth_func.side_effect = self.credentials_exception
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await read_contacts(filter=None,skip=0, limit=10, db=self.session, current_user=mock_auth_func)
        self.assertEqual(context.exception.status_code, 401)   
        self.assertIsNone(result)  

    @patch('src.repository.contacts.get_contact')
    async def test_read_contact_found(self, mock_func): 
        mock_func.return_value = self.contacts[0]
        result = await read_contact(contact_id=1, db=self.session, current_user=self.user)
        self.assertEqual(result, self.contacts[0])  
    
    @patch('src.repository.contacts.get_contact')
    async def test_read_contact_not_found(self, mock_func): 
        mock_func.return_value = None
        with self.assertRaises(HTTPException) as context:
            result = await read_contact(contact_id=1, db=self.session, current_user=self.user)        
        self.assertEqual(context.exception.status_code, 404)
    
    @patch('src.repository.contacts.get_contact')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_read_contact_unauthorized(self, mock_func, mock_auth_func): 
        mock_func.return_value = self.contacts[0]
        mock_auth_func.side_effect = self.credentials_exception
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await read_contact(contact_id=1, db=self.session, current_user=mock_auth_func)        
        self.assertEqual(context.exception.status_code, 401)
        self.assertIsNone(result)

    @patch('src.repository.contacts.get_contacts_by_birthdays')
    async def test_retrieve_birthdays(self, mock_func): 
        mock_func.return_value = self.contacts
        result = await retrieve_birthdays(skip=0, limit=10, db=self.session, current_user=self.user)
        self.assertEqual(result, self.contacts)

    @patch('src.repository.contacts.get_contacts_by_birthdays')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_get_contacts_by_birthdays_unauthorized(self, mock_func, mock_auth_func): 
        mock_func.return_value = self.contacts
        mock_auth_func.side_effect = self.credentials_exception
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await retrieve_birthdays(skip=0, limit=10, db=self.session, current_user=mock_auth_func)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIsNone(result)
    
    @patch('src.repository.contacts.create_contact')
    async def test_create_contact(self, mock_func): 
        mock_func.return_value = self.contacts[0]
        body = MagicMock(spec=ContactBase)
        result = await create_contact(body=body, current_user=self.user)
        self.assertEqual(result, self.contacts[0])   
    
    @patch('src.repository.contacts.create_contact')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_create_contact_unauthorized(self, mock_func,mock_auth_func): 
        mock_func.return_value = self.contacts[0]
        body = MagicMock(spec=ContactBase)
        mock_auth_func.side_effect = self.credentials_exception
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await create_contact(body=body, current_user=mock_auth_func)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIsNone(result)

    @patch('src.repository.contacts.update_contact')
    async def test_update_contact_found(self, mock_func): 
        mock_func.return_value = self.contacts[0]
        body = MagicMock(spec=ContactUpdate)
        result = await update_contact(contact_id=1,body=body, current_user=self.user)
        self.assertEqual(result, self.contacts[0])   

    @patch('src.repository.contacts.update_contact')
    async def test_update_contact_not_found(self, mock_func): 
        mock_func.return_value = None
        body = MagicMock(spec=ContactUpdate)
        with self.assertRaises(HTTPException) as context:
            result = await update_contact(contact_id=1,body=body, current_user=self.user)
        self.assertEqual(context.exception.status_code, 404)

    @patch('src.repository.contacts.update_contact')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_update_contact_unauthorized(self, mock_func, mock_auth_func): 
        mock_func.return_value = self.contacts[0]
        mock_auth_func.side_effect = self.credentials_exception
        body = MagicMock(spec=ContactUpdate)
        result = None
        with self.assertRaises(Exception) as context:
            result = await update_contact(contact_id=1,body=body, current_user=mock_auth_func)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIsNone(result)

    @patch('src.repository.contacts.remove_contact')
    async def test_remove_contact_found(self, mock_func): 
        mock_func.return_value = self.contacts[0]
        result = await remove_contact(contact_id=1, current_user=self.user)
        self.assertEqual(result, self.contacts[0])   

    @patch('src.repository.contacts.remove_contact')
    async def test_remove_contact_not_found(self, mock_func): 
        mock_func.return_value = None
        body = MagicMock(spec=ContactUpdate)
        with self.assertRaises(HTTPException) as context:
            result = await remove_contact(contact_id=1, current_user=self.user)
        self.assertEqual(context.exception.status_code, 404)

    @patch('src.repository.contacts.remove_contact')
    @patch('src.services.auth.Auth.get_current_user')
    async def test_remove_contact_unauthorized(self, mock_func, mock_auth_func): 
        mock_func.return_value = self.contacts[0]
        mock_auth_func.side_effect = self.credentials_exception
        body = MagicMock(spec=ContactUpdate)
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await remove_contact(contact_id=1, current_user=mock_auth_func)
        self.assertEqual(context.exception.status_code, 401)
        self.assertIsNone(result)