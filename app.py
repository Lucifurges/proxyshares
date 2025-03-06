import requests
import hashlib
import uuid
import random
import string
import time
import threading
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

# List of proxies (replace with actual working proxies)
proxy_list = [
    'http://14.102.155.233:6361',  # Indonesia - Transparent HTTP
    'socks4://102.176.178.66:BF',  # Burkina Faso - Elite SOCKS4
    'http://1.20.200.154:6320',   # Thailand - Transparent HTTP
    'http://102.0.14.38:KE',      # Kenya - Transparent HTTP
    'http://139.135.189.175:11963', # Philippines - Transparent HTTP
    'http://102.222.51.105:6899',  # Botswana - Transparent HTTP
    'socks4://0.241.235.103:17563', # Elite SOCKS4
    'socks4://134.202.84.7:7642',   # Australia - Elite SOCKS4
    'socks4://14.207.56.105:17387', # Thailand - Elite SOCKS4
    'socks4://134.73.99.32:13878',  # United States - Elite SOCKS4
    'socks4://100.110.6.97:10113',  # Elite SOCKS4
    'socks4://1.20.184.75:1064',    # Thailand - Elite SOCKS4
    'socks4://137.242.54.38:11228', # United States - Elite SOCKS4
    'socks4://136.226.100.166:10770', # United States - Elite SOCKS4
    'socks4://1.82.216.134:11228',  # China - Elite SOCKS4
]

def clear_screen():
    os.system('clear')  # Works for Termux

def display_banner(title):
    banner = "(PyeulShares)" * 10  # Repeat 10 times
    console.print(Panel(banner, title=f"[yellow]● {title}[/]", width=65, style="bold bright_white"))

def random_string(length):
    characters = string.ascii_lowercase + "0123456789"
    return ''.join(random.choice(characters) for _ in range(length))

def encode_sig(data):
    sorted_data = {k: data[k] for k in sorted(data)}
    data_str = ''.join(f"{key}={value}" for key, value in sorted_data.items())
    return hashlib.md5((data_str + '62f8ce9f74b12f84c123cc23437a4a32').encode()).hexdigest()

def generate_token(email, password):
    device_id = str(uuid.uuid4())  # Generate a unique device ID each time
    adid = str(uuid.uuid4())  # Generate a unique adid each time
    random_str = random_string(24)

    form = {
        'adid': adid,
        'email': email,
        'password': password,
        'format': 'json',
        'device_id': device_id,
        'cpl': 'true',
        'family_device_id': device_id,
        'locale': 'en_US',
        'client_country_code': 'US',
        'credentials_type': 'device_based_login_password',
        'generate_session_cookies': '1',
        'generate_analytics_claim': '1',
        'generate_machine_id': '1',
        'source': 'login',
        'machine_id': random_str,
        'api_key': '882a8490361da98702bf97a021ddc14d',
        'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
    }

    form['sig'] = encode_sig(form)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile; rv:94.0) Gecko/94.0 Firefox/94.0',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }

    url = 'https://graph.facebook.com/auth/login'

    # Ask the user if they want to use a proxy
    use_proxy = input("Do you want to use a proxy? (y/n): ").strip().lower()
    proxies = None
    if use_proxy == 'y':
        # Rotate through proxies until one works
        for _ in range(5):  # Try up to 5 proxies
            proxy = random.choice(proxy_list)
            proxies = {
                'http': proxy,
                'https': proxy,
            }
            try:
                response = requests.post(url, data=form, headers=headers, proxies=proxies, timeout=15)
                data = response.json()

                if response.status_code == 200 and 'access_token' in data:
                    full_token = data['access_token']
                    console.print(f"\n[+] Generated Token: {full_token}\n", style="green")
                    return  # Exit once token is successfully generated
                elif 'error' in data:
                    console.print(f"[-] Facebook Error: {data['error']['message']}", style="red")
                    return
                else:
                    console.print("[-] Unknown error occurred. Check credentials.", style="red")
                    return
            except requests.exceptions.RequestException as e:
                console.print(f"[!] Proxy Error: {str(e)}", style="red")
                time.sleep(2)  # Wait before trying another proxy
        console.print("[!] All proxies failed! Try again later.", style="red")
    else:
        # Without Proxy
        try:
            response = requests.post(url, data=form, headers=headers, timeout=15)
            data = response.json()

            if response.status_code == 200 and 'access_token' in data:
                full_token = data['access_token']
                console.print(f"\n[+] Generated Token: {full_token}\n", style="green")
            elif 'error' in data:
                console.print(f"[-] Facebook Error: {data['error']['message']}", style="red")
            else:
                console.print("[-] Unknown error occurred. Check credentials.", style="red")

        except requests.exceptions.RequestException as e:
            console.print(f"[!] Request Error: {str(e)}", style="red")
    
    input("\nPress Enter to return to menu...")

def load_cookies():
    clear_screen()
    display_banner("PASTE MULTIPLE TOKENS")
    console.print("[yellow]Paste your access tokens (one per line, then press Enter when done):[/yellow]")
    tokens = input().strip().split()
    return [token for token in tokens if token.startswith("EAAAA")]

def share_post(cookie, share_url, share_count, interval=0.1):
    url = "https://graph.facebook.com/me/feed"
    headers = {"User-Agent": "Mozilla/5.0"}
    data = {
        "link": share_url,
        "privacy": '{"value":"SELF"}',
        "no_story": "true",
        "published": "false",
        "access_token": cookie
    }
    
    success_count = 0
    for i in range(1, share_count * 2 + 1):
        try:
            response = requests.post(url, json=data, headers=headers)
            response_data = response.json()
            if "id" in response_data:
                success_count += 1
                console.print(f"[bold cyan]({success_count}/{share_count * 2})[/bold cyan] [green]Shared successfully.")
            else:
                console.print(f"[red]Failed to share: {response_data}")
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error: {e}")
        time.sleep(interval)
    console.print(f"[bold cyan]Total Successful Shares: {success_count}[/bold cyan]\n")

def spam_share_multiple():
    clear_screen()
    display_banner("MULTI-COOKIE SPAM SHARE")
    cookies = load_cookies()
    if not cookies:
        return
    share_url = input("Enter post link: ").strip()
    share_count = int(input("Enter Share Count per account: ").strip())
    threads = [threading.Thread(target=share_post, args=(cookie, share_url, share_count)) for cookie in cookies]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    console.print("[green]Finished sharing posts from all accounts.")
    input("\nPress Enter to return to menu...")

def spam_share_single():
    clear_screen()
    display_banner("SINGLE TOKEN SHARE")
    token = input("Enter Facebook access token: ").strip()
    if not token.startswith("EAAAA"):
        console.print("[red]Invalid token format!")
        return
    share_url = input("Enter post link: ").strip()
    share_count = int(input("Enter Share Count: ").strip())
    share_post(token, share_url, share_count, interval=0.1)
    console.print("[green]Finished sharing post.")
    input("\nPress Enter to return to menu...")

def main_menu():
    while True:
        clear_screen()
        display_banner("FACEBOOK TOOL")
        console.print(Panel("""
[green]1. Multi-Cookie Spam Share
[green]2. Single Token Share
[green]3. Generate Token
[green]4. Exit
        """, width=65, style="bold bright_white"))
        choice = input("Select an option: ").strip()
        if choice == "1":
            spam_share_multiple()
        elif choice == "2":
            spam_share_single()
        elif choice == "3":
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            generate_token(email, password)
        elif choice == "4":
            console.print("[red]Exiting... Goodbye!")
            break
        else:
            console.print("[red]Invalid choice! Try again.")
            time.sleep(2)

if __name__ == '__main__':
    main_menu()
