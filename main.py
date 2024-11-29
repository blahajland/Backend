import argparse
import sys
import re
import json
import termios
import tty
from logging_utils import log_info, log_success, log_warning, log_error
from yunohost_utils import retry_command_until_success
from mongo_utils import load_users_from_db, save_user_to_db, update_db_with_yunohost_users, get_all_users, remove_user_from_db
from email_utils import send_recovery_email
from discord_utils import discord_client, start_discord_client_thread

def show_all_user_info(verbose=False):
    command = "yunohost user list --fields username fullname mail-alias mail-forward mailbox-quota groups --json"
    result = retry_command_until_success(command, verbose)
    users = json.loads(result)['users']
    for user in users:
        print(f"{user['username']} {user['fullname']} {','.join(user['mail-alias'])} {','.join(user['mail-forward'])} {user['mailbox-quota']} {','.join(user['groups'])}")

def show_particular_user_info(usernames, verbose=False):
    usernames = re.split(r'[,\s]+', usernames.strip())
    command = f"yunohost user list --fields username fullname mail-alias mail-forward mailbox-quota groups --json"
    result = retry_command_until_success(command, verbose)
    users = json.loads(result)['users']
    for user in users:
        if user['username'] in usernames:
            print(f"{user['username']} {user['fullname']} {','.join(user['mail-alias'])} {','.join(user['mail-forward'])} {user['mailbox-quota']} {','.join(user['groups'])}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YunoHost user manager")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--start", action="store_true", help="Start Flask app and Discord client")
    args = parser.parse_args()

    if args.start:
        from flask_app import app
        from discord_utils import start_discord_client_thread
        start_discord_client_thread()
        app.run(debug=True)
    else:
        from usermanager import main_menu
        main_menu(verbose=args.verbose)