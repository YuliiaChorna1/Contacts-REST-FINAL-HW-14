from typing import BinaryIO
import unittest
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status, UploadFile, File
from sqlalchemy.orm import Session
from unittest.mock import MagicMock, patch
from src.database.models import User
from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.routes.auth import (
    signup,
    confirmed_email,
    request_email,
    login,
    refresh_token
)

class TestUsersRoutes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user.username = "test_user"
        self.user.confirmed = False
        self.user.email = "test@example.com"
        self.user.id = 1     
        self.request = MagicMock(spec=Request)   
        self.tasks = MagicMock(spec=BackgroundTasks)
    
    @patch('src.repository.users.get_user_by_email')
    @patch('src.repository.users.create_user')
    async def test_signup(self, mocked_create_user, mocked_get_user_by_email):     
        body = UserModel(  username="test", 
                           password="test", 
                           email="test@example.com")                
        
        mocked_get_user_by_email.return_value = None
        mocked_create_user.return_value = self.user        
        result = await signup(body=body, background_tasks=self.tasks, request=self.request, db=self.session)
        self.assertEqual(result["user"], self.user)    
        mocked_create_user.assert_called_with(body, self.session)
    
    @patch('src.repository.users.get_user_by_email')
    @patch('src.repository.users.create_user')
    async def test_signup_exists(self, mocked_create_user, mocked_get_user_by_email):     
        body = UserModel(  username="test", 
                           password="test", 
                           email="test@example.com")                
        
        mocked_get_user_by_email.return_value = self.user 
        mocked_create_user.return_value = self.user        
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await signup(body=body, background_tasks=self.tasks, request=self.request, db=self.session)
        self.assertEqual(context.exception.status_code, 409)   
        self.assertIsNone(result)  
        mocked_create_user.assert_not_called()

    @patch('src.services.auth.Auth.get_email_from_token')
    @patch('src.repository.users.get_user_by_email')
    @patch('src.repository.users.confirmed_email')
    async def test_confirmed_email(self, mocked_confirmed_email, mocked_get_user_by_email, mocked_get_email_from_token):     
        token = "test_token"
        mocked_get_email_from_token.return_value = self.user.email
        mocked_get_user_by_email.return_value = self.user                
        result = await confirmed_email(token=token, db=self.session)
        self.assertEqual(result["message"], "Email confirmed")    
        mocked_confirmed_email.assert_called_with(self.user.email, self.session)
    
    @patch('src.services.auth.Auth.get_email_from_token')
    @patch('src.repository.users.get_user_by_email')
    @patch('src.repository.users.confirmed_email')
    async def test_confirmed_email_already_confirmed(self, mocked_confirmed_email, mocked_get_user_by_email, mocked_get_email_from_token):     
        token = "test_token"
        mocked_get_email_from_token.return_value = self.user.email
        mocked_get_user_by_email.return_value = self.user  
        self.user.confirmed = True              
        result = await confirmed_email(token=token, db=self.session)
        self.assertEqual(result["message"], "Your email is already confirmed")    
        mocked_confirmed_email.assert_not_called()

    @patch('src.services.auth.Auth.get_email_from_token')
    @patch('src.repository.users.get_user_by_email')
    @patch('src.repository.users.confirmed_email')
    async def test_confirmed_email_not_found(self, mocked_confirmed_email, mocked_get_user_by_email, mocked_get_email_from_token):     
        token = "test_token"
        mocked_get_email_from_token.return_value = self.user.email
        mocked_get_user_by_email.return_value = None  
        result = None
        with self.assertRaises(HTTPException) as context:
            result = await confirmed_email(token=token, db=self.session)
        self.assertEqual(context.exception.status_code, 400)   
        self.assertIsNone(result)  
        mocked_confirmed_email.assert_not_called()  