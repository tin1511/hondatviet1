import urllib.request
import urllib.parse
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'HonDatVietApp/1.0 (https://hondatviet.vn; contact@hondatviet.vn)'
}

def get_wiki_image(title, lang='vi'):
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=1200&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'thumbnail' in pdata:
                    return pdata['thumbnail']['source'], pdata.get('title')
    except Exception as e:
        print(f"Error {lang} {title}: {e}")
    return None, None

def search_commons_image(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1200&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                imageinfo = pdata.get('imageinfo', [])
                if imageinfo:
                    info = imageinfo[0]
                    thumb = info.get('thumburl') or info.get('url')
                    title = pdata.get('title')
                    # filter out flags, icons, logos, maps
                    lower = title.lower()
                    if not any(w in lower for w in ['icon', 'logo', 'flag', 'map', 'symbol', 'seal', 'locator']):
                        return thumb, title
    except Exception as e:
        print(f"Error commons {query}: {e}")
    return None, None

test_places = [
    ('Cầu Rồng (Đà Nẵng)', 'Cầu Rồng Đà Nẵng'),
    ('Bà Nà Hills', 'Bà Nà Hills Cầu Vàng'),
    ('Chùa Linh Ứng Bãi Bụt', 'Chùa Linh Ứng Đà Nẵng'),
    ('Bãi biển Mỹ Khê', 'Mỹ Khê Đà Nẵng'),
    ('Ngũ Hành Sơn', 'Ngũ Hành Sơn'),
    ('Bảo tàng Điêu khắc Chăm Đà Nẵng', 'Bảo tàng Chăm Đà Nẵng'),
    ('Thành Điện Hải', 'Thành Điện Hải'),
    ('Cầu Sông Hàn', 'Cầu quay Sông Hàn'),
    ('Đỉnh Bàn Cờ', 'Đỉnh Bàn Cờ Sơn Trà')
]

for title, q in test_places:
    img, found_title = get_wiki_image(title, 'vi')
    if not img:
        img, found_title = search_commons_image(q)
    print(f"{title} -> {found_title}: {img}")
