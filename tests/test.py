import unittest
import dbhandler

class TestDBHandler(unittest.TestCase):

    def test_CheckEmail(self):
        # "james@email.com" is one of the test entries in the database
        self.assertEqual(False, dbhandler.checkEmail("james@email.com"))

    def test_GetLogin(self):
        self.assertEqual(["PASSWORD", "SALT"], dbhandler.checkEmail("james@email.com"))
        
if __name__ == "__main__":
    unittest.main()
