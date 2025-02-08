#!/usr/bin/env python3

import subprocess
import sys
import argparse
from termcolor import colored
from logging_utils import log_error, log_info, log_warning, log_success
from yunohost_utils import retry_command_until_success

def list_domains():
    log_info("fetching domain list...")
    domains_output = retry_command_until_success("yunohost domain list --output-as plain")
    if domains_output:
        domains = domains_output.splitlines()
        if domains:
            for i, domain in enumerate(domains, 1):
                print(f"{i}. {domain}")
            return domains
    log_error("no domains found.")
    return []

def add_domain(website_domain):
    log_info(f"adding domain: {website_domain}")
    retry_command_until_success(f"yunohost domain add {website_domain}")
    log_success(f"domain {website_domain} added.")
    
    log_info(f"signing certificate for {website_domain}...")
    retry_command_until_success(f"yunohost domain cert install {website_domain} --no-checks")
    log_success(f"certificate signed for {website_domain}")

def remove_domain(website_domain):
    log_info(f"removing domain: {website_domain}")
    retry_command_until_success(f"yunohost domain remove {website_domain}")
    log_success(f"domain {website_domain} removed.")

def renew_certificate(website_domain):
    log_info(f"renewing certificate for {website_domain}...")
    retry_command_until_success(f"yunohost domain cert install {website_domain} --no-checks")
    log_success(f"certificate for {website_domain} renewed.")

def print_dns_config(website_domain):
    log_info(f"fetching dns config for {website_domain}...")
    dns_output = retry_command_until_success(f"yunohost domain dns-conf {website_domain}")
    if dns_output:
        print(f"\n🔧 dns configuration for {website_domain}:\n{'-'*40}\n{dns_output}\n{'-'*40}\n")
    else:
        log_warning(f"could not fetch dns config for {website_domain}.")

