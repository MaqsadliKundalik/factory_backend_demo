import requests
import json

# Loyihaning URL manzili (Lokal yoki Render)
BASE_URL = "https://factory-backend-demo.onrender.com"  # Yoki "http://localhost:8000"

def run_demo():
    print("--- API Demo Boshlandi ---")

    # 1. Login (Web platformasi uchun)
    login_url = f"{BASE_URL}/auth/web/login/"
    login_data = {
        "phone_number": "+998912223344",
        "password": "admin123"
    }

    print(f"\n1. Login qilinmoqda: {login_data['phone_number']}")
    res_login = requests.post(login_url, json=login_data)
    
    if res_login.status_code != 200:
        print(f"Xatolik: {res_login.status_code}")
        print(res_login.text)
        return

    tokens = res_login.json()
    access_token = tokens['access_token']
    print("Login muvaffaqiyatli! Access token olindi.")

    # Headerlar (Barcha keyingi so'rovlar uchun)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 2. Profilni tekshirish
    profile_url = f"{BASE_URL}/auth/web/me/"
    print("\n2. Profil ma'lumotlari olinmoqda...")
    res_profile = requests.get(profile_url, headers=headers)
    print(f"Profil: {json.dumps(res_profile.json(), indent=2)}")

    # 3. Mahsulot yaratish (On-the-fly turlari bilan)
    # Eslatma: 'types' va 'unit' agar bazada bo'lmasa, on-the-fly yaratiladi
    product_url = f"{BASE_URL}/products/products/"
    product_data = {
        "name": "Yangi Mahsulot Test",
        "types": ["Suyuq", "Yuvuvchi"],  # Ismi bo'yicha (bazada bo'lmasa yaratiladi)
        "unit": "Litr"                   # Ismi bo'yicha (bazada bo'lmasa yaratiladi)
    }

    print(f"\n3. Yangi mahsulot yaratilmoqda: {product_data['name']}")
    res_product = requests.post(product_url, json=product_data, headers=headers)
    
    if res_product.status_code in [201, 200]:
        print("Mahsulot muvaffaqiyatli yaratildi!")
        print(json.dumps(res_product.json(), indent=2))
    else:
        print(f"Xatolik: {res_product.status_code}")
        print(res_product.text)

    # 4. Transporslar ro'yxatini ko'rish
    transport_url = f"{BASE_URL}/transports/"
    print("\n4. Transportlar ro'yxati tekshirilmoqda...")
    res_transports = requests.get(transport_url, headers=headers)
    print(f"Transportlar soni: {len(res_transports.json())}")

if __name__ == "__main__":
    run_demo()
