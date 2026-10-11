import urllib.request, urllib.parse, json, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'HonDatVietApp/1.0 (https://hondatviet.vn)'}
# Check both vi and en Wikipedia for Dragon Bridge
for lang, title in [('vi', 'Cầu Rồng (Đà Nẵng)'), ('en', 'Dragon Bridge (Da Nang)')]:
    url = f'https://{lang}.wikipedia.org/w/api.php?action=query&prop=pageimages|images&titles={urllib.parse.quote(title)}&pithumbsize=1200&format=json'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                print(f"[{lang}] {pdata.get('title')}: thumbnail = {pdata.get('thumbnail', {}).get('source')}")
                images = [img['title'] for img in pdata.get('images', [])]
                print(f"      images count = {len(images)}: {images[:5]}")
    except Exception as e:
        print(f"Error {lang}: {e}")
