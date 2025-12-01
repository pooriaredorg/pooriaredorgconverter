import requests
import base64
from urllib.parse import unquote

# لینک سابسکرایب شما
SUB_URL = "https://raw.githubusercontent.com/pooriaredorg/pooriaredorg/refs/heads/main/configs/proxy_configs.txt"
OUTPUT_FILE = 'sub_config.json' # نام فایل خروجی طبق درخواست شما

def decode_base64_safe(data):
    """دیکد کردن محتوای اولیه با مدیریت خطا"""
    data = data.strip()
    try:
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except:
        return data

def clean_links(link):
    """اصلاح نام (Remark) با دیکد کردن کاراکترهای درصد دار و حفظ ساختار لینک"""
    try:
        # unquote کردن برای تبدیل %F0%9F... به ایموجی و متن خوانا
        return unquote(link)
    except:
        return link

def main():
    print(f"Fetching from: {SUB_URL}")
    try:
        response = requests.get(SUB_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        decoded_content = decode_base64_safe(content)
        
        links = decoded_content.splitlines()
        cleaned_links = []
        
        for link in links:
            link = link.strip()
            if not link: continue
            
            # فقط لینک‌های Vmess/Vless/Trojan/SS را تمیز و حفظ می‌کنیم
            if link.startswith(("vmess://", "vless://", "trojan://", "ss://")):
                cleaned_links.append(clean_links(link))
            else:
                pass 

        if not cleaned_links:
            print("No valid links found!")
            return

        # ساخت یک رشته واحد از همه لینک‌ها
        final_string = "\n".join(cleaned_links)
        
        # Base64 کردن کل محتوا (این همان محتوایی است که V2Box می‌خواند)
        final_base64 = base64.b64encode(final_string.encode('utf-8')).decode('utf-8')

        # ذخیره در فایل JSON (با محتوای Base64)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_base64)
            
        print(f"Success! Created functional subscription file named {OUTPUT_FILE}.")

    except Exception as e:
        print(f"Critical Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
