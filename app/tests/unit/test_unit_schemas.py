import unittest
from unittest.mock import MagicMock
from unittest import TestCase
from tests.unit.test_base import TestBase
from src.schemas import ContactUpdate

class TestContactUpdate(TestBase):    
    def setUp(self):        
        super().setUp()
        self.contactUpdate = ContactUpdate()

    def test_is_dirty_has_attribute_with_value(self):        
        self.contactUpdate.name = "test"    
        self.logs.write(f"ContactUpdate.name attribute value set to '{self.contactUpdate.name}'")     
        
        result = self.contactUpdate.is_dirty

        self.assertTrue(result)                

    def test_is_dirty_has_no_attributes_with_value(self):
        self.logs.write(f"ContactUpdate object created without attributes")           
        
        result = self.contactUpdate.is_dirty        
        
        self.assertFalse(result)        
