import mysql.connector
import app


# Function to send messages
def send_message(avail_class, ch, db, cursor):
    message = input("Enter the message: ")
    query = f"INSERT INTO {avail_class[ch-1]}_MESSAGES (message) VALUES(%s)"
    cursor.execute(query, (message,))
    db.commit()
    db.close()


# Function to receive messages
def get_message(avail_class, ch, db, cursor):
    query=f"SELECT * FROM {avail_class[ch-1]}_MESSAGES"
    cursor.execute(query)
    for i in cursor:
        print(f"{i[0]}. {i[1]} (Created on {i[2].day}/{i[2].month}/{i[2].year} at {i[2].hour}:{i[2].minute}:{i[2].second})")
    db.close()


# Function to check role of user
def check_role(avail_class, role, db, cursor):
    ch=int(input("Enter S.No. of the class: "))
    if role[0] == "TEACHER":
        menu=int(input("What would you like to do:\n1.Send messages\n2.See messages\n(Enter the S.No. corresponding to the option): "))
        if menu==1:
            send_message(avail_class, ch, db, cursor)
        elif menu==2:
            get_message(avail_class, ch, db, cursor)

    elif role[0] == "STUDENT":
        get_message(avail_class, ch, db, cursor)


# Function to check the available classes for a user
def check_classes(db, cursor):
    avail_class=[]
    cursor.execute(f"SELECT ROLE FROM USERS WHERE UID={uid}")
    role=cursor.fetchone()
    print(f"Logged In Successfully as {role[0]}!")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for (table_name,) in tables:
        if table_name.endswith("_MESSAGES") or table_name=="USERS":
            continue
        else:
            query = f"SELECT '{table_name}' AS table_name FROM {table_name} WHERE UID = {uid}"
            cursor.execute(query)
            result = cursor.fetchall()
            if result:
                avail_class.append(result[0][0])
    print("Available Classes:")
    for index, myclass in enumerate(avail_class):
        print(f"{index+1}. {myclass}")
    check_role(avail_class, role, db, cursor)


# Function to check whether a user is valid or not
def check_user(uid, upass):
    db=create_connection()
    cursor=db.cursor()
    valid_user = False
    cursor.execute("SELECT * FROM USERS")
    for i in cursor:
        if uid in i and upass in i:
            valid_user=True
    if valid_user:
        check_classes(db, cursor)
    else:
        print("invalid User ID or Password!")

      
# Function to establish a connection with MySQL database
def create_connection():
    return mysql.connector.connect(host="localhost", user="root", password="mysql.pass", database="mydatabase")


# Main Loop
while True:
    print("WELCOME TO EDUNET")
    uid=input("Enter your User ID: ")
    upass=input("Enter your password: ")
    check_user(uid, upass)
    ch=input("Would you like to continue(Y/N): ")
    if ch.upper()=='N':
        print("Thanks for using EDUNET")
        break







