import requests
import base64
import json
from urllib.parse import urlparse, parse_qs, unquote

# لینک سابسکرایب خام حاوی لینک‌های vmess/vless/trojan
SOURCE_SUB_URL = "https://raw.githubusercontent.com/pooriaredorg/pooriaredorg/refs/heads/main/configs/proxy_configs.txt"

# نام فایل خروجی (باید با لینک نهایی شما مطابقت داشته باشد)
OUTPUT_FILE = 'singbox_configs.json' 

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

def map_vless_to_xray(url):
    """تبدیل لینک VLESS به ساختار Outbound هسته Xray"""
    try:
        parsed = urlparse(unquote(url))
        params = parse_qs(parsed.query)
        
        # اصلاح نام (tag)
        tag_name = unquote(parsed.fragment) if parsed.fragment else f"VLESS-{parsed.hostname}"
        
        # --- تنظیمات Stream (شبکه و امنیت) ---
        network_type = params.get('type', ['tcp'])[0]
        security_type = params.get('security', [''])[0]
        
        stream_settings = {"network": network_type}
        
        # تنظیمات TLS
        if security_type in ('tls', 'xtls', 'reality'):
            stream_settings["security"] = "tls"
            stream_settings["tlsSettings"] = {
                "serverName": params.get('sni', [parsed.hostname])[0],
                "allowInsecure": params.get('allowInsecure', ['0'])[0] == '1'
            }

        # تنظیمات WebSocket
        if network_type == 'ws':
            stream_settings["wsSettings"] = {
                "path": params.get('path', ['/'])[0],
                "headers": {"Host": params.get('host', [parsed.hostname])[0]}
            }
        
        # --- ساخت Outbound نهایی ---
        outbound = {
            "tag": tag_name,
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": parsed.hostname,
                    "port": parsed.port,
                    "users": [{
                        "id": parsed.username,
                        "flow": params.get('flow', [''])[0],
                        "encryption": "none"
                    }]
                }]
            },
            "streamSettings": stream_settings,
            "mux": {"enabled": False} 
        }
        
        return outbound
    except Exception as e:
        print(f"Error mapping VLESS to Xray: {e}")
        return None

def main():
    print(f"Fetching raw links from: {SOURCE_SUB_URL}")
    try:
        response = requests.get(SOURCE_SUB_URL, timeout=30)
        response.raise_for_status()
        
        content = response.text.strip()
        decoded_content = decode_base64_safe(content)
        
        links = decoded_content.splitlines()
        outbounds = []
        
        for link in links:
            link = link.strip()
            if not link: continue
            
            # تبدیل پروتکل‌ها
            if link.startswith("vless://"):
                data = map_vless_to_xray(link)
                if data: outbounds.append(data)
            # شما باید توابع map_vmess_to_xray و map_trojan_to_xray را نیز اضافه کنید
            
        # --- ساختار کامل Xray JSON (Full Config) ---
        final_config = {
            "log": {"loglevel": "warning"},
            "dns": {
                "servers": [{"address": "8.8.8.8", "tag": "dns-remote"}]
            },
            "inbounds": [
                {"protocol": "socks", "listen": "127.0.0.1", "port": 10808, "tag": "socks-in"},
                {"protocol": "http", "listen": "127.0.0.1", "port": 10809, "tag": "http-in"}
            ],
            "outbounds": outbounds + [
                {"protocol": "freedom", "tag": "direct"},
                {"protocol": "blackhole", "tag": "block"}
            ],
            "routing": {
                "rules": [
                    {"type": "field", "outboundTag": "block", "domain": ["geosite:category-ads-all"]},
                    {"type": "field", "outboundTag": "direct", "network": "tcp,udp"}
                ],
                "domainStrategy": "AsIs"
            }
        }
        
        # ذخیره خروجی در فایل JSON
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_config, f, indent=4, ensure_ascii=False)
            
        print(f"Successfully created full Xray JSON file: {len(outbounds)} proxies.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
