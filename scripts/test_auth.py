import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import json

BASE_URL = "http://localhost:8000"
API_KEY  = "trainradar-secret-key-2026"

print("=" * 50)
print("TrainRadar - Auth Tests")
print("=" * 50)
print()

# Test 1 — No key
print("Test 1 — No API key (should fail)...")
try:
    urllib.request.urlopen(f"{BASE_URL}/positions")
    print("  ❌ Should have been blocked!")
except urllib.error.HTTPError as e:
    print(f"  ✅ Blocked! Status: {e.code}")

# Test 2 — Wrong key
print()
print("Test 2 — Wrong API key (should fail)...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/positions",
        headers={"X-API-Key": "wrong-key"}
    )
    urllib.request.urlopen(req)
    print("  ❌ Should have been blocked!")
except urllib.error.HTTPError as e:
    print(f"  ✅ Blocked! Status: {e.code}")

# Test 3 — Correct key
print()
print("Test 3 — Correct API key (should work)...")
try:
    req = urllib.request.Request(
        f"{BASE_URL}/positions",
        headers={"X-API-Key": API_KEY}
    )
    r = urllib.request.urlopen(req)
    data = json.loads(r.read())
    print(f"  ✅ Got {len(data)} positions!")
    for p in data:
        print(f"     {p['train_id']} → {p['latitude']}, {p['longitude']}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 4 — Health check (no key needed)
print()
print("Test 4 — Health check (no key needed)...")
try:
    r = urllib.request.urlopen(f"{BASE_URL}/health")
    data = json.loads(r.read())
    print(f"  ✅ Status: {data['status']}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()
print("=" * 50)
print("Auth tests complete!")
print("=" * 50)