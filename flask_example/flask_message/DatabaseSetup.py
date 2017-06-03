import sqlite3


users = sqlite3.connect("users").cursor()
message = sqlite3.connect("message").cursor()

users.execute("CREATE TABLE USER(")


