import unittest
from unittest import TestLoader
import tests.unit.test_unit_schemas
import tests.unit.repository.test_unit_contacts
import tests.unit.test_base
import tests.unit.routes.test_unit_contacts
import tests.unit.routes.test_unit_users
import tests.unit.routes.test_unit_auth


if __name__ == '__main__':
    # unittest.main()
    # unittest.main("tests.unit.test_unit_schemas")    
    unittest.main("tests.unit.routes.test_unit_auth")    