from termcolor import colored

def log_info(message):
    print(colored(f"ℹ️ {message}", "blue"))

def log_success(message):
    print(colored(f"✅ {message}", "green"))

def log_warning(message):
    print(colored(f"⚠️ {message}", "yellow"))

def log_error(message):
    print(colored(f"❌ {message}", "red"))