import requests
import io
import json
import tempfile
import os

# Login
print("Logging in...")
res = requests.post('https://factory-backend-demo.onrender.com/auth/web/login/', 
                    json={'phone_number': '+998912223344', 'password': '1'})
token = res.json().get('access')
headers = {'Authorization': f'Bearer {token}'}

print(f"✅ Login successful")
print(f"Token: {token[:50]}...\n")

# Create test files
test_files = [
    ("test_image_1.jpg", b"fake image content 1", "image/jpeg"),
    ("test_image_2.jpg", b"fake image content 2", "image/jpeg"),
    ("test_document.pdf", b"fake pdf content", "application/pdf"),
]

uploaded_ids = []

for filename, content, content_type in test_files:
    print(f"Uploading {filename}...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, 'rb') as f:
            files = {
                'file': (filename, f, content_type)
            }
            
            upload_res = requests.post(
                'https://factory-backend-demo.onrender.com/files/upload/',
                headers=headers,
                files=files
            )
        
        if upload_res.status_code in [200, 201]:
            file_data = upload_res.json()
            file_id = file_data.get('id')
            uploaded_ids.append(file_id)
            print(f"  ✅ Uploaded: {file_id}")
        else:
            print(f"  ❌ Failed: {upload_res.status_code}")
            print(f"     Response: {upload_res.text[:200]}")
    finally:
        os.unlink(tmp_path)

print("\n" + "="*80)
print("UPLOADED FILE IDs:")
print("="*80)
print(json.dumps(uploaded_ids, indent=2))
print("\nCopy these IDs to use in tests!")
