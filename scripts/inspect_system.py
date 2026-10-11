import re
import os
import json
import urllib.request
import urllib.error
import socket
from collections import defaultdict

socket.setdefaulttimeout(8)

with open('src/services/imageVerificationService.ts', 'r', encoding='utf-8') as f:
    ivs_content = f.read()

# Extract keys in VERIFIED_HERITAGE_IMAGE_REGISTRY
reg_blocks = re.findall(r"'([a-zA-Z0-9_\-]+)'\s*:\s*\{([^}]+name:[^}]+imageUrl:[^}]+)\}", ivs_content)
print(f"VERIFIED_HERITAGE_IMAGE_REGISTRY entries: {len(reg_blocks)}")

reg_items = {}
for reg_id, block in reg_blocks:
    name_m = re.search(r"name:\s*'([^']+)'", block)
    img_m = re.search(r"imageUrl:\s*'([^']+)'", block)
    source_m = re.search(r"source:\s*'([^']+)'", block)
    reg_items[reg_id] = {
        'name': name_m.group(1) if name_m else '',
        'imageUrl': img_m.group(1) if img_m else '',
        'source': source_m.group(1) if source_m else ''
    }

with open('scripts/extracted_places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

print(f"Total places extracted: {len(places)}")

# Let's map how many places are covered by imageVerificationService
covered = 0
for p in places:
    if p['id'] in reg_items:
        covered += 1

print(f"Places covered by VERIFIED_HERITAGE_IMAGE_REGISTRY: {covered}/{len(places)}")

# Analyze all unique URLs across places
all_urls = set(p['imageUrl'] for p in places if p['imageUrl'])
print(f"Total unique URLs in places: {len(all_urls)}")

# Check duplicate usage in places
url_to_places = defaultdict(list)
for p in places:
    url = p['imageUrl']
    if url:
        url_to_places[url].append(p)

duplicated_urls = {k: v for k, v in url_to_places.items() if len(v) > 1}
print(f"URLs shared across multiple places: {len(duplicated_urls)}")

with open('scripts/duplicated_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_places': len(places),
        'unique_urls': len(all_urls),
        'duplicated_urls': [
            {'url': k, 'count': len(v), 'places': [{'id': p['id'], 'name': p['name'], 'province': p['province'], 'file': p['file']} for p in v]}
            for k, v in sorted(duplicated_urls.items(), key=lambda x: -len(x[1]))
        ]
    }, f, ensure_ascii=False, indent=2)

print("Saved duplicated analysis to scripts/duplicated_analysis.json")
