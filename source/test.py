import unittest
from selenium import webdriver

import dbhandler

class TestDBHandler(unittest.TestCase):
    # Function 'makeConnection()' is tested by proxy throughit's use in all
    # other functions being tested.
    def test_CheckEmail(self):
        self.assertEqual(False, dbhandler.checkEmail("james@email.com"))

    def test_GetLogin(self):
        self.assertEqual({'password': "$2b$12$geZhg2ZjprZ16HbTgyq./OwefllzO/Dv0f7uhkIGbmmo.2eBDtkMy",
                        'salt': "$2b$12$geZhg2ZjprZ16HbTgyq./O"}, dbhandler.getLogin("james@email.com"))

    def test_checkAdmin(self):
        self.assertTrue(dbhandler.checkAdmin(1))
        self.assertEqual(0, dbhandler.checkAdmin(2)[0]['admin'])

    def test_getUserName(self):
        self.assertEqual("jack", dbhandler.getUserName(2)['name'])
        self.assertEqual("janet", dbhandler.getUserName(5)['name'])

    def test_getChatName(self):
        self.assertEqual("finance", dbhandler.getChatName(1)['name'])
        self.assertEqual("legal", dbhandler.getChatName(2)['name'])

    def test_getMemberIDs(self):
        ids = dbhandler.getMemberIDs(2)
        self.assertEqual(3, ids[0]['ID'])
        self.assertEqual(4, ids[1]['ID'])

    def test_getUserID(self):
        self.assertEqual(4, dbhandler.getUserID("jane@email.com")['ID'])

    def test_getChats(self):
        chats = dbhandler.getChats(1)
        self.assertEqual('finance', chats[0]['name'])
        self.assertEqual('admin', chats[1]['name'])

    def test_getChatNameID(self):
        chats = dbhandler.getChats("james@email.com")
        self.assertEqual('finance', chats[0]['name'])
        self.assertEqual('admin', chats[1]['name'])
        
#class TestCore(unittest.TestCase):
#    def test_loginPage(self):
#        driver = webdriver.Firefox()
#        driver.get("http://localhost:8080/")



if __name__ == "__main__":
    unittest.main()
