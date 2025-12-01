import requests
import base64
import re
from urllib.parse import urlparse, unquote

# لینک سابسکرایب شما
SUB_URL = "https://raw.githubusercontent.com/pooriaredorg/pooriaredorg/refs/heads/main/configs/proxy_configs.txt"

# نام فایل خروجی (فرمت txt برای سابسکرایب استاندارد بهتر است)
OUTPUT_FILE = 'sub_config.txt'

def decode_base64(data):
    """دیکد کردن محتوای اولیه اگر بیس ۶۴ باشد"""
    data = data.strip()
    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except:
        return data

def clean_vmess(link):
    """اصلاح نام در لینک‌های vmess"""
    try:
        # لینک vmess معمولا خودش یک json بیس ۶۴ است
        # ما اینجا فقط خود لینک را برمی‌گردانیم چون vmess استاندارد است
        # اما اگر بخواهیم نام را عوض کنیم باید دیکد و انکد شود که پیچیده است
        # پس خود لینک را سالم برمی‌گردانیم
        return link
    except:
        return None

def clean_vless_trojan(link):
    """اصلاح نام (Remark) در لینک‌های vless و trojan"""
    try:
        # دیکد کردن کاراکترهای درصد دار (%F0...) به ایموجی و متن
        decoded_link = unquote(link) 
        return decoded_link
    except:
        return link

def main():
    print(f"Fetching from: {SUB_URL}")
    try:
        response = requests.get(SUB_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        decoded_content = decode_base64(content)
        
        links = decoded_content.splitlines()
        cleaned_links = []
        
        for link in links:
            link = link.strip()
            if not link: continue
            
            # پردازش لینک‌ها برای اصلاح نام‌های بهم ریخته
            if link.startswith("vmess://"):
                cleaned_links.append(link) # Vmess معمولا نیازی به unquote ندارد
            elif link.startswith("vless://") or link.startswith("trojan://") or link.startswith("ss://"):
                cleaned_links.append(clean_vless_trojan(link))
            else:
                pass # خطوط نامعتبر را نادیده می‌گیریم

        if not cleaned_links:
            print("No valid links found!")
            return

        # اتصال همه لینک‌ها با خط جدید
        final_string = "\n".join(cleaned_links)
        
        # تبدیل کل محتوا به Base64 (استاندارد سابسکرایب)
        final_base64 = base64.b64encode(final_string.encode('utf-8')).decode('utf-8')

        # ذخیره در فایل
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_base64)
            
        print(f"Successfully created subscription compatible with V2Box/Hiddify.")
        print(f"Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
