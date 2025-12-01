import requests
import base64
import json
from urllib.parse import urlparse, parse_qs, unquote

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
        # Base64 استاندارد (نه URLsafe)
        return base64.b64decode(data).decode('utf-8')
    except:
        return data

def parse_vmess(vmess_url):
    """تبدیل لینک vmess به دیکشنری و دیکد کردن نام (ps)"""
    try:
        # حذف پیشوند vmess://
        b64_part = vmess_url.replace("vmess://", "")
        json_str = decode_base64(b64_part)
        data = json.loads(json_str)
        # دیکد کردن remark (نام)
        if 'ps' in data:
            data['ps'] = unquote(data['ps'])
        return data
    except Exception:
        return None

def parse_vless_trojan(url, protocol):
    """استخراج اطلاعات از لینک vless یا trojan و دیکد کردن نام (fragment)"""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # نام (Remarks) معمولاً در fragment قرار دارد و باید unquote شود
        name = unquote(parsed.fragment) if parsed.fragment else "No Name"

        # دیکد کردن پارامترهای دیگر (مانند host, path و ...)
        processed_params = {k: unquote(v[0]) for k, v in params.items()}
        
        return {
            "protocol": protocol,
            "uuid": parsed.username if parsed.username else "",
            "address": unquote(parsed.hostname),
            "port": parsed.port,
            "name": name,
            "params": processed_params
        }
    except Exception:
        return None

def main():
    print(f"Fetching from: {SUB_URL}")
    try:
        response = requests.get(SUB_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        # تلاش برای دیکد کردن محتوای کلی سابسکرایب
        decoded_content = decode_base64(content)
        
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
                
            # می‌توانید شرط‌های دیگری برای ss یا shadowsocks اضافه کنید.

        # ذخیره خروجی در فایل JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # از ensure_ascii=False برای نمایش صحیح ایموجی و حروف فارسی استفاده می‌شود
            json.dump(json_output, f, indent=4, ensure_ascii=False)
            
        print(f"Done! Converted {len(json_output)} configs to {OUTPUT_FILE} (JSON format).")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
