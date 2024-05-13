import os
import unittest
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import Mock, MagicMock, patch
from unittest import TestCase
from tests.unit.test_base import TestBase
from src.database.db import SessionLocal, get_db

class TestDb(TestBase):    
    pass
    def setUp(self):        
        super().setUp()
        self.mocked_session = MagicMock(spec=Session)
        #self.mocked_session_maker = MagicMock(spec=sessionmaker, return_value=self.mocked_session)             

    #@patch('src.database.db.SessionLocal')
    def test_get_db(self):#, session_local):        
        mock_session_macker = Mock(spec=sessionmaker, return_value=self.mocked_session)
        with patch('src.database.db.SessionLocal', mock_session_macker):
            result = next(get_db())
        self.assertIs(result, self.mocked_session)                
