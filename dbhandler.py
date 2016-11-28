import pymysql

# Initialise the connection with the DB
try:
    connection = pymysql.connect(host = "host",
                                user = "user",
                                password = "password",
                                db = "db",
                                charset = "utf8mb4",
                                cursorclass = pymysql.cursors.DictCursor)
except:
    print("Connection error, check network status, credentials, & dependancies")

# Function to add new user
def addUser(email, name, password, salt):
    try:
        # Initialise the cursor, which is used to perform tasks on the DB
        with connection.cursor() as cursor:
            # Insert new record, ID is blank as is self incrementing
            sql = "INSERT INTO 'users' ('email', 'name', 'password', 'salt') VALUES (%s, %s, %s, %s)"
            cursor.execute((sql % (email, name, password, salt)))
        # Commit the changes made to the DB
        connection.commit()

    # Handle any errors on MySQL's part
    except MySQLError as e:
        return("Error: %s. Error code is %s" % (e, e.args[0]))

    finally:
        connection.close()

# Function to check if the new sign-up's email is already in use
def checkEmail(email):
    try:
        with connection.cursor() as cursor:
            sql = ("SELECT 'email' FROM 'users' WHERE 'email' = %s")
            return(cursor.execute(sql % (email,)))
