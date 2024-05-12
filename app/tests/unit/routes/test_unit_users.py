from typing import BinaryIO
import unittest
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb
from src.routes.users import (
    read_users_me,
    update_avatar_user
)

class TestUsersRoutes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user.username = "test_user"
        self.user.email = "test@example.com"
        self.user.id = 1        
    
    async def test_read_users_me(self):     
        result = await read_users_me(current_user=self.user)
        self.assertEqual(result, self.user)    
    
    @patch('src.repository.users.update_avatar')
    @patch('cloudinary.CloudinaryImage.build_url')    
    @patch('cloudinary.uploader.upload')    
    @patch('cloudinary.config')
    async def test_update_avatar_user(self, mocked_config, mocked_upload, mocked_build_url, mocked_update_avatar): 
        r = MagicMock()         
        file = MagicMock(spec=UploadFile)  
        file.file = MagicMock(BinaryIO)    
        url = "test_url"
        mocked_config.return_value = None        
        mocked_upload.return_value = r
        mocked_build_url.return_value = url   
        mocked_update_avatar.return_value = self.user     
        result = await update_avatar_user(file=file, current_user=self.user, db=self.session)
        mocked_update_avatar.assert_called_with(self.user.email, url, self.session)   
        self.assertEqual(result, self.user)