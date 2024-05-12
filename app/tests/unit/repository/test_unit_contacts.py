import unittest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from unittest import TestCase
from datetime import datetime
from tests.unit.test_base import TestBase
from src.database.models import Contact, User
from src.schemas import ContactBase, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contacts_by_birthdays,
    create_contact,
    remove_contact,
    update_contact
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        #self.user = User(id=1)
        self.user = MagicMock(spec=User)
        self.user.id = 1
        # self.user.username = "test"
        # self.user.email = "test"
        # self.user.password = "test"
        # self.user.created_at = datetime.now()
        # self.user.avatar = "test"
        # self.user.refresh_token = "test"
        # self.user.confirmed = True
        self.contacts = []
        for _ in range(3):
            self.contacts.append(MagicMock(spec=Contact))

    async def test_get_contacts(self):        
        self.session.query().filter().offset().limit().all.return_value = self.contacts
        result = await get_contacts(filter=None,skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, self.contacts)    

    async def test_get_contacts_by_birthdays(self):        
        self.session.query().filter().filter().all.return_value = self.contacts
        result = await get_contacts_by_birthdays(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, self.contacts)

    async def test_get_contact_found(self):
        self.session.query().filter().filter().first.return_value = self.contacts[0]
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, self.contacts[0])

    async def test_get_contact_not_found(self):
        self.session.query().filter().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactBase(name="test", 
                           surname="test", 
                           email="test@example.com",
                           phone="+380999999999",
                           birthday="2024-04-15",
                           address="test")
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        user = User(id=1)
        result = await create_contact(body=body, user=user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)        
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.address, body.address)
        self.assertIs(result.user, user)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = self.contacts[0]
        self.session.query().filter().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdate(name="test", 
                           surname="test", 
                           email="test@example.com",
                           phone="+380999999999",
                           birthday="2024-04-15",
                           address="test")
        contact = self.contacts[0]
        self.session.query().filter().filter().first.return_value = contact        
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(name="test", 
                           surname="test", 
                           email="test@example.com",
                           phone="+380999999999",
                           birthday="2024-04-15",
                           address="test")
        self.session.query().filter().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)
    
