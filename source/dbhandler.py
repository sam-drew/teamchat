import pymysql
import yaml

# Take the 'setUserInfo' function as the example code structure (with comments) for
# all connections using PyMySQL, with regard to asigning cursors etc.

# Function to make connection to the database. Reads the parameters out of a
# configuration file. Returns the connection object for use by other functions.
def makeConnection():
    with open("dbconfig.yaml", 'r') as stream:
        try:
            config = yaml.load(stream)
            connection = pymysql.connect(host = config['MySQL']['hostname'],
                                        user = config['MySQL']['user'],
                                        password = config['MySQL']['password'],
                                        db = config['MySQL']['database'],
                                        charset = "utf8mb4",
                                        cursorclass = pymysql.cursors.DictCursor)
            return(connection)
        except Exception as e:
            return("Error: {0}".format(e))

# Function to set user information
def setUserInfo(email, name, password, salt):
    connection = makeConnection()
    try:
        # Initialise the cursor, which is used to perform tasks on the DB
        with connection.cursor() as cursor:
            # Insert new record, ID is blank as is self incrementing
            sql = ("INSERT INTO users (email, name, password, salt) VALUES ('{0}', '{1}', '{2}', '{3}')")
            cursor.execute(sql.format(email, name, password, salt))
        # Commit the changes made to the DB
        connection.commit()
    # Handle any errors on MySQL's part
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if the new sign-up's email is already in use, returns False
# if not in use
def checkEmail(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT email FROM users WHERE email = '{0}'")
            return(cursor.execute(sql.format(email)))
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the login information of a given account
def getLogin(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT password, salt FROM users WHERE email = '{0}'")
            returnValue = cursor.execute(sql.format(email))
            if returnValue == True:
                results = cursor.fetchone()
                return(results)
            else:
                return(False)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to set a new message in the database
def setMessage(userID, chatID, content):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            # Get the memberID of the related user and chat
            memberID = checkChatPrivileges(userID, chatID)
            if memberID != False:
                # Insert new entry into the messages table with the memberID and message content
                sql = ("INSERT INTO messages (content, memberID) VALUES ('{0}', {1})")
                cursor.execute(sql.format(content, memberID['ID']))
                lastID = connection.insert_id()
            else:
                return(False)
        connection.commit()
        return(lastID)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to set user privileges. Input user will be the userID, Input
# chats will be a dict defined as chatID: admin? where admin is boolean
def setPrivileges(userID, chats):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            # Iterate over the keys in the dict
            for chatID in chats:
                # If the key's value is True (i.e. they are admin of that chat),
                # insert a record to reflect this, else omit 'admin' value.
                if checkChatPrivileges(userID, chatID) == False:
                    if chats[chatID] == True:
                        sql = ("INSERT INTO members (chatID, userID, admin) VALUES ('{0}', '{1}', '{2}')")
                        cursor.execute(sql.format(chatID, userID, 1))
                    else:
                        sql = ("INSERT INTO members (chatID, userID) VALUES ('{0}', '{1}')")
                        cursor.execute(sql.format(chatID, userID))
                else:
                    return(False)
        connection.commit()
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if a user has admin privileges, returns True if true
def checkAdmin(userID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT admin FROM members WHERE userID = {0}")
            cursor.execute(sql.format(userID))
            result = cursor.fetchall()
            admin = False
            for r in result:
                if r['admin'] == 1:
                    admin = True
            return(admin)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if a user has the the correct privileges to message a chat
def checkChatPrivileges(userID, chatID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT ID FROM members WHERE userID = '{0}' AND chatID = '{1}'")
            cursor.execute(sql.format(userID, chatID))
            if cursor != False:
                returnVal = cursor.fetchone()
                if returnVal == None:
                    return(False)
                else:
                    return(returnVal)
            else:
                return(False)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if the specified user of a chat is an admin of that chat.
def checkChatAdmin(userID, chatID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT admin FROM members WHERE userID = '{0}' AND chatID = '{1}'")
            cursor.execute(sql.format(userID, chatID))
            isAdmin = cursor.fetchone()
            if isAdmin == None:
                return(False)
            elif isAdmin['admin'] == 1:
                return(True)
            else:
                return("ERROR: dbhandler.checkChatAdmin returned an incorrect value")
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get a user's name by their memberID
def getUserName(memberID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT users.name FROM users INNER JOIN members ON members.userID = users.ID WHERE members.ID = '{0}'")
            cursor.execute(sql.format(memberID))
            name = cursor.fetchone()
            return(name)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get a users name from their userID
def getUserNameFromID(userID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT name FROM users WHERE ID = {0}")
            cursor.execute(sql.format(userID))
            name = cursor.fetchone()
            return(name)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the name of a chat
def getChatName(chatID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT name FROM chats WHERE ID = '{0}'")
            cursor.execute(sql.format(chatID))
            name = cursor.fetchone()
            return(name)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the all the memberID's associated with a chat
def getMemberIDs(chatID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT ID FROM members WHERE chatID = '{0}'")
            cursor.execute(sql.format(chatID))
            memberIDs = cursor.fetchall()
            memberIDList = []
            for i in memberIDs:
                memberIDList.append(i['ID'])
            return(memberIDList)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the userID of a given email address
def getUserID(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT ID FROM users WHERE email = '{0}'")
            cursor.execute(sql.format(email))
            userID = cursor.fetchone()
            return(userID)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

def getChats(userID):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT chats.name, chats.ID FROM chats INNER JOIN members ON chats.ID = members.chatID WHERE userID = {0}")
            cursor.execute(sql.format(userID))
            return(cursor.fetchall())
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

def getChatNameID(email):
    connection = makeConnection()
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT chats.name, chats.ID FROM chats INNER JOIN members ON chats.ID = members.chatID INNER JOIN users ON users.ID = members.userID WHERE users.email = '{0}'")
            cursor.execute(sql.format(email))
            return(cursor.fetchall())
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to return the last n messages sent in a chat
def getRecentMessages(chatID):
    try:
        connection = makeConnection()
        with connection.cursor() as cursor:
            # Get all the memberID's associated with that chat, to
            # search the table for all messages to that chat
            allMembers = str(getMemberIDs(chatID))
            # Select the 25 most recent entries to the table where the
            # memberID is of allMembers list
            sql = ("SELECT ID, content, ts, memberID FROM messages WHERE memberID IN ({0}) ORDER BY ID DESC LIMIT 25")
            cursor.execute((sql.format(allMembers).replace("[", "").replace("]", "")))
            messages = cursor.fetchall()
            if messages != ():
                return(messages)
            else:
                return(False)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to add new user to database
def addNewUser(userID, email, name, password, salt):
    try:
        isAdmin = checkAdmin(userID)
        if isAdmin == True:
            setUserInfo(email, name, password, salt)
            return(True)
        else:
            return(isAdmin)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))

# Function to add a new chat to the database.
def addNewChat(name):
    try:
        connection = makeConnection()
        with connection.cursor() as cursor:
            sql = ("INSERT INTO chats (name) VALUES ('{0}')")
            cursor.execute(sql.format(name))
        connection.commit()
        with connection.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            chatID = cursor.fetchone()['LAST_INSERT_ID()']
            return(chatID)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()
