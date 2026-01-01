import requests
import json
from requests.exceptions import RequestException, Timeout, ConnectionError

def format_address(address):
    if not address:
        return "N/A"
    return ", ".join(part.strip() for part in address.split("!") if part.strip())


def mask_id(id_number):
    if not id_number or len(id_number) < 4:
        return "N/A"
    return "*" * (len(id_number) - 4) + id_number[-4:]


def fetch_mobile_info(mobile):
    url = "https://zionix.rf.gd/land.php"

    params = {
        "type": "mobile",
        "term": mobile
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Connection": "close"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        if not data.get("data", {}).get("success"):
            print("❌ No data found")
            return

        results = data["data"].get("result", [])

        if not results:
            print("❌ Empty result")
            return

        print("\n📞 MOBILE INFORMATION")
        print("=" * 60)

        for i, record in enumerate(results, start=1):
            print(f"\n🔹 Record {i}")
            print("-" * 60)
            print(f"📱 Mobile       : {record.get('mobile', 'N/A')}")
            print(f"👤 Name         : {record.get('name', 'N/A')}")
            print(f"👨 Father Name : {record.get('father_name', 'N/A')}")
            print(f"🏠 Address     : {format_address(record.get('address'))}")
            print(f"📞 Alt Mobile  : {record.get('alt_mobile', 'N/A')}")
            print(f"📡 Circle      : {record.get('circle', 'N/A')}")
            print(f"🆔 ID Number   : {mask_id(record.get('id_number'))}")
            print(f"📧 Email       : {record.get('email') or 'N/A'}")

        print("\n✅ Finished Successfully")

    except Timeout:
        print("❌ Request timed out (server slow or blocked)")
    except ConnectionError:
        print("❌ Server closed connection (free hosting / rate limit)")
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from server")
    except RequestException as e:
        print("❌ API Error:", e)


if __name__ == "__main__":
    mobile_number = input("📲 Enter Indian Mobile Number: ").strip()
    fetch_mobile_info(mobile_number)