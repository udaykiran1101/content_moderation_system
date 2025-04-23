import hashlib
import database

def create_admin_user():
    # Initialize the database
    database.init_db()
    
    # Get admin credentials from user input
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Add the admin user
    if database.add_admin_user(username, password_hash):
        print("Admin user created successfully!")
    else:
        print("Error: Username already exists or database error occurred.")

if __name__ == "__main__":
    create_admin_user() 