import requests
import base64
import json
from urllib.parse import urlparse, parse_qs, unquote

# لینک سابسکرایب خام حاوی لینک‌های vmess/vless/trojan
SOURCE_SUB_URL = "https://raw.githubusercontent.com/pooriaredorg/pooriaredorg/refs/heads/main/configs/proxy_configs.txt"

# نام فایل خروجی (مانند تصویر شما)
OUTPUT_FILE = 'sub_config.json' 

def decode_base64_safe(data):
    """دیکد کردن محتوای Base64"""
    data = data.strip()
    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except:
        return data

def parse_vless_trojan(url, protocol):
    """تبدیل لینک VLESS/Trojan به آبجکت JSON با نام دیکد شده"""
    try:
        # لینک را دیکد نمی‌کنیم تا پارس کردن صحیح باشد، فقط Fragment را دیکد می‌کنیم.
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # اصلاح و دیکد کردن نام (Fragment) - این کاراکترهای %F0%9F را به ایموجی/متن تبدیل می‌کند
        tag_name = unquote(parsed.fragment) if parsed.fragment else f"{protocol.upper()}-{parsed.hostname}"

        # ساخت آبجکت JSON مطابق با ساختار Xray
        proxy_object = {
            "protocol": protocol,
            "uuid": parsed.username if parsed.username else "",
            "address": parsed.hostname,
            "port": parsed.port,
            "name": tag_name, # نام اصلاح شده
            "params": {}
        }
        
        # افزودن پارامترها
        for key, value in params.items():
            # دیکد کردن مقادیر
            proxy_object['params'][key] = unquote(value[0])
            
        return proxy_object
    except Exception:
        return None

def main():
    print(f"Fetching raw links from: {SOURCE_SUB_URL}")
    try:
        response = requests.get(SOURCE_SUB_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        decoded_content = decode_base64_safe(content)
        
        links = decoded_content.splitlines()
        json_output = []
        
        for link in links:
            link = link.strip()
            if not link: continue
            
            # تبدیل پروتکل‌ها
            if link.startswith(("vless://", "trojan://")):
                protocol = link.split(':')[0].replace("://", "")
                data = parse_vless_trojan(link, protocol)
                if data: json_output.append(data)
            # توجه: برای vmess:// نیاز به تابع parse_vmess (بیس‌64 مجزا) دارید که در اینجا به دلیل تمرکز بر VLESS/Trojan حذف شده است.
            
        # --- ذخیره خروجی به صورت آرایه JSON مجزا ---
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # خروجی نهایی یک آرایه [ {...}, {...}, ... ] است (۱۰ کانفیگ جداگانه)
            json.dump(json_output, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully created JSON array file: {len(json_output)} distinct configs.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
