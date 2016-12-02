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

# Function to add new user
def addUser(email, name, password, salt):
    try:
        # Initialise the cursor, which is used to perform tasks on the DB
        with connection.cursor() as cursor:
            # Insert new record, ID is blank as is self incrementing
            sql = "INSERT INTO 'users' ('email', 'name', 'password', 'salt') VALUES ({0}, {1}, {2}, {3})"
            cursor.execute((sql.format(email, name, password, salt)))
        # Commit the changes made to the DB
        connection.commit()
    # Handle any errors on MySQL's part
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to check if the new sign-up's email is already in use
def checkEmail(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'email' FROM 'users' WHERE 'email' = {}")
            return(cursor.execute(sql.format(email)))
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()

# Function to get the login information of a given account
def getLogin(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'password', 'salt' FROM 'users' WHERE 'email' = {}")
            cursor.execute(sql.format(email))
            results = cursor.fetchone()
            return(results)
    except MySQLError as e:
        return("Error: {0}. Error code is {1}".format(e, e.args[0]))
    finally:
        connection.close()
