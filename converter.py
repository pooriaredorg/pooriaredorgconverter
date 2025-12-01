import requests
import base64
import json
import re
from urllib.parse import urlparse, parse_qs

# لینک سابسکرایب شما
SUB_URL = "https://raw.githubusercontent.com/pooriaredorg/pooriaredorg/refs/heads/main/configs/proxy_configs.txt"
OUTPUT_FILE = 'sub_config.json'

def decode_base64(data):
    """تلاش برای دیکد کردن Base64، اگر نشد متن اصلی را برمی‌گرداند"""
    data = data.strip()
    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except Exception:
        # اگر خطا داد یعنی متن احتمالا Base64 نیست و لینک‌ها مستقیم نوشته شده‌اند
        return data

def parse_vmess(vmess_url):
    """استخراج اطلاعات از لینک vmess"""
    try:
        b64_part = vmess_url.replace("vmess://", "")
        json_str = decode_base64(b64_part)
        return json.loads(json_str)
    except Exception:
        return None

def parse_vless_trojan(url, protocol):
    """استخراج اطلاعات از لینک vless یا trojan"""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return {
            "protocol": protocol,
            "uuid": parsed.username,
            "address": parsed.hostname,
            "port": parsed.port,
            "name": parsed.fragment if parsed.fragment else "No Name",
            "params": {k: v[0] for k, v in params.items()} # ساده‌سازی پارامترها
        }
    except Exception:
        return None

def main():
    print(f"Fetching from: {SUB_URL}")
    try:
        response = requests.get(SUB_URL, timeout=30)
        response.raise_for_status()
        
        # محتوا را می‌گیریم
        content = response.text.strip()
        
        # بررسی می‌کنیم آیا کل فایل کد شده است یا خیر
        decoded_content = decode_base64(content)
        
        # خط به خط جدا می‌کنیم
        links = decoded_content.splitlines()
        
        json_output = []
        
        for link in links:
            link = link.strip()
            if not link: continue
            
            if link.startswith("vmess://"):
                data = parse_vmess(link)
                if data: json_output.append(data)
                
            elif link.startswith("vless://"):
                data = parse_vless_trojan(link, "vless")
                if data: json_output.append(data)
                
            elif link.startswith("trojan://"):
                data = parse_vless_trojan(link, "trojan")
                if data: json_output.append(data)
                
            elif link.startswith("ss://"):
                # برای شدوساکس فعلا خود لینک را نگه می‌داریم یا می‌توان پارسر اضافه کرد
                json_output.append({"protocol": "shadowsocks", "link": link})

        # ذخیره فایل نهایی
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=4, ensure_ascii=False)
            
        print(f"Done! Converted {len(json_output)} configs to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
