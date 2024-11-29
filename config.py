import configparser

# read configs
config = configparser.ConfigParser()
config.read('config.conf')

# general settings
base_directory = config['DEFAULT']['base_directory']
email_template_path = config['DEFAULT']['email_template_path']
password_reset_email_template_path = config['DEFAULT']['password_reset_email_template_path']
website_email_template_path = config['DEFAULT']['website_email_template_path']
user_pulls_sh = config['DEFAULT']['user_pulls_sh']

# discord settings
discord_bot_token = config['DISCORD']['bot_token']
discord_server_id = config['DISCORD']['server_id']
discord_webhook_url = config['DISCORD']['discord_webhook_url']

# mongo settings
mongo_host = config['MONGODB']['host']
mongo_port = config['MONGODB']['port']
mongo_user = config['MONGODB']['user']
mongo_password = config['MONGODB']['password']
mongo_db_name = config['MONGODB']['db_name']

# JWT settings
jwt_user = {
    'username': config['JWT_USER']['username'],
    'password': config['JWT_USER']['password']
}
jwt_secret_key = config['JWT_KEY']['jwt_secret_key']

# SMTP settings
smtp_server = config['SMTP']['smtp_server']
smtp_port = config['SMTP']['smtp_port']
smtp_user = config['SMTP']['smtp_user']
smtp_password = config['SMTP']['smtp_password']