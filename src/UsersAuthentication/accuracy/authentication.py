from src.UsersAuthentication.database.storage_users import MongoDB

db = MongoDB('mongodb://localhost:27017/')
def accurate():

    while True:
        token = input("Token: ")
        user = db.get_by_token(token)
        if user['token'] == token:
            print(user)
            break
        else:
            print("cannot signin")
