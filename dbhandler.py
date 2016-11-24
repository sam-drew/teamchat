import pymysql

connection = pymysql.connect(host = "host",
                             user = "user",
                             password = "password",
                             db = "db",
                             charset = "utf8mb4",
                             cursorclass = pymysql.cursors.DictCursor)
