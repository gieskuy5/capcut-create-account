import requests
import json
import time
import random
import string
import os
import re
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# EMAIL PROVIDERS
# ═══════════════════════════════════════════════════════════════════════════════

class GuerrillaMailAPI:
    def __init__(self):
        self.base_url = "https://api.guerrillamail.com/ajax.php"
        self.session = requests.Session()
        self.email = self.sid_token = self.last_error = None

    def create_account(self):
        try:
            response = self.session.get(self.base_url, params={"f": "get_email_address", "ip": "127.0.0.1", "agent": "Mozilla/5.0"})
            data = response.json()
            self.email = data.get("email_addr")
            self.sid_token = data.get("sid_token")
            return self.email is not None
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_messages(self):
        try:
            response = self.session.get(self.base_url, params={"f": "get_email_list", "offset": 0, "sid_token": self.sid_token})
            return response.json().get("list", [])
        except:
            return []

    def get_message_content(self, mail_id):
        try:
            response = self.session.get(self.base_url, params={"f": "fetch_email", "email_id": mail_id, "sid_token": self.sid_token})
            data = response.json()
            return data.get("mail_body", ""), data.get("mail_from", ""), data.get("mail_subject", "")
        except:
            return "", "", ""

    def wait_for_verification_code(self, timeout=120, interval=5):
        start = time.time()
        print(f"  ├─ Checking inbox for CapCut verification email...")
        while time.time() - start < timeout:
            messages = self.get_messages()
            for msg in messages:
                content, sender, subject = self.get_message_content(msg.get("mail_id"))
                # Only process CapCut emails
                if "capcut" in sender.lower() or "capcut" in subject.lower() or "bytedance" in sender.lower():
                    # Look for 6-digit verification code
                    codes = re.findall(r'(?:code|Code|CODE)[:\s]*?(\d{6})', content)
                    if not codes:
                        codes = re.findall(r'>\s*(\d{6})\s*<', content)
                    if not codes:
                        codes = re.findall(r'\b(\d{6})\b', content)
                    # Filter out invalid codes
                    valid_codes = [c for c in codes if c != '000000' and len(set(c)) > 1]
                    if valid_codes:
                        print(f"  ├─ Found email from: {sender[:40]}...")
                        return valid_codes[0]
            elapsed = int(time.time() - start)
            print(f"  ├─ Waiting for email... ({elapsed}s/{timeout}s)")
            time.sleep(interval)
        return None


class MailTm:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        self.session = requests.Session()
        self.email = self.password = self.token = self.last_error = None

    def get_domains(self):
        try:
            response = self.session.get(f"{self.base_url}/domains")
            domains = response.json().get("hydra:member", [])
            return [d["domain"] for d in domains] if domains else []
        except Exception as e:
            self.last_error = str(e)
            return []

    def create_account(self):
        try:
            domains = self.get_domains()
            if not domains:
                return False
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            self.email = f"{username}@{domains[0]}"
            self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            response = self.session.post(f"{self.base_url}/accounts", json={"address": self.email, "password": self.password})
            return response.status_code == 201
        except Exception as e:
            self.last_error = str(e)
            return False

    def login(self):
        try:
            response = self.session.post(f"{self.base_url}/token", json={"address": self.email, "password": self.password})
            self.token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return self.token is not None
        except:
            return False

    def get_messages(self):
        try:
            response = self.session.get(f"{self.base_url}/messages")
            return response.json().get("hydra:member", [])
        except:
            return []

    def get_message_content(self, msg_id):
        try:
            response = self.session.get(f"{self.base_url}/messages/{msg_id}")
            data = response.json()
            content = data.get("text", "") or data.get("html", "")
            sender = data.get("from", {}).get("address", "")
            subject = data.get("subject", "")
            return content, sender, subject
        except:
            return "", "", ""

    def wait_for_verification_code(self, timeout=120, interval=5):
        if not self.login():
            return None
        start = time.time()
        print(f"  ├─ Checking inbox for CapCut verification email...")
        while time.time() - start < timeout:
            messages = self.get_messages()
            for msg in messages:
                content, sender, subject = self.get_message_content(msg.get("id"))
                if "capcut" in sender.lower() or "capcut" in subject.lower() or "bytedance" in sender.lower():
                    codes = re.findall(r'(?:code|Code|CODE)[:\s]*?(\d{6})', content)
                    if not codes:
                        codes = re.findall(r'>\s*(\d{6})\s*<', content)
                    if not codes:
                        codes = re.findall(r'\b(\d{6})\b', content)
                    valid_codes = [c for c in codes if c != '000000' and len(set(c)) > 1]
                    if valid_codes:
                        print(f"  ├─ Found email from: {sender[:40]}...")
                        return valid_codes[0]
            elapsed = int(time.time() - start)
            print(f"  ├─ Waiting for email... ({elapsed}s/{timeout}s)")
            time.sleep(interval)
        return None


class OneSecMail:
    def __init__(self):
        self.base_url = "https://www.1secmail.com/api/v1"
        self.session = requests.Session()
        self.email = self.login_name = self.domain = self.last_error = None

    def create_account(self):
        try:
            response = self.session.get(f"{self.base_url}/?action=genRandomMailbox&count=1")
            self.email = response.json()[0]
            self.login_name, self.domain = self.email.split("@")
            return True
        except Exception as e:
            self.last_error = str(e)
            return False

    def get_messages(self):
        try:
            response = self.session.get(f"{self.base_url}/?action=getMessages&login={self.login_name}&domain={self.domain}")
            return response.json()
        except:
            return []

    def get_message_content(self, msg_id):
        try:
            response = self.session.get(f"{self.base_url}/?action=readMessage&login={self.login_name}&domain={self.domain}&id={msg_id}")
            data = response.json()
            content = data.get("body", "")
            sender = data.get("from", "")
            subject = data.get("subject", "")
            return content, sender, subject
        except:
            return "", "", ""

    def wait_for_verification_code(self, timeout=120, interval=5):
        start = time.time()
        print(f"  ├─ Checking inbox for CapCut verification email...")
        while time.time() - start < timeout:
            messages = self.get_messages()
            for msg in messages:
                content, sender, subject = self.get_message_content(msg.get("id"))
                if "capcut" in sender.lower() or "capcut" in subject.lower() or "bytedance" in sender.lower():
                    codes = re.findall(r'(?:code|Code|CODE)[:\s]*?(\d{6})', content)
                    if not codes:
                        codes = re.findall(r'>\s*(\d{6})\s*<', content)
                    if not codes:
                        codes = re.findall(r'\b(\d{6})\b', content)
                    valid_codes = [c for c in codes if c != '000000' and len(set(c)) > 1]
                    if valid_codes:
                        print(f"  ├─ Found email from: {sender[:40]}...")
                        return valid_codes[0]
            elapsed = int(time.time() - start)
            print(f"  ├─ Waiting for email... ({elapsed}s/{timeout}s)")
            time.sleep(interval)
        return None


def create_temp_email_with_fallback():
    """Try multiple email providers until one works"""
    providers = [GuerrillaMailAPI, MailTm, OneSecMail]
    for Provider in providers:
        try:
            provider = Provider()
            if provider.create_account():
                print(f"  ├─ Email Provider: {Provider.__name__}")
                print(f"  ├─ Email: {provider.email}")
                return provider
        except Exception as e:
            print(f"  ├─ {Provider.__name__} failed: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# PROXY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class ProxyManager:
    def __init__(self, proxy_file="proxy.txt"):
        self.proxies = []
        self.current_index = 0
        self.load_proxies(proxy_file)

    def load_proxies(self, proxy_file):
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        print(f"  ├─ Loaded {len(self.proxies)} proxies")

    def get_next(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index % len(self.proxies)]
        self.current_index += 1
        return {"http": proxy, "https": proxy}


# ═══════════════════════════════════════════════════════════════════════════════
# BROWSER DATA GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class BrowserData:
    def __init__(self):
        self.device_id = self.generate_device_id()
        self.verify_fp = self.generate_verify_fp()
        self.csrf_token = self.generate_csrf_token()

    @staticmethod
    def generate_device_id():
        """Generate a 19-digit device ID"""
        return str(random.randint(7000000000000000000, 7999999999999999999))

    @staticmethod
    def generate_verify_fp():
        """Generate a verifyFp token"""
        chars = string.ascii_letters + string.digits
        suffix = ''.join(random.choices(chars, k=40))
        return f"verify_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}_{suffix}"

    @staticmethod
    def generate_csrf_token():
        """Generate a 32-character hex CSRF token"""
        return ''.join(random.choices('0123456789abcdef', k=32))

    def get_headers(self):
        return {
            "accept": "application/json, text/javascript",
            "accept-language": "en-US,en;q=0.9",
            "appid": "348188",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "did": self.device_id,
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "store-country-code": "id",
            "store-country-code-src": "uid",
            "x-tt-passport-csrf-token": self.csrf_token,
            "referer": "https://www.capcut.com/",
            "origin": "https://www.capcut.com",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CAPCUT API
# ═══════════════════════════════════════════════════════════════════════════════

class CapCutAPI:
    BASE_URL = "https://login-row.www.capcut.com/passport/web"
    
    def __init__(self, browser_data: BrowserData, proxy=None):
        self.browser = browser_data
        self.session = requests.Session()
        self.session.headers.update(self.browser.get_headers())
        if proxy:
            self.session.proxies = proxy
        self.session.verify = True

    @staticmethod
    def encode_mix_mode(text):
        """Encode text using CapCut's mix_mode (XOR with 0x05, hex output)"""
        return ''.join(format(ord(c) ^ 0x05, '02x') for c in text)

    def _get_url_params(self):
        return {
            "aid": "348188",
            "account_sdk_source": "web",
            "sdk_version": "2.1.10-tiktok",
            "language": "en",
            "verifyFp": self.browser.verify_fp
        }

    def check_email_registered(self, email):
        """Step 1: Check if email is already registered"""
        url = f"{self.BASE_URL}/user/check_email_registered"
        encoded_email = self.encode_mix_mode(email)
        data = f"mix_mode=1&email={encoded_email}&fixed_mix_mode=1"
        
        try:
            response = self.session.post(url, params=self._get_url_params(), data=data, timeout=30)
            result = response.json()
            if result.get("message") == "success" and result.get("data", {}).get("is_registered") == 0:
                return True
            return False
        except Exception as e:
            print(f"  ├─ Check email error: {e}")
            return False

    def send_verification_code(self, email, password):
        """Step 2: Send verification code to email"""
        url = f"{self.BASE_URL}/email/send_code/"
        encoded_email = self.encode_mix_mode(email)
        encoded_password = self.encode_mix_mode(password)
        data = f"mix_mode=1&email={encoded_email}&password={encoded_password}&type=34&fixed_mix_mode=1"
        
        try:
            response = self.session.post(url, params=self._get_url_params(), data=data, timeout=30)
            result = response.json()
            if result.get("message") == "success":
                return result.get("data", {}).get("email_ticket")
            print(f"  ├─ Send code failed: {result}")
            return None
        except Exception as e:
            print(f"  ├─ Send code error: {e}")
            return None

    def register_verify(self, email, code, password, birthday="2000-01-01"):
        """Step 3: Complete registration with verification code"""
        url = f"{self.BASE_URL}/email/register_verify_login/"
        encoded_email = self.encode_mix_mode(email)
        encoded_code = self.encode_mix_mode(code)
        encoded_password = self.encode_mix_mode(password)
        
        biz_param = '{"invite_code":""}'
        data = (
            f"mix_mode=1&email={encoded_email}&code={encoded_code}&password={encoded_password}"
            f"&type=34&birthday={birthday}&force_user_region=ID"
            f"&biz_param={requests.utils.quote(biz_param)}&fixed_mix_mode=1"
        )
        
        try:
            response = self.session.post(url, params=self._get_url_params(), data=data, timeout=30)
            result = response.json()
            if result.get("message") == "success":
                return result.get("data", {})
            print(f"  ├─ Register failed: {result}")
            return None
        except Exception as e:
            print(f"  ├─ Register error: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN REGISTRATION LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

def generate_password(length=10):
    """Generate a random password"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_birthday():
    """Generate a random birthday (18-35 years old)"""
    year = random.randint(1990, 2006)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def save_session(data, email, password, browser: BrowserData, filename="sessions.json"):
    """Save account data to sessions.json"""
    sessions = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                sessions = json.load(f)
            except:
                sessions = []
    
    session_data = {
        "email": email,
        "password": password,
        "user_id": data.get("user_id_str", data.get("user_id")),
        "name": data.get("name"),
        "device_id": browser.device_id,
        "sec_user_id": data.get("sec_user_id"),
        "created_at": datetime.now().isoformat()
    }
    sessions.append(session_data)
    
    with open(filename, 'w') as f:
        json.dump(sessions, f, indent=2)
    
    return session_data


def register_account(proxy_manager: ProxyManager, account_num: int):
    """Register a single CapCut account"""
    print(f"\n{'='*60}")
    print(f"  ACCOUNT #{account_num}")
    print(f"{'='*60}")
    
    # Generate unique browser data
    browser = BrowserData()
    print(f"  ├─ Device ID: {browser.device_id}")
    
    # Get proxy
    proxy = proxy_manager.get_next()
    if proxy:
        print(f"  ├─ Proxy: {list(proxy.values())[0][:50]}...")
    else:
        print(f"  ├─ Proxy: None (direct connection)")
    
    # Create temp email
    email_provider = create_temp_email_with_fallback()
    if not email_provider:
        print(f"  └─ ❌ Failed to create temp email")
        return None
    
    email = email_provider.email
    password = generate_password()
    birthday = generate_birthday()
    print(f"  ├─ Password: {password}")
    print(f"  ├─ Birthday: {birthday}")
    
    # Initialize API
    api = CapCutAPI(browser, proxy)
    
    # Step 1: Check email
    print(f"  ├─ Step 1: Checking email...")
    if not api.check_email_registered(email):
        print(f"  └─ ❌ Email check failed or already registered")
        return None
    print(f"  ├─ ✓ Email available")
    
    # Step 2: Send verification code
    print(f"  ├─ Step 2: Sending verification code...")
    ticket = api.send_verification_code(email, password)
    if not ticket:
        print(f"  └─ ❌ Failed to send verification code")
        return None
    print(f"  ├─ ✓ Verification code sent (ticket: {ticket[:20]}...)")
    
    # Step 3: Wait for and get verification code
    print(f"  ├─ Step 3: Waiting for verification code (up to 120s)...")
    code = email_provider.wait_for_verification_code(timeout=120, interval=5)
    if not code:
        print(f"  └─ ❌ No verification code received")
        return None
    print(f"  ├─ ✓ Verification code: {code}")
    
    # Step 4: Complete registration
    print(f"  ├─ Step 4: Completing registration...")
    result = api.register_verify(email, code, password, birthday)
    if not result:
        print(f"  └─ ❌ Registration failed")
        return None
    
    # Save session
    session = save_session(result, email, password, browser)
    print(f"  ├─ ✓ User ID: {session.get('user_id')}")
    print(f"  ├─ ✓ Name: {session.get('name')}")
    print(f"  └─ ✓ Account saved to sessions.json")
    
    return session


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║            CAPCUT AUTO REGISTRATION BOT                    ║
║        Proxy Support + Unique Browser Data                 ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Load proxies
    print("\n[INITIALIZING]")
    proxy_manager = ProxyManager("proxy.txt")
    
    # Get number of accounts
    try:
        num_accounts = int(input("\n[?] How many accounts to create: "))
    except ValueError:
        num_accounts = 1
    
    print(f"\n[*] Creating {num_accounts} account(s)...")
    
    successful = 0
    failed = 0
    
    for i in range(1, num_accounts + 1):
        try:
            result = register_account(proxy_manager, i)
            if result:
                successful += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  └─ ❌ Error: {e}")
            failed += 1
        
        # Delay between accounts
        if i < num_accounts:
            delay = random.randint(3, 8)
            print(f"\n[*] Waiting {delay}s before next account...")
            time.sleep(delay)
    
    # Summary
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                      SUMMARY                               ║
╠════════════════════════════════════════════════════════════╣
║  ✓ Successful: {successful:<44}║
║  ✗ Failed: {failed:<48}║
║  Total: {num_accounts:<50}║
╚════════════════════════════════════════════════════════════╝
    """)
    
    if successful > 0:
        print(f"[*] Accounts saved to: sessions.json")


if __name__ == "__main__":
    main()
