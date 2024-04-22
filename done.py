import hashlib
import emaRSI  # Assuming emaRSI is a custom module containing get_trade_details function

def read_password_hash(file_path):
    """Reads the hashed password from a file."""
    try:
        with open(file_path, "r") as file:
            hashed_password = file.readline().strip()
            return hashed_password
    except FileNotFoundError:
        return None

def set_and_save_password(password, file_path):
    """Sets and saves the hashed password to a file."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with open(file_path, "w") as file:
        file.write(password_hash)

def authenticate_user(hashed_password):
    """Authenticates the user based on the hashed password."""
    user_password = input("Enter the password: ")
    user_password_hash = hashlib.sha256(user_password.encode()).hexdigest()
    return user_password_hash == hashed_password

def main():
    PASSWORD_FILE = "password.txt"

    # Check if a password is already set
    hashed_password = read_password_hash(PASSWORD_FILE)
    if hashed_password:
        # Password is set, prompt for authentication
        if authenticate_user(hashed_password):
            print("Password accepted. Proceeding with program execution...")
            emaRSI.get_trade_details()
        else:
            print("Incorrect password. Exiting program.")
    else:
        # No password is set, prompt for setting a new password
        while True:
            password = input("Set a password: ")
            password_confirm = input("Confirm password: ")
            if password == password_confirm:
                set_and_save_password(password, PASSWORD_FILE)
                print("Password set. Proceeding with program execution...")
                emaRSI.get_trade_details()
                break
            else:
                print("Passwords do not match. Please try again.")

if __name__ == "__main__":
    main()
