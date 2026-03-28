import requests
import json

# Login
print("Logging in...")
res = requests.post('https://factory-backend-demo.onrender.com/auth/web/login/', 
                    json={'phone_number': '+998912223344', 'password': '1'})

if res.status_code != 200:
    print(f"❌ Login failed: {res.status_code}")
    print(res.text)
    exit(1)

token = res.json().get('access')
print(f"✅ Login successful\n")

# Get files from different endpoints
headers = {'Authorization': f'Bearer {token}'}

endpoints = [
    '/files/',
    '/files/documents/',
]

all_files = []

for endpoint in endpoints:
    print(f"Checking {endpoint}...")
    url = f'https://factory-backend-demo.onrender.com{endpoint}'
    files_res = requests.get(url, headers=headers, params={'page_size': 50})
    
    if files_res.status_code == 200:
        data = files_res.json()
        files = data.get('results', [])
        print(f"  Found {len(files)} items")
        all_files.extend(files)
    else:
        print(f"  ❌ Failed: {files_res.status_code}")

print(f'\n{"="*80}')
print(f'TOTAL FILES FOUND: {len(all_files)}')
print('='*80)

if all_files:
    for i, f in enumerate(all_files[:10], 1):  # Show first 10
        print(f"\n{i}. ID: {f.get('id', 'N/A')}")
        print(f"   Name: {f.get('name', f.get('file', 'N/A'))}")
        print(f"   Type: {f.get('file_type', f.get('type', 'N/A'))}")
        if 'file' in f:
            print(f"   URL: {f['file'][:80]}...")
    
    if len(all_files) > 10:
        print(f"\n... and {len(all_files) - 10} more files")
    
    # Print just IDs for easy copy-paste
    print(f'\n{"="*80}')
    print('FILE IDs (for copy-paste):')
    print('='*80)
    file_ids = [f.get('id') for f in all_files if f.get('id')]
    print(json.dumps(file_ids[:10], indent=2))  # First 10 IDs
    
    if len(file_ids) > 10:
        print(f"\n... and {len(file_ids) - 10} more IDs")
else:
    print("\n⚠️ No files found in the system")
