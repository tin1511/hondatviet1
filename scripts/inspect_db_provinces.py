import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/heritage_db_items.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total HERITAGE_DATABASE items: {len(items)}")
provinces = {}
for it in items:
    p = it['province']
    provinces[p] = provinces.get(p, 0) + 1

print(f"Provinces covered ({len(provinces)}):")
for p, c in sorted(provinces.items(), key=lambda x: -x[1]):
    print(f"  {p}: {c} places")
