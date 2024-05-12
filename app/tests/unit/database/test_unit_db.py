import os
import unittest
from unittest.mock import MagicMock
from unittest import TestCase
from tests.unit.test_base import TestBase
from src.database.db import SessionLocal, get_db

class TestDb(TestBase):    
    pass
    # def setUp(self):        
    #     super().setUp()
    #     SessionLocal = MagicMock()       
    #     self.mocked_session = "some_session" 
    #     SessionLocal.__call__.return_value.session = self.mocked_session

    # def test_get_db(self):        
    #     result = get_db()
    #     self.assertIs(result, self.mocked_session)                
