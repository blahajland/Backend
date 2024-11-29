from flask import Flask, request, jsonify, redirect, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from logging_utils import log_info, log_error, log_warning
import config
from discord_utils import fetch_discord_id, send_discord_webhook
from usermanager import create_user
from mongo_utils import get_all_users, fetch_user_by_username, store_reset_token, fetch_reset_token, store_makesite_token, fetch_makesite_token, store_website_details, websites_collection
from usermanager import reset_password, generate_password
from email_utils import send_password_reset_email, send_website_setup_email
import secrets
import string
import datetime
from datetime import timedelta
import logging
import subprocess
import os 
import re
from website_utils import sftp_password, create_website, website_index

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.jwt_secret_key
jwt = JWTManager(app)

ALLOWED_GIT_URL_PATTERN = r"^[a-zA-Z0-9./:-]+$"

def validate_git_url(git_url):
    logging.debug(f"Validating Git URL: {git_url}")
    if not isinstance(git_url, str):
        logging.debug(f"Invalid Git URL: {git_url}")
        return None

    if re.match(ALLOWED_GIT_URL_PATTERN, git_url):
        logging.debug(f"URL matches allowed pattern")
        if not git_url.endswith('.git'):
            git_url += '.git'
        return git_url
    else:
        logging.debug(f"URL does not match allowed pattern")
    return None

logging.basicConfig(level=logging.INFO)

# Use user from config
jwt_user = config.jwt_user

def generate_reset_token(length=128):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == jwt_user['username'] and password == jwt_user['password']:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Bad username or password"}), 401

@app.route('/create_user', methods=['POST'])
@jwt_required()
async def create_user_endpoint():
    log_info("Received request to create user")
    
    current_user = get_jwt_identity()
    log_info(f"Authenticated user: {current_user}")

    data = request.get_json()
    log_info(f"Request data: {data}")

    username = data.get('username')
    display_name = data.get('display_name')
    recovery_email = data.get('recovery_email')
    discord_username = data.get('discord_username', None)

    all_users = get_all_users()
    if any(user['Username'] == username for user in all_users):
        log_warning(f"Username {username} is already taken")
        return jsonify({"error": "Username already taken"}), 432

    discord_id = None
    if discord_username:
        log_info(f"Fetching Discord ID for username: {discord_username}")
        discord_id = await fetch_discord_id(discord_username)
        log_info(f"Fetched Discord ID: {discord_id}")

    log_info("Creating user with provided data")
    user_creation_result = create_user(username, display_name, recovery_email, discord_id)
    
    if user_creation_result:
        log_info("User created successfully")
        return jsonify({"message": "User created successfully"}), 201
    else:
        log_error("Failed to create user")
        return jsonify({"error": "Failed to create user"}), 500

@app.route('/request_password_reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    username = data.get('username')
    
    log_info(f"Received password reset request for username: {username}")

    user = fetch_user_by_username(username)
    if not user:
        log_error(f"User {username} not found.")
        return jsonify({"error": "User not found"}), 404

    reset_token = generate_reset_token()
    store_reset_token(username, reset_token)

    reset_link = f"https://backhaj.blahaj.land/reset_password?token={reset_token}"
    
    send_password_reset_email(user['RecoveryEmail'], username, reset_link)
    log_info(reset_link)
    
    log_info(f"Password reset email sent to {user['RecoveryEmail']}.")
    return jsonify({"message": "Password reset link sent"}), 200

@app.route('/reset_password', methods=['GET'])
def reset_password_api():
    token = request.args.get('token')
    if not token:
        log_error("Token not provided.")
        return jsonify({"error": "Token not provided"}), 400

    token_data = fetch_reset_token(token)
    if not token_data:
        log_error("Invalid or expired reset token.")
        return jsonify({"error": "Invalid or expired reset token"}), 900

    if token_data['Expiry'] < datetime.datetime.utcnow():
        log_error(f"Reset token for {token_data['Username']} has expired.")
        return jsonify({"error": "Reset token has expired"}), 901

    username = token_data['Username']
    log_info(f"Resetting password for user: {username}")

    reset_password(username)

    log_info(f"Password for user {username} reset successfully.")
    return redirect('/password_reset')

@app.route('/password_reset', methods=['GET'])
def reset_password_page():
    return render_template('password_reset.html')

@app.route('/create_website', methods=['POST'])
def create_website_endpoint():
    data = request.get_json()
    username = data.get('username')
    git_url = data.get('git_url')
    sftp_access = data.get('sftp_access', False)  # Default to False
    ssg = data.get('ssg', False)  # Default to False
    domain = data.get('domain')

    log_info(f"Received website creation request for username: {username}")

    user = fetch_user_by_username(username)
    if not user:
        log_error(f"User {username} not found.")
        return jsonify({"error": "User not found"}), 404

    user_tier = user.get('Tier', 'starter')
    existing_sites = websites_collection.find({'Username': username}).count()

    if user_tier == 'starter' and existing_sites >= 1:
        log_error(f"User {username} already using their starter tier website slot.")
        return jsonify({"error": "You are already using the starter tier website slot"}), 409

    if user_tier == 'starter':
        if not domain.endswith('.blahaj.land'):
            return jsonify({"error": "Free users can only use blahaj.land subdomains."}), 468

    git_url = validate_git_url(git_url)
    if not sftp_access and not git_url:
        log_error(f"Invalid Git URL: {git_url}")
        return jsonify({"error": "Invalid Git URL"}), 400

    makesite_token = generate_reset_token()
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    
    store_makesite_token(username, makesite_token, domain, git_url, sftp_access, expiry_time, ssg)

    confirm_link = f"https://backhaj.blahaj.land/confirm_site?token={makesite_token}"

    case = "Confirm creating a website."
    line1 = "If this wasn't you, please ignore this message, do not forward the link to anyone."
    line2 = "If this was you, click the link below to confirm the request."
    line3 = "It might take a couple of minutes, we will notify you when it's done!"
    link = confirm_link
    buttontext = "Confirm"

    send_website_setup_email(f"{username}@blahaj.land", f"{username}", case, line1, line2, line3, link, buttontext)
    send_website_setup_email(user['RecoveryEmail'], f"{username}", case, line1, line2, line3, link, buttontext)
    log_info(f"Website setup confirmation email sent to {user['RecoveryEmail']} and {username}@blahaj.land.")

    return jsonify({"message": "Website setup confirmation link sent"}), 200

@app.route('/website_being_made', methods=['GET'])
def website_being_made_page():
    return render_template('website_being_made.html')

@app.route('/confirm_site', methods=['GET'])
def confirm_site():
    token = request.args.get('token')
    if not token:
        log_error("Token not provided.")
        return jsonify({"error": "Token not provided"}), 400

    token_data = fetch_makesite_token(token)
    if not token_data:
        log_error("Invalid or expired makesite token.")
        return jsonify({"error": "Invalid or expired makesite token"}), 900

    if token_data['Expiry'] < datetime.datetime.utcnow():
        log_error(f"Makesite token for {token_data['Username']} has expired.")
        return jsonify({"error": "Makesite token has expired"}), 901

    username = token_data['Username']
    git_url = token_data.get('GitURL')
    sftp_access = token_data['SftpAccess']
    ssg = token_data['SSG']
    website_domain = token_data['Domain']

    log_info(f"Confirmed website creation for user: {username}")

    timestamp = datetime.datetime.utcnow()

# this is mostly broken, it always sends out SFTP access emails because the checking doesnt work and idk how to make it work
    create_website(username, website_domain, sftp_password)

    if website_domain.endswith(".blahaj.land"):
        if sftp_access :
            case = "your site is almost ready!"
            line1 = "All you have to do now, is log in with sftp with these credentials:"
            line2 = "Host: blahaj.land Port:5898"
            line3 = f"User: blahaj_site__{website_index} Password: {sftp_password}"
            link = f"sftp://blahaj_site__{website_index}:{sftp_password}@blahaj.land:5898"
            buttontext = "Or click here!"
        elif ssg:
            case = "your site is almost ready!"
            line1 = "Unfortunately, this process couldn't be done automagically D:"
            line2 = "For safety reasons, static site generators are set up manually."
            line3 = "To finish setting up your site, contact @flathub on Discord."
            link = "https://discord.com/users/986309324521472040"
            buttontext = "Or click here to DM!"
        else:
            case = "your site is ready!"
            line1 = "Your request to set up a website has been processed."
            line2 = f"The site automatically pulls from {git_url} "
            line3 = "on all commits forward. Enjoy!"
            link = website_domain
            buttontext = "Check it out!"
    else:
        case = "your site is almost ready!"
        line1 = "A: 81.17.101.235"
        line2 = 'CAA: 0 issue "letsencrypt.org"'
        line3 = "Contact @flathub on Discord to finish setting it up!"
        link = "https://discord.com/users/986309324521472040"
        buttontext = "Or click here to DM!"

    if git_url:
        os.system(f"git clone {git_url} /var/www/blahaj_site__{website_index}")
        with open(config.user_pulls_sh, 'a') as f:
            f.write(f"cd /var/www/blahaj_site__{website_index} && git pull\n")
        return redirect('/website_being_made')
    
    send_website_setup_email(f"{username}@blahaj.land", f"{username}@blahaj.land", case, line1, line2, line3, link, buttontext)
    log_info(f"Website {website_domain} created successfully for user {username}.")

    send_discord_webhook(f"Website {website_domain} created for user {username}. SFTP: {sftp_access}, Git URL: {git_url}, Timestamp: {timestamp}")
    store_website_details(username, website_domain, git_url, sftp_access, ssg, timestamp)



if __name__ == '__main__':
    app.run(debug=True)