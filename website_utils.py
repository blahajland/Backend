import time
import random
import string
import re
import subprocess
import shlex
from flask import jsonify
from logging_utils import log_success, log_error, log_info, log_warning
from mongo_utils import fetch_user_by_username, save_user_to_db, store_reset_token, fetch_reset_token
from domainmanager import add_domain, print_dns_config
from yunohost_utils import retry_command_until_success
from usermanager import generate_password
import re

#the regex is nt working iirc

# Define regex for Git URLs
TRUSTED_GIT_URLS = [
    r"^https://github.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)/?$",
    r"^https://gitlab.com/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)/?$",
    r"^https://codeberg.org/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)/?$",
    r"^https://git.blahaj.land/([a-zA-Z0-9-]+)/([a-zA-Z0-9-]+)/?$"
]

def validate_git_url(git_url):
    for pattern in TRUSTED_GIT_URLS:
        if re.match(pattern, git_url):
            if not git_url.endswith('.git'):
                git_url += '.git'
            return git_url
    return None

sftp_password = generate_password()
website_index = 0

def create_website(username, website_domain, sftp_password):
    global website_index
    # Add the domain
    add_domain(website_domain)
    
    # Install the website app in Yunohost
    command = (f'yunohost app install https://github.com/blahajland/blahaj_site_ynh '
               f'-l "{username}\'s site" -a "domain={website_domain}&path=/&with_sftp=true&password="{sftp_password}"&'
               f'init_main_permission=visitors&phpversion=8.3&database=none&custom_error_file=true" --force')
    
    result = retry_command_until_success(command, verbose=True)
    if result:
        log_info(f"Website installation output: {result}")
        match = re.search(r'Installation of blahaj_site__(\d+) completed', result)
        if match:
            website_index = match.group(1)
            log_success(f"Website blahaj_site__{website_index} created successfully for {username}.")
            return {"message": "Website created successfully", "website_index": website_index, "sftp_password": sftp_password}, 201
        else:
            log_error("Failed to extract website index from the Yunohost output.")
            return None
    else:
        log_error("Website installation failed.")
        return None
    
# iirc this is also not really functional, it makes the site but there are errors