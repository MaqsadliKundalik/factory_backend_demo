import requests
import json

# Login
print("Logging in...")
res = requests.post('https://factory-backend-demo.onrender.com/auth/web/login/', 
                    json={'phone_number': '+998912223344', 'password': '1'})

if res.status_code != 200:
    print(f"❌ Login failed: {res.status_code}")
    exit(1)

token = res.json().get('access')
headers = {'Authorization': f'Bearer {token}'}
print(f"✅ Login successful\n")

# Get excavator sub-orders (they have before_files and after_files)
print("Fetching excavator sub-orders to find file IDs...")
url = 'https://factory-backend-demo.onrender.com/excavator-order/sub-orders/'
res = requests.get(url, headers=headers, params={'page_size': 50})

if res.status_code != 200:
    print(f"❌ Failed: {res.status_code}")
    print(res.text[:500])
    exit(1)

data = res.json()
sub_orders = data.get('results', [])
print(f"Found {len(sub_orders)} sub-orders\n")

# Collect all file IDs from sub-orders
all_file_ids = set()

for sub in sub_orders:
    before_files = sub.get('before_files', [])
    after_files = sub.get('after_files', [])
    
    if before_files or after_files:
        print(f"Sub-order {sub.get('id', 'N/A')[:8]}...")
        print(f"  before_files: {len(before_files)} files")
        print(f"  after_files: {len(after_files)} files")
        
        # Extract file IDs
        for f in before_files:
            if isinstance(f, dict) and 'id' in f:
                all_file_ids.add(f['id'])
            elif isinstance(f, str):
                all_file_ids.add(f)
        
        for f in after_files:
            if isinstance(f, dict) and 'id' in f:
                all_file_ids.add(f['id'])
            elif isinstance(f, str):
                all_file_ids.add(f)

file_ids_list = list(all_file_ids)

print(f'\n{"="*80}')
print(f'TOTAL UNIQUE FILE IDs FOUND: {len(file_ids_list)}')
print('='*80)

if file_ids_list:
    print('\nFile IDs (for copy-paste):')
    print(json.dumps(file_ids_list, indent=2))
else:
    print("\n⚠️ No file IDs found in excavator sub-orders")
    print("\nYou can:")
    print("1. Upload files via Swagger UI at: https://factory-backend-demo.onrender.com/swagger/")
    print("2. Or use the mobile app to upload files")
