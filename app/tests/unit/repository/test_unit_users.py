import unittest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from unittest import TestCase
from datetime import datetime
from tests.unit.test_base import TestBase
from src.database.models import Contact, User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    confirmed_email,
    update_token,
    update_avatar
)

class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        #self.user = User(id=1)
        self.user = MagicMock(spec=User)
        self.user.id = 1
        self.user.refresh_token = "test"
        # self.user.username = "test"
        # self.user.email = "test"
        # self.user.password = "test"
        # self.user.created_at = datetime.now()
        # self.user.avatar = "test"
        # self.user.refresh_token = "test"
        # self.user.confirmed = True

    async def test_get_user_by_email_found(self):        
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email="test", db=self.session)
        self.assertEqual(result, self.user)    

    # async def test_get_contacts_by_birthdays(self):        
    #     self.session.query().filter().filter().all.return_value = self.contacts
    #     result = await get_contacts_by_birthdays(skip=0, limit=10, user=self.user, db=self.session)
    #     self.assertEqual(result, self.contacts)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="test", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(  username="test", 
                           password="test", 
                           email="test@example.com")
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)        
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))

    async def test_confirmed_email(self):        
        self.session.query().filter().first.return_value = self.user 
        self.session.commit.return_value = None       
        await confirmed_email(email="test", db=self.session)
        self.assertTrue(self.user.confirmed)    
    
    async def test_update_token(self):        
        token = "test_token"
        self.session.commit.return_value = None       
        await update_token(self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)  

    async def test_update_avatar(self):        
        url = "test_url"
        self.session.query().filter().first.return_value = self.user 
        self.session.commit.return_value = None       
        result = await update_avatar(email="test", url=url, db=self.session)
        self.assertEqual(result.avatar, url) 
