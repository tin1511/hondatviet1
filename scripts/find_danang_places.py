import json
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/extracted_places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

danang_places = [p for p in places if 'đà nẵng' in p['province'].lower() or 'da nang' in p['province'].lower()]

print(f"Total Đà Nẵng places across all data files: {len(danang_places)}")
for p in danang_places:
    print(f"- [{p['id']}] {p['name']} (file: {p['file']})")
    print(f"    Current imageUrl: {p['imageUrl']}")
