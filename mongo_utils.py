from pymongo import MongoClient
from config import mongo_host, mongo_port, mongo_user, mongo_password, mongo_db_name
from logging_utils import log_error, log_success, log_info
from yunohost_utils import fetch_yunohost_users, get_user_timestamp
import datetime
from datetime import timedelta

client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/?directConnection=true&serverSelectionTimeoutMS=2000&authSource=blahajusers&appName=mongosh+2.3.2")
db = client[mongo_db_name]
users_collection = db['users']
reset_tokens_collection = db['reset_tokens']
websites_collection = db['websites']
makesite_tokens_collection = db['makesite_tokens']

def load_users_from_db():
    users = []
    try:
        users = list(users_collection.find())
    except Exception as e:
        log_error(f"Error loading users from DB: {e}")
    return users

def save_user_to_db(user_data):
    try:
        log_info(f"Attempting to save user to DB: {user_data}")
        result = users_collection.insert_one(user_data)
        if result.acknowledged:
            log_success(f"User {user_data['Username']} saved to DB.")
            return True
        else:
            log_error(f"Failed to save user {user_data['Username']} to DB.")
            return False
    except Exception as e:
        log_error(f"Error saving user to DB: {e}")
        return False

def update_db_with_yunohost_users(yunohost_users):
    existing_users = set(user['Username'] for user in load_users_from_db())
    for username, user_info in yunohost_users.items():
        if username not in existing_users:
            user_data = {
                'Username': username,
                'DisplayName': user_info['fullname'],
                'RecoveryEmail': user_info['mail'],
                'DiscordID': '000000000000000000',
                'Timestamp': get_user_timestamp(username),
                'Tier': 'Starter'
            }
            save_user_to_db(user_data)
    log_success("Database updated with YunoHost users.")

def fetch_db_users():
    return load_users_from_db()

def remove_user_from_db(username):
    try:
        users_collection.delete_one({'Username': username})
        log_success(f"User {username} removed from database.")
    except Exception as e:
        log_error(f"Error removing user from DB: {e}")

def get_all_users(verbose=False):
    if verbose:
        log_info("Fetching all users from database")
    db_users = fetch_db_users()
    yunohost_users = fetch_yunohost_users()
    all_users = db_users + [{'Username': username} for username in yunohost_users]
    unique_users = []
    seen_usernames = set()
    for user in all_users:
        username = user.get('Username')
        if username not in seen_usernames:
            unique_users.append(user)
            seen_usernames.add(username)
    return unique_users

def fetch_user_by_username(username):
    try:
        log_info(f"Fetching user by username: {username}")
        user = users_collection.find_one({'Username': username})
        if user:
            log_success(f"User {username} found.")
        else:
            log_error(f"User {username} not found.")
        return user
    except Exception as e:
        log_error(f"Error fetching user by username: {e}")
        return None
    
def store_reset_token(username, token):
    try:
        expiry_time = datetime.datetime.utcnow() + timedelta(hours=2)
        log_info(f"Storing reset token for user: {username}, expiry: {expiry_time}")
        reset_tokens_collection.insert_one({
            'Username': username,
            'Token': token,
            'Expiry': expiry_time
        })
        log_success(f"Reset token stored for {username}.")
    except Exception as e:
        log_error(f"Error storing reset token for {username}: {e}")

def fetch_reset_token(token):
    try:
        log_info(f"Fetching reset token data for token: {token}")
        token_data = reset_tokens_collection.find_one({'Token': token})
        if token_data:
            log_success(f"Reset token data found for token: {token}")
            return token_data
        else:
            log_error(f"No reset token data found for token: {token}")
            return None
    except Exception as e:
        log_error(f"Error fetching reset token data for token: {token}: {e}")
        return None
    
def store_makesite_token(username, token, domain, git_url, sftp_access, expiry_time, ssg):
    try:
        log_info(f"Storing makesite token for user: {username}, expiry: {expiry_time}")
        makesite_tokens_collection.insert_one({
            'Username': username,
            'Token': token,
            'Domain': domain,
            'GitURL': git_url,
            'SftpAccess': sftp_access,
            'Expiry': expiry_time,
            'SSG': ssg,
        })
        log_success(f"Makesite token stored for {username}.")
    except Exception as e:
        log_error(f"Error storing makesite token for {username}: {e}")

def fetch_makesite_token(token):
    try:
        log_info(f"Fetching makesite token data for token: {token}")
        token_data = makesite_tokens_collection.find_one({'Token': token})
        if token_data:
            log_success(f"Makesite token data found for token: {token}")
            return token_data
        else:
            log_error(f"No makesite token data found for token: {token}")
            return None
    except Exception as e:
        log_error(f"Error fetching makesite token data for token: {token}: {e}")
        return None

def store_website_details(username, domain, git_url, sftp_access, ssg, timestamp):
    try:
        website_info = {
            'Username': username,
            'Domain': domain,
            'GitURL': git_url,
            'SftpAccess': sftp_access,
            'SSG': ssg,
            'Timestamp': timestamp
        }
        
        websites_collection.insert_one(website_info)
        log_success(f"Website details stored for {username}.")
    except Exception as e:
        log_error(f"Error storing website details for {username}: {e}")


def insert_recovery_emails_and_user_ids(data, verbose=False):
    entries = data.split(',')
    for entry in entries:
        parts = entry.strip().split('-')
        if len(parts) != 3:
            log_error(f"Invalid format for entry: {entry}")
            continue
        username, email, user_id = parts
        try:
            log_info(f"Inserting: Username={username}, Email={email}, UserID={user_id}")
            result = users_collection.update_one(
                {'Username': username},
                {'$set': {'RecoveryEmail': email, 'DiscordID': user_id}},
                upsert=True
            )
            if result.matched_count > 0:
                log_success(f"Updated user {username} with RecoveryEmail={email} and DiscordID={user_id}.")
            elif result.upserted_id is not None:
                log_success(f"Inserted new user {username} with RecoveryEmail={email} and DiscordID={user_id}.")
            else:
                log_error(f"Failed to insert or update user {username}.")
        except Exception as e:
            log_error(f"Error inserting/updating user {username}: {e}")