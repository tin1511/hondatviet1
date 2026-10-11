import re
import json
import sys
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('src/services/imageVerificationService.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Match entries in VERIFIED_HERITAGE_IMAGE_REGISTRY
# Each entry starts with 'key': { ... }
# Let's extract between "export const VERIFIED_HERITAGE_IMAGE_REGISTRY" and the closing "};"
start_idx = content.find('export const VERIFIED_HERITAGE_IMAGE_REGISTRY')
end_idx = content.find('\nexport function getVerifiedHeritageImageData', start_idx)
registry_block = content[start_idx:end_idx]

entries = re.finditer(r"'([a-zA-Z0-9_\-]+)'\s*:\s*\{", registry_block)
indices = [m.start() for m in entries]
indices.append(len(registry_block))

registry_items = []
urls = defaultdict(list)

for i in range(len(indices) - 1):
    chunk = registry_block[indices[i]:indices[i+1]]
    key_m = re.search(r"'([a-zA-Z0-9_\-]+)'\s*:\s*\{", chunk)
    id_m = re.search(r"id:\s*'([^']+)'", chunk)
    name_m = re.search(r"name:\s*'([^']+)'", chunk)
    prov_m = re.search(r"province:\s*'([^']+)'", chunk)
    img_m = re.search(r"imageUrl:\s*'([^']+)'", chunk)
    src_m = re.search(r"source:\s*'([^']+)'", chunk)
    
    if key_m and id_m and img_m:
        item = {
            'key': key_m.group(1),
            'id': id_m.group(1),
            'name': name_m.group(1) if name_m else '',
            'province': prov_m.group(1) if prov_m else '',
            'imageUrl': img_m.group(1),
            'source': src_m.group(1) if src_m else ''
        }
        registry_items.append(item)
        urls[item['imageUrl']].append(item)

print(f"Registry total parsed items: {len(registry_items)}")
print(f"Registry unique URLs: {len(urls)}")

dups = {k: v for k, v in urls.items() if len(v) > 1}
print(f"Registry duplicated URLs: {len(dups)}")
for url, p_list in sorted(dups.items(), key=lambda x: -len(x[1])):
    print(f"\nURL ({len(p_list)} places): {url}")
    for it in p_list:
        print(f"   - {it['id']}: {it['name']} ({it['province']})")

with open('scripts/registry_items.json', 'w', encoding='utf-8') as f:
    json.dump(registry_items, f, ensure_ascii=False, indent=2)
