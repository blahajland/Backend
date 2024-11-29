import discord
from discord import Client, Intents, utils
from logging_utils import log_info, log_warning, log_error, log_success
from config import discord_bot_token, discord_webhook_url 
import threading
import requests

intents = Intents.default()
intents.members = True
discord_client = Client(intents=intents)

@discord_client.event
async def on_ready():
    log_info(f"Logged into Discord as {discord_client.user}")

async def fetch_discord_id(username):
    for guild in discord_client.guilds:
        member = utils.get(guild.members, name=username)
        if member:
            return member.id
    log_warning(f"Discord user {username} not found in any guild.")
    return None

def run_discord_client():
    discord_client.run(discord_bot_token)

def start_discord_client_thread():
    log_info("Starting Discord client thread.")
    discord_thread = threading.Thread(target=run_discord_client)
    discord_thread.start()
    log_info("Discord client thread started.")


def send_discord_webhook(message):
    data = {
        "content": message
    }
    
    try:
        response = requests.post(discord_webhook_url, json=data)
        if response.status_code == 204:
            log_success("Discord webhook sent successfully.")
        else:
            log_error(f"Failed to send Discord webhook. Status code: {response.status_code}")
    except Exception as e:
        log_error(f"Error sending Discord webhook: {e}")
