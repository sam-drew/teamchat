import pymysql

# Take the 'addUser' function as the example code structure (with comments) for
# all connections using PyMySQL, with regard to asigning cursors etc.

# Initialise the connection with the DB
try:
    connection = None
    connection = pymysql.connect(host = "host",
                                user = "user",
                                password = "password",
                                db = "db",
                                charset = "utf8mb4",
                                cursorclass = pymysql.cursors.DictCursor)
except MySQLError as e:
    return("Error: {0}. Error code is {1}".format(e, e.args[0]))

# Function to set user information
def setUserInfo(email, name, password, salt):
    try:
        # Initialise the cursor, which is used to perform tasks on the DB
        with connection.cursor() as cursor:
            # Insert new record, ID is blank as is self incrementing
            sql = ("INSERT INTO 'users' ('email', 'name', 'password', 'salt') VALUES ({0}, {1}, {2}, {3})")
            cursor.execute(sql.format(email, name, password, salt))
        # Commit the changes made to the DB
        connection.commit()
    # Handle any errors on MySQL's part
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if the new sign-up's email is already in use, returns False
# if not in use
def checkEmail(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'email' FROM 'users' WHERE 'email' = {0}")
            return(not(cursor.execute(sql.format(email))))
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the login information of a given account
def getLogin(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'password', 'salt' FROM 'users' WHERE 'email' = {0}")
            returnValue = cursor.execute(sql.format(email))
            if returnValue == True:
                results = cursor.fetchone()
                return(results)
            else:
                return(False)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to set a new message in the database
def setMessage(userID, chatID, content):
    try:
        with connection.cursor() as cursor:
            # Get the memberID of the related user and chat
            memberID = checkChatPrivileges(userID, chatID)
            if memberID != False:
                # Insert new entry into the messages table with the memberID and message content
                sql = ("INSERT INTO 'messages' ('content', 'memberID') VALUES ({0}, {1})")
                cursor.execute(sql.format(content, memberID))
            else:
                return(False)
        connection.commit()
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to set user privileges. Input user will be the userID, Input
# chats will be a dict defined as chatID: admin? where admin is boolean
def setPrivileges(userID, chats):
    try:
        with connection.cursor() as cursor:
            # Iterate over the keys in the dict
            for chatID in chats:
                # If the key's value is True (i.e. they are admin of that chat),
                # insert a record to reflect this, else omit 'admin' value
                if chats[chatID] == True:
                    sql = ("INSERT INTO 'members' ('chatID', 'userID', 'admin') VALUES ({0}, {1}, {2})")
                    cursor.execute(sql.format(chatID, userID, True))
                else:
                    sql = ("INSERT INTO 'members' ('chatID', 'userID') VALUES ({0}, {1})")
                    cursor.execute(sql.format(chatID, userID))
        connection.commit()
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if a user has admin privileges, returns True if true
def checkAdmin(userID):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'admin' FROM 'members' WHERE 'userID' = {0}")
            cursor.execute(sql.format(userID, chatID))
            result = cursor.fetchall()
            return(result)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if a user has the the correct privileges to message a chat
def checkChatPrivileges(userID, chatID):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'ID' FROM 'members' WHERE 'userID' = {0} AND 'chatID' = {1}")
            cursor.execute(sql.format(userID, chatID))
            if cursor != False:
                return(cursor.fetchone())
            else:
                return(False)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get a user's name by their userID
def getUserName(userID):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'name' FROM 'users' WHERE 'ID' = {0}")
            cursor.execute(sql.format(userID))
            name = cursor.fetchone()
            return(name)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the name of a chat
def getChatName(chatID):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'name' FROM 'chats' WHERE 'ID' = {0}")
            cursor.execute(sql.format(chatID))
            name = cursor.fetchone()
            return(name)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the all the memberID's associated with a chat
def getMemberIDs(chatID):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'ID' FROM 'members' WHERE 'chatID' = {0}")
            cursor.execute(sql.format(chatID))
            memberIDs = cursor.fetchall()
            return(memberIDs)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the userID of a given email address
def getUserID(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'ID' FROM 'users' WHERE 'email' = {0}")
            cursor.execute(sql.format(email))
            userID = cursor.fetchone()
            return(userID)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to return the last n messages sent in a chat
def getRecentMessages(chatID, userID):
    try:
        # Use checkChatPrivileges to see if user is allowed to access specified chat
        memberID = checkChatPrivileges(userID, chatID)
        if memberID != False:
            try:
                with connection.cursor() as cursor:
                    # Get all the memberID's associated with that chat, to
                    # search the table for all messages to that chat
                    allMembers = getMemberIDs(chatID)
                    # Select the 25 most recent entries to the table where the
                    # memberID is of allMembers list
                    sql = ("SELECT 'ID', 'content', 'ts', 'memberID' FROM 'messages' WHERE 'memberID' = {0} ORDER BY 'ID' DESC LIMIT 25")
                    cursor.execute((sql.format(allMembers).replace("[", "").replace("]", "")))
                    messages = cursor.fetchall()
                    return(messages)
            except MySQLError as e:
                return("Error: {0}. Error code is {1}".format(e, e.args[0]))
            finally:
                connection.close()
        else:
            return(False)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))

# Function to add new user to database
def addNewUser(userID, email, name, password, salt, chats):
    try:
        chatPrivs = checkChatPrivileges(userID, chatID)
        if chatPrivs != False:
            isAdmin = checkAdmin(userID)
            if isAdmin == True:
                setUserInfo(email, name, password, salt)
                if len(chats) > 0:
                    newUserID = getUserID(email)
                    setPrivileges(newUserID, chats)
                else:
                    return("No chats specified, user is a member of 0 chats")
            else:
                return(isAdmin)
        else:
            return(chatPrivs)
    except Exception as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
