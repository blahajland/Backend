import time
import random
import string
import re
from logging_utils import log_success, log_error, log_warning, log_info
from yunohost_utils import retry_command_until_success, fetch_yunohost_users, fetch_and_print_users_csv_for_list
from mongo_utils import save_user_to_db, get_all_users, remove_user_from_db, load_users_from_db, update_db_with_yunohost_users, insert_recovery_emails_and_user_ids
from email_utils import send_recovery_email
import sys
import termios
import tty
import subprocess
import shlex
import html

USERNAME_REGEX = r"^[a-z0-9_.]+$"
DISPLAY_NAME_REGEX = r"^([^\W_]{1,30}[ ,.'-]{0,3})+$"
SAFE_PASSWORD_CHARS = string.ascii_letters + string.digits + "!#$%()*+,-./=?@[]^_~"

def generate_password(length=16):
    return ''.join(random.choice(SAFE_PASSWORD_CHARS) for _ in range(length))

def sanitize_input(input_str):
    sanitized_str = html.escape(input_str)
    return sanitized_str

def validate_input(username, display_name):
    username = sanitize_input(username)
    display_name = sanitize_input(display_name)
    
    if len(username) > 30 or len(display_name) > 30:
        log_error("Input too long.")
        return False
    
    if not re.match(USERNAME_REGEX, username):
        log_error("Invalid username format.")
        return False
    if not re.match(DISPLAY_NAME_REGEX, display_name):
        log_error("Invalid display name format.")
        return False
    
    return True

def create_user(username, display_name, recovery_email, discord_id=None, verbose=False):
    if not validate_input(username, display_name):
        log_error("Invalid input")
        return False

    password = generate_password()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    command = f'yunohost user create {username} -F "{display_name}" -p "{password}" -d blahaj.land -q 500M'
    log_info(f"Running command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if verbose:
            log_info(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        log_error(e.stderr.decode())
        log_error("Failed to run command to create user")
        return False

    user_data = {
        'Username': username,
        'DisplayName': display_name,
        'RecoveryEmail': recovery_email,
        'DiscordID': discord_id or '',
        'Timestamp': timestamp
    }
    log_info(f"Attempting to save user to DB: {user_data}")
    if not save_user_to_db(user_data):
        log_error("Failed to save user to database")
        return False

    send_recovery_email(recovery_email, username, password)
    log_success(f"User {username} created successfully.")
    return True

def reset_password(username, verbose=False):
    all_users = get_all_users(verbose)
    user = next((user for user in all_users if user['Username'] == username), None)
    if not user:
        log_error(f"User {username} not found.")
        return

    new_password = generate_password()
    command = f"yunohost user update {shlex.quote(username)} -p {shlex.quote(new_password)}"
    log_info(f"Running command: {command}")
    retry_command_until_success(command, verbose)

    if 'RecoveryEmail' in user:
        send_recovery_email(user['RecoveryEmail'], username, new_password)
        log_success(f"Password for user {username} reset successfully.")
    else:
        log_success(f"Password for user {username} reset successfully. No recovery email sent (user not found in DB).")

def reset_password_custom_email(username, custom_email, verbose=False):
    all_users = get_all_users(verbose)
    user = next((user for user in all_users if user['Username'] == username), None)
    if not user:
        log_error(f"User {username} not found.")
        return

    new_password = generate_password()
    command = f"yunohost user update {username} -p {new_password}"
    retry_command_until_success(command, verbose)
    send_recovery_email(custom_email, username, new_password)
    log_success(f"Password for user {username} reset and sent to {custom_email}.")

def batch_remove_users(usernames, verbose=False):
    log_info(f"Original usernames input: {usernames}")
    usernames = re.split(r'[,\s]+', usernames.strip())
    log_info(f"Parsed usernames: {usernames}")
    
    for username in usernames:
        command = f"yunohost user delete {username}"
        log_info(f"Executing command: {command}")
        try:
            retry_command_until_success(command, verbose)
            log_info(f"Command executed successfully for user: {username}")
        except Exception as e:
            log_error(f"Failed to execute command for user {username}: {e}")
            continue
        
        try:
            log_info(f"Removing user {username} from database")
            remove_user_from_db(username)
            log_success(f"User {username} removed from database successfully.")
        except Exception as e:
            log_error(f"Failed to remove user {username} from database: {e}")
            continue
        
        log_success(f"User {username} removed successfully.")

def list_users(verbose=False):
    command = "yunohost user list --fields username fullname groups --json"
    result = retry_command_until_success(command, verbose)
    
    if verbose:
        print("Raw JSON response:", result)
    
    try:
        parsed_result = json.loads(result)
        if verbose:
            print("Parsed JSON:", parsed_result)
        
        users = parsed_result['users']
        for user in users:
            print(f"{user['username']} {user['fullname']} {','.join(user['groups'])}")
    except (KeyError, TypeError) as e:
        log_error(f"Error parsing JSON response: {e}")
        if verbose:
            print("Parsed JSON:", parsed_result)

def show_all_user_info(verbose=False):
    users = load_users_from_db()
    for user in users:
        print(f"{user['Username']} {user['DisplayName']} {user['RecoveryEmail']} {user['DiscordID']} {user['Timestamp']}")

def show_particular_user_info(usernames, verbose=False):
    usernames = re.split(r'[,\s]+', usernames.strip())
    users = load_users_from_db()
    for user in users:
        if user['Username'] in usernames:
            print(f"{user['Username']} {user['DisplayName']} {user['RecoveryEmail']} {user['DiscordID']} {user['Timestamp']}")


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def main_menu(verbose=False):
    while True:
        print("\n==============================")
        print("🛠️ YunoHost User Manager 🛠️")
        print("==============================")
        print("1. Create new user")
        print("2. Reset user password (to recovery email)")
        print("3. Reset user password (to custom email)")
        print("4. Update Database with YunoHost users")
        print("5. Remove user(s)")
        print("6. List users")
        print("7. Show all user info")
        print("8. Show particular user(s) info")
        print("9. Import recovery email(s)")
        print("10. Insert additional user data")
        print("11. Print CSV for mailing list")
        print("12. Exit")
        print("==============================")

        choice = input("Select an option: ").strip()
        
        if choice == "1":
            username = input("Enter username: ").strip()
            display_name = input("Enter display name: ").strip()
            recovery_email = input("Enter recovery email: ").strip()
            create_user(username, display_name, recovery_email, verbose=verbose)
        elif choice == "2":
            all_users = get_all_users(verbose=verbose)
            usernames = [user['Username'] for user in all_users]
            print("\nAvailable users:")
            for username in usernames:
                print(username)
            username = input("Enter username to reset password for: ").strip()
            reset_password(username, verbose=verbose)
        elif choice == "3":
            all_users = get_all_users(verbose=verbose)
            usernames = [user['Username'] for user in all_users]
            print("\nAvailable users:")
            for username in usernames:
                print(username)
            username = input("Enter username to reset password for: ").strip()
            custom_email = input("Enter the custom email address: ").strip()
            reset_password_custom_email(username, custom_email, verbose=verbose)
        elif choice == "4":
            yunohost_users = fetch_yunohost_users()
            update_db_with_yunohost_users(yunohost_users)
        elif choice == "5":
            usernames = input("Enter usernames to remove (comma or space separated): ").strip()
            batch_remove_users(usernames, verbose=verbose)
        elif choice == "6":
            list_users(verbose=verbose)
        elif choice == "7":
            show_all_user_info(verbose=verbose)
        elif choice == "8":
            usernames = input("Enter usernames to show info for (comma or space separated): ").strip()
            show_particular_user_info(usernames, verbose=verbose)
        elif choice == "9":
            emails = input("Enter recovery emails (username-email, comma or space separated): ").strip()
            import_recovery_emails(emails, verbose=verbose)
        elif choice == "10":
            data = input("Enter data (username-email-userID, comma or space separated): ").strip()
            insert_recovery_emails_and_user_ids(data, verbose=verbose)
        elif choice == "11":
            fetch_and_print_users_csv_for_list()
        elif choice == "12":
            print("Exiting...")
            sys.exit(0)
        else:
            log_warning("Invalid choice.")
        
        print("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YunoHost user manager")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--shell", action="store_true", help="Launch interactive shell")
    args = parser.parse_args()

    if args.shell:
        main_menu(verbose=args.verbose)
    else:
        from flask_app import app
        app.run(debug=True)
