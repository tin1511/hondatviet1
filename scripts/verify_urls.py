import json
import urllib.request
import urllib.error
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('scripts/registry_items.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Testing {len(items)} registry URLs...")

headers = {
    'User-Agent': 'HonDatVietApp/1.0 (https://hondatviet.vn; contact@hondatviet.vn) Mozilla/5.0'
}

results = []

for idx, it in enumerate(items):
    url = it['imageUrl']
    req = urllib.request.Request(url, headers=headers)
    req.get_method = lambda: 'HEAD'
    
    status = None
    content_type = None
    error_msg = None
    
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            status = resp.status
            content_type = resp.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        status = e.code
        error_msg = str(e)
    except Exception as e:
        status = 0
        error_msg = str(e)
        
    results.append({
        'id': it['id'],
        'name': it['name'],
        'url': url,
        'status': status,
        'content_type': content_type,
        'error': error_msg
    })
    
    if (idx + 1) % 20 == 0 or idx == len(items) - 1:
        print(f"Tested {idx+1}/{len(items)} items...")
    time.sleep(0.05)

with open('scripts/url_verification_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok_count = sum(1 for r in results if r['status'] == 200)
err_count = sum(1 for r in results if r['status'] != 200)
print(f"\nVerification summary:")
print(f"  OK (200): {ok_count}")
print(f"  FAILED:   {err_count}")

failed_items = [r for r in results if r['status'] != 200]
for f_it in failed_items[:20]:
    print(f"  - [{f_it['status']}] {f_it['id']} ({f_it['name']}): {f_it['url']} ({f_it['error']})")
if len(failed_items) > 20:
    print(f"  ... and {len(failed_items)-20} more failed")
