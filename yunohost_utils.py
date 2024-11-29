import subprocess
import json
import shlex
import time
from datetime import datetime
from logging_utils import log_info, log_warning, log_error
import csv
import io

def fetch_yunohost_users():
    command = "yunohost user list --output-as json --fields username fullname mail"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    users = json.loads(result.stdout)['users']
    return users

def get_user_timestamp(username):
    command = f"ls -l /home/{username}"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    lines = result.stdout.splitlines()
    for line in lines:
        if 'media' in line:
            parts = line.split()
            date_str = f"{parts[5]} {parts[6]} {parts[7]}"
            timestamp = datetime.strptime(date_str, "%b %d %H:%M")
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return None

def run_command(command, verbose=False, timeout=1000):
    if verbose:
        log_info(f"Running command: {command}")
    try:
        args = shlex.split(command)
        result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        if verbose:
            print(result.stdout.strip())
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log_error(f"Command timed out: {command}")
        return None
    except subprocess.CalledProcessError as e:
        if verbose:
            log_error(f"Command failed: {e.stderr.strip()}")
        return None

# this function needs to be replaced with a queue, that runs the commands from a collection in the db probably
# then it needs to try the commands, after that it should move the command to a logs collection with a status and timestamp
def retry_command_until_success(command, verbose=False, retry_interval=10):
    while True:
        output = run_command(command, verbose)
        if output and 'Another YunoHost command is running' in output:
            log_warning("YunoHost is busy, retrying in 10 seconds...")
            time.sleep(retry_interval)
        else:
            return output

def get_yunohost_users(verbose=False):
    command = "yunohost user list --output-as json --fields username"
    output = retry_command_until_success(command, verbose)
    if output:
        try:
            users_data = json.loads(output)
            return [user["username"] for user in users_data["users"].values()] 
        except json.JSONDecodeError as e:
            log_error(f"Error decoding YunoHost user list: {e}")
            return []
    else:
        log_error("Failed to retrieve YunoHost user list.")
        return []

def fetch_and_print_users_csv_for_list():
    command = "yunohost user export"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    csv_output = result.stdout
    
    csv_reader = csv.reader(io.StringIO(csv_output), delimiter=';')
    
    print("email,name,attributes")
    for row in csv_reader:
        if row:  
            username = row[0]
            email = f"{username}@blahaj.land"
            name = username
            attributes = "{}"
            print(f'{email},"{name}","{attributes}"')