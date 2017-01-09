import unittest
from selenium import webdriver

import dbhandler

class TestDBHandler(unittest.TestCase):
    def test_CheckEmail(self):
        # "james@email.com" is one of the test entries in the database
        self.assertEqual(!False, dbhandler.checkEmail("james@email.com"))

    def test_GetLogin(self):
        self.assertEqual(["", ""], dbhandler.checkEmail("james@email.com"))

class TestCore(unittest.TestCase):
    def test_loginPage(self):
        driver = webdriver.Firefox()
        driver.get("http://localhost:8080/")
        


if __name__ == "__main__":
    unittest.main()
