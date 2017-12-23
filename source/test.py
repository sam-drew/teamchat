import unittest
from selenium import webdriver
import pymysql
import time

import dbhandler

class TestDBHandler(unittest.TestCase):
    # Function 'makeConnection()' is tested by proxy throughit's use in all
    # other functions being tested.
    def test_CheckEmail(self):
        self.assertEqual(1, dbhandler.checkEmail("james@email.com"))

    def test_GetLogin(self):
        self.assertEqual({'password': "$2b$12$7DO/OjbCh7SBdzBkhgfXD.DcL3GbqzxOROdTSrjQDCJvKjbmLWJwy",
                        'salt': "$2b$12$7DO/OjbCh7SBdzBkhgfXD."}, dbhandler.getLogin("james@email.com"))

    def test_checkAdmin(self):
        self.assertTrue(dbhandler.checkAdmin(1))
        self.assertFalse(dbhandler.checkAdmin(2))

    def test_getUserName(self):
        self.assertEqual("james", dbhandler.getUserName(2)['name'])
        self.assertEqual("janet", dbhandler.getUserName(5)['name'])

    def test_getChatName(self):
        self.assertEqual("finance", dbhandler.getChatName(1)['name'])
        self.assertEqual("legal", dbhandler.getChatName(2)['name'])

    def test_getMemberIDs(self):
        ids = dbhandler.getMemberIDs(2)
        self.assertEqual(5, ids[0])

    def test_getUserID(self):
        self.assertEqual(4, dbhandler.getUserID("jane@email.com")['ID'])

    def test_getChats(self):
        chats = dbhandler.getChats(1)
        self.assertEqual('finance', chats[0]['name'])
        self.assertEqual('admin', chats[1]['name'])

    def test_getChatNameID(self):
        chats = dbhandler.getChats(1)
        self.assertEqual('finance', chats[0]['name'])
        self.assertEqual('admin', chats[1]['name'])

    def test_checkChatPrivileges(self):
        self.assertFalse(dbhandler.checkChatPrivileges(1, 2))
        self.assertEqual(2, dbhandler.checkChatPrivileges(1, 1)['ID'])

    def test_checkChatAdmin(self):
        self.assertTrue(dbhandler.checkChatAdmin(1, 1))
        self.assertFalse(dbhandler.checkChatAdmin(2, 4))

    def test_getUserNameFromID(self):
        self.assertEqual('james', dbhandler.getUserNameFromID(1)['name'])

    def test_getChatNameID(self):
        info = dbhandler.getChatNameID("james@email.com")
        self.assertEqual(1, info[0]['ID'])
        self.assertEqual('admin', info[1]['name'])

    def test_getRecentMessages(self):
        messages = dbhandler.getRecentMessages(2)
        self.assertEqual('TEST', messages[0]['content'])
        self.assertEqual(3, messages[0]['ID'])

    #FUNCTIONS THAT SET / SAVE DATA.

    def test_setUserInfo(self):
        email = "TEST@TESTEMAIL.COM"
        name = "TESTNAME"
        password = "$2b$12$IB/erL6YpE48btg6pQnDF.8WhCE4x4qw0YppmfD1L3w4XdJsI.xFW"
        salt = "$2b$12$IB/erL6YpE48btg6pQnDF."
        dbhandler.setUserInfo(email, name, password, salt)
        self.assertEqual(1, dbhandler.checkEmail(email))
        info = dbhandler.getLogin(email)
        self.assertEqual(info['password'], password)
        self.assertEqual(info['salt'], salt)
        ID = dbhandler.getUserID(email)['ID']
        self.assertEqual(name, dbhandler.getUserNameFromID(ID)['name'])
        # Clean up the mess made here ^
        connection = dbhandler.makeConnection()
        try:
            with connection.cursor() as cursor:
                sql = ("DELETE FROM users WHERE email = '{0}'")
                cursor.execute(sql.format(email))
            connection.commit()
        except Exception as e:
            return("Error: {0}. Error code is {1}".format(e, e.args[0]))
        finally:
            connection.close()

    def test_setMessage(self):
        messageID = dbhandler.setMessage(1, 1, "TEST_MESSAGE")
        returnMessages = dbhandler.getRecentMessages(1)
        message = returnMessages[0]
        self.assertEqual("TEST_MESSAGE", message['content'])
        # Clean up the mess made here ^
        connection = dbhandler.makeConnection()
        try:
            with connection.cursor() as cursor:
                sql = ("DELETE FROM messages WHERE ID = {0}")
                cursor.execute(sql.format(messageID))
            connection.commit()
        except Exception as e:
            return("Error: {0}. Error code is {1}".format(e, e.args[0]))
        finally:
            connection.close()

    def test_addNewUser(self):
        email = "TEST@TESTEMAIL.COM"
        name = "TESTNAME"
        password = "$2b$12$IB/erL6YpE48btg6pQnDF.8WhCE4x4qw0YppmfD1L3w4XdJsI.xFW"
        salt = "$2b$12$IB/erL6YpE48btg6pQnDF."
        userIDAdmin = 1
        self.assertTrue(dbhandler.addNewUser(userIDAdmin, email, name, password, salt))
        self.assertEqual(1, dbhandler.checkEmail(email))
        info = dbhandler.getLogin(email)
        self.assertEqual(info['password'], password)
        self.assertEqual(info['salt'], salt)
        ID = dbhandler.getUserID(email)['ID']
        self.assertEqual(name, dbhandler.getUserNameFromID(ID)['name'])

        userID = 2
        self.assertFalse(dbhandler.addNewUser(userID, email, name, password, salt))
        # Clean up the mess made here ^
        connection = dbhandler.makeConnection()
        try:
            with connection.cursor() as cursor:
                sql = ("DELETE FROM users WHERE email = '{0}'")
                cursor.execute(sql.format(email))
            connection.commit()
        except Exception as e:
            return("Error: {0}. Error code is {1}".format(e, e.args[0]))
        finally:
            connection.close()

    def test_addNewChat(self):
        name = "TESTCHAT"
        chatID = dbhandler.addNewChat(name)
        self.assertEqual(name, dbhandler.getChatName(chatID)['name'])
        # Clean up mess
        connection = dbhandler.makeConnection()
        try:
            with connection.cursor() as cursor:
                sql = ("DELETE FROM chats WHERE ID = {0}")
                cursor.execute(sql.format(chatID))
            connection.commit()
        except Exception as e:
            return("Error: {0}. Error code is {1}".format(e, e.args[0]))
        finally:
            connection.close()

    def test_setPrivileges(self):
        userID = 4
        chats = {2: False,}
        dbhandler.setPrivileges(userID, chats)
        self.assertTrue(isinstance(dbhandler.checkChatPrivileges(userID, 2)['ID'], int))
        # Clean up mess
        connection = dbhandler.makeConnection()
        try:
            with connection.cursor() as cursor:
                sql = ("DELETE FROM members WHERE userID = 4 AND chatID = 2")
                cursor.execute(sql)
            connection.commit()
        except Exception as e:
            return("Error: {0}. Error code is {1}".format(e, e.args[0]))
        finally:
            connection.close()

class TestUI(unittest.TestCase):

    def test_indexPage(self):
        self.maxDiff = None
        # Read the file into a single string
        template = open("templates/index.html")
        html = template.read()
        template.close()
        html = html.replace('\n', '')
        html = html.replace(' ', '')
        html = html.replace('<!DOCTYPEhtml>', '')
        # Initialise the browser using selenium
        driver = webdriver.Firefox()
        driver.get("http://localhost:8080/")
        source = driver.page_source
        driver.quit()
        source = source.replace('\n', '')
        source = source.replace(' ', '')
        # Test equal
        self.assertEqual(html, source)


    def test_loginPageSource(self):
        self.maxDiff = None
        # Read the file into a single string
        template = open("templates/login.html")
        html = template.read()
        template.close()
        html = html.replace('\n', '')
        html = html.replace(' ', '')
        html = html.replace('<!DOCTYPEhtml>', '')
        # Initialise the browser using selenium
        driver = webdriver.Firefox()
        driver.get("http://localhost:8080/login")
        source = driver.page_source
        driver.quit()
        source = source.replace('\n', '')
        source = source.replace(' ', '')
        # Test equal
        self.assertEqual(html, source)

    def test_loginPageAction(self):
        # Init the browser
        driver = webdriver.Firefox()
        driver.get("http://localhost:8080/login")
        # Find the form elements and send information to them
        emailInput = driver.find_element_by_id("emailInput")
        emailInput.send_keys("james@email.com")
        passwordInput = driver.find_element_by_id("passwordInput")
        passwordInput.send_keys("password")
        submitButton = driver.find_element_by_id("submit")
        submitButton.click()
        time.sleep(10)
        self.assertEqual(driver.current_url, "http://localhost:8080/home")
        driver.quit()

    def test_chatPageSource(self):
        # Init the browser
        driver = webdriver.Firefox()
        driver.get("http://localhost:8080/login")
        # Find the form elements and send information to them
        emailInput = driver.find_element_by_id("emailInput")
        emailInput.send_keys("james@email.com")
        passwordInput = driver.find_element_by_id("passwordInput")
        passwordInput.send_keys("password")
        submitButton = driver.find_element_by_id("submit")
        submitButton.click()
        time.sleep(10)
        driver.get("http://localhost:8080/chat/1")
        source = driver.page_source
        driver.quit()
        source = source.replace('\n', '')
        source = source.replace(' ', '')
        # Get the template source
        template = open("templates/chatAdmin.html")
        html = template.read()
        template.close()
        html = html.replace('\n', '')
        html = html.replace(' ', '')
        html = html.replace('<!DOCTYPEhtml>', '')
        # Test equal
        self.assertEqual(html, source)

    def test_sendMessageAction(self):
        # Initialise two browser windows, and login with different accounts.
        browser1 = webdriver.Firefox()
        browser2 = webdriver.Firefox()
        # Log browser1 into chatID 1 with userID 1.
        browser1.get("http://localhost:8080/login")
        emailInput = browser1.find_element_by_id("emailInput")
        emailInput.send_keys("james@email.com")
        passwordInput = browser1.find_element_by_id("passwordInput")
        passwordInput.send_keys("password")
        submitButton = browser1.find_element_by_id("submit")
        submitButton.click()
        time.sleep(10)
        browser1.get("http://localhost:8080/chat/1")
        # Log browser2 into chatID 1 with userID 2.
        browser1.get("http://localhost:8080/login")
        emailInput = browser2.find_element_by_id("emailInput")
        emailInput.send_keys("jack@email.com")
        passwordInput = browser2.find_element_by_id("passwordInput")
        passwordInput.send_keys("password")
        submitButton = browser2.find_element_by_id("submit")
        submitButton.click()
        time.sleep(10)
        browser2.get("http://localhost:8080/chat/1")
        # Check the original source of both chats as rendered.
        b1OriginalHTML = browser1.page_source
        b2OriginalHTML = browser2.page_source
        # Send a message
        messageInput = browser1.find_element_by_id("message")
        messageInput.send_keys("TEST_MESSAGE")
        messageInput.send_keys(Keys.RETURN)
        time.sleep(5)
        b1NewHTML = browser1.page_source
        b2NewHTML = browser2.page_source
        self.assertFalse(b1OriginalHTML == b1NewHTML)
        self.assertFalse(b2OriginalHTML == b2NewHTML)

if __name__ == "__main__":
    unittest.main()
