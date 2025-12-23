# CapCut Auto Registration Bot

Automated CapCut account registration using temporary email providers, with proxy support and unique browser fingerprints per account.

## Features

- **Multiple Email Providers** - GuerrillaMail, MailTm, 1SecMail with automatic fallback
- **Proxy Support** - Rotating proxies from `proxy.txt`
- **Unique Browser Data** - Each account gets unique device_id, verifyFp, and CSRF token
- **Auto Verification** - Automatically extracts verification code from email
- **Session Storage** - Saves account credentials to `sessions.json`

## Requirements

```bash
pip install requests
```

## Usage

1. **Add proxies** (optional but recommended):
   ```
   # proxy.txt - one proxy per line
   http://user:pass@host:port
   ```

2. **Run the script**:
   ```bash
   python main.py
   ```

3. **Enter number of accounts** to create when prompted

## Files

| File | Description |
|------|-------------|
| `main.py` | Main registration script |
| `proxy.txt` | Proxy list (one per line) |
| `sessions.json` | Saved account credentials |

## Output Example

```
============================================================
  ACCOUNT #1
============================================================
  ├─ Device ID: 7106615967717160363
  ├─ Proxy: http://user:pass@host:port...
  ├─ Email Provider: GuerrillaMailAPI
  ├─ Email: example@guerrillamailblock.com
  ├─ Password: nJ83pVs9M8
  ├─ Birthday: 2004-07-12
  ├─ Step 1: Checking email...
  ├─ ✓ Email available
  ├─ Step 2: Sending verification code...
  ├─ ✓ Verification code sent
  ├─ Step 3: Waiting for verification code (up to 120s)...
  ├─ ✓ Verification code: 502007
  ├─ Step 4: Completing registration...
  ├─ ✓ User ID: 7586918190342571015
  └─ ✓ Account saved to sessions.json
```

## Session Format

```json
{
  "email": "example@guerrillamailblock.com",
  "password": "nJ83pVs9M8",
  "user_id": "7586918190342571015",
  "name": "user266812270218",
  "device_id": "7106615967717160363",
  "sec_user_id": "MS4wLjABAAAA...",
  "created_at": "2025-12-23T12:20:00"
}
```

## Notes

- Uses CapCut's mix_mode encoding (XOR with 0x05)
- Waits up to 120s for verification email
- Random 3-8s delay between accounts to avoid rate limiting
