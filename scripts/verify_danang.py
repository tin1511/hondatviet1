import urllib.request
import urllib.parse
import json
import time
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'HonDatVietApp/1.0 (https://hondatviet.vn; contact@hondatviet.vn) Mozilla/5.0'
}

def query_commons(search_term):
    """Search Wikimedia Commons for images matching the term."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(search_term)}&gsrnamespace=6&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=1280&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            candidates = []
            for pid, pdata in pages.items():
                title = pdata.get('title', '')
                lower = title.lower()
                # filter out icons, logos, flags, svg, maps, buttons, diagrams
                if any(w in lower for w in ['icon', 'logo', 'flag', 'map', 'symbol', 'seal', 'button', 'diagram', '.svg']):
                    continue
                imageinfo = pdata.get('imageinfo', [])
                if imageinfo:
                    info = imageinfo[0]
                    mime = info.get('mime', '')
                    if not mime.startswith('image/'):
                        continue
                    thumb = info.get('thumburl') or info.get('url')
                    orig = info.get('url')
                    meta = info.get('extmetadata', {})
                    lic = meta.get('LicenseShortName', {}).get('value', 'CC BY-SA')
                    artist = meta.get('Artist', {}).get('value', 'Wikimedia Commons')
                    # strip html tags from artist
                    import re
                    clean_artist = re.sub(r'<[^>]+>', '', artist).strip()
                    desc = meta.get('ImageDescription', {}).get('value', '')
                    clean_desc = re.sub(r'<[^>]+>', '', desc).strip()
                    
                    candidates.append({
                        'title': title,
                        'thumbUrl': thumb,
                        'origUrl': orig,
                        'license': lic,
                        'artist': clean_artist[:100],
                        'description': clean_desc[:200]
                    })
            return candidates
    except Exception as e:
        print(f"Error querying {search_term}: {e}")
        return []

def query_wikipedia(title, lang='vi'):
    """Query Wikipedia page thumbnail and images."""
    url = f"https://{lang}.wikipedia.org/w/api.php?action=query&prop=pageimages|extracts&titles={urllib.parse.quote(title)}&pithumbsize=1280&format=json"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, pdata in pages.items():
                if 'thumbnail' in pdata:
                    thumb = pdata['thumbnail']['source']
                    return {
                        'title': pdata.get('title'),
                        'thumbUrl': thumb,
                        'source': f"{lang.upper()} Wikipedia: {pdata.get('title')}",
                        'license': 'Wikimedia CC BY-SA'
                    }
    except Exception as e:
        pass
    return None

def test_url_status(url):
    """Check if URL returns 200 OK and image mime."""
    req = urllib.request.Request(url, headers=headers)
    req.get_method = lambda: 'HEAD'
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.headers.get('Content-Type', '')
    except Exception as e:
        # Retry with GET in case HEAD is not allowed
        try:
            req_get = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_get, timeout=5) as resp:
                return resp.status, resp.headers.get('Content-Type', '')
        except Exception as e2:
            return 0, str(e2)

# Test search for Da Nang places
danang_search_specs = [
    {
        'id': 'dn-cau-rong-song-han',
        'name': 'Cầu Rồng Sông Hàn',
        'wiki_terms': ['Dragon Bridge (Da Nang)', 'Cầu Rồng (Đà Nẵng)'],
        'commons_terms': ['Dragon Bridge Da Nang', 'Cầu Rồng Đà Nẵng']
    },
    {
        'id': 'dn-cau-vang-bana',
        'name': 'Cầu Vàng Bà Nà Hills',
        'wiki_terms': ['Golden Bridge (Vietnam)', 'Cầu Vàng (Đà Nẵng)'],
        'commons_terms': ['Golden Bridge Ba Na Hills', 'Cầu Vàng Đà Nẵng']
    },
    {
        'id': 'dn-bana-hills-resort',
        'name': 'Quần Thể Du Lịch Sun World Ba Na Hills',
        'wiki_terms': ['Bà Nà Hills'],
        'commons_terms': ['Ba Na Hills cable car', 'Ba Na Hills Da Nang']
    },
    {
        'id': 'dn-lang-phap-bana',
        'name': 'Làng Pháp & Hầm Rượu Debay Bà Nà',
        'wiki_terms': [],
        'commons_terms': ['French Village Ba Na Hills', 'Debay wine cellar Ba Na']
    },
    {
        'id': 'dn-ban-dao-son-tra',
        'name': 'Khu Bảo Tồn Thiên Nhiên Bán Đảo Sơn Trà',
        'wiki_terms': ['Bán đảo Sơn Trà', 'Sơn Trà Mountain'],
        'commons_terms': ['Son Tra Peninsula', 'Bán đảo Sơn Trà']
    },
    {
        'id': 'dn-chua-linh-ung-son-tra',
        'name': 'Chùa Linh Ứng Bãi Bụt & Tượng Phật Quan Âm 67m',
        'wiki_terms': ['Chùa Linh Ứng'],
        'commons_terms': ['Linh Ung Pagoda Lady Buddha Da Nang', 'Chùa Linh Ứng Bãi Bụt Sơn Trà']
    },
    {
        'id': 'dn-dinh-ban-co',
        'name': 'Đỉnh Bàn Cờ Sơn Trà',
        'wiki_terms': [],
        'commons_terms': ['Dinh Ban Co Son Tra', 'Đỉnh Bàn Cờ Sơn Trà', 'Chessboard Peak Son Tra']
    },
    {
        'id': 'dn-cay-da-ngan-nam',
        'name': 'Cây Đa Di Sản Ngàn Năm Sơn Trà',
        'wiki_terms': [],
        'commons_terms': ['Son Tra banyan tree', 'Cây đa Sơn Trà']
    },
    {
        'id': 'dn-hai-dang-tien-sa',
        'name': 'Hải Đăng Tiên Sa Sơn Trà',
        'wiki_terms': [],
        'commons_terms': ['Tien Sa Lighthouse', 'Hải đăng Tiên Sa']
    },
    {
        'id': 'dn-nha-trung-bay-hoang-sa',
        'name': 'Nhà Trưng Bày Hoàng Sa',
        'wiki_terms': [],
        'commons_terms': ['Nha trung bay Hoang Sa Da Nang', 'Hoang Sa Exhibition House']
    },
    {
        'id': 'dn-ngu-hanh-son-complex',
        'name': 'Quần Thể Danh Thắng Di Tích Quốc Gia Đặc Biệt Ngũ Hành Sơn',
        'wiki_terms': ['Ngũ Hành Sơn', 'Marble Mountains (Vietnam)'],
        'commons_terms': ['Marble Mountains Da Nang', 'Ngũ Hành Sơn']
    },
    {
        'id': 'dn-dong-huyen-khong',
        'name': 'Động Huyền Không (Ngũ Hành Sơn)',
        'wiki_terms': [],
        'commons_terms': ['Huyen Khong Cave Marble Mountains', 'Động Huyền Không Ngũ Hành Sơn']
    },
    {
        'id': 'dn-chua-tam-thai',
        'name': 'Chùa Tam Thai (Ngũ Hành Sơn)',
        'wiki_terms': ['Chùa Tam Thai (Đà Nẵng)'],
        'commons_terms': ['Tam Thai Pagoda Da Nang', 'Chùa Tam Thai Ngũ Hành Sơn']
    },
    {
        'id': 'dn-lang-da-non-nuoc',
        'name': 'Làng Đá Mỹ Nghệ Non Nước',
        'wiki_terms': ['Non Nước (làng đá)'],
        'commons_terms': ['Non Nuoc stone carving village', 'Làng đá Non Nước']
    },
    {
        'id': 'dn-bai-bien-my-khe',
        'name': 'Bãi Biển Mỹ Khê Đà Nẵng',
        'wiki_terms': ['Bãi biển Mỹ Khê', 'My Khe Beach'],
        'commons_terms': ['My Khe Beach Da Nang', 'Bãi biển Mỹ Khê']
    },
    {
        'id': 'dn-bai-bien-non-nuoc',
        'name': 'Bãi Biển Non Nước',
        'wiki_terms': ['Bãi biển Non Nước'],
        'commons_terms': ['Non Nuoc Beach Da Nang', 'Bãi biển Non Nước']
    },
    {
        'id': 'dn-ran-nam-o',
        'name': 'Rạn Nam Ô & Làng Nghề Nước Mắm Nam Ô',
        'wiki_terms': [],
        'commons_terms': ['Ran Nam O Da Nang', 'Nam O reef', 'Nam O fish sauce']
    },
    {
        'id': 'dn-bao-tang-cham',
        'name': 'Bảo Tàng Điêu Khắc Chăm Đà Nẵng',
        'wiki_terms': ['Bảo tàng Điêu khắc Chăm Đà Nẵng', 'Museum of Cham Sculpture'],
        'commons_terms': ['Museum of Cham Sculpture Da Nang', 'Bảo tàng Chăm Đà Nẵng']
    },
    {
        'id': 'dn-thanh-dien-hai',
        'name': 'Di Tích Quốc Gia Đặc Biệt Thành Điện Hải & Bảo Tàng Đà Nẵng',
        'wiki_terms': ['Thành Điện Hải'],
        'commons_terms': ['Dien Hai Citadel Da Nang', 'Thành Điện Hải']
    },
    {
        'id': 'dn-bao-tang-my-thuat',
        'name': 'Bảo Tàng Mỹ Thuật Đà Nẵng',
        'wiki_terms': ['Bảo tàng Mỹ thuật Đà Nẵng'],
        'commons_terms': ['Da Nang Fine Arts Museum', 'Bảo tàng Mỹ thuật Đà Nẵng']
    },
    {
        'id': 'dn-nha-tho-chinh-toa',
        'name': 'Nhà Thờ Chính Tòa Đà Nẵng (Nhà Thờ Con Gà)',
        'wiki_terms': ['Nhà thờ chính tòa Đà Nẵng', 'Da Nang Cathedral'],
        'commons_terms': ['Da Nang Cathedral', 'Nhà thờ Chính tòa Đà Nẵng']
    },
    {
        'id': 'dn-cau-song-han-quay',
        'name': 'Cầu Quay Sông Hàn',
        'wiki_terms': ['Cầu Sông Hàn', 'Han River Bridge'],
        'commons_terms': ['Han River Bridge Da Nang', 'Cầu Sông Hàn']
    },
    {
        'id': 'dn-cau-thuan-phuoc',
        'name': 'Cầu Thuận Phước',
        'wiki_terms': ['Cầu Thuận Phước', 'Thuan Phuoc Bridge'],
        'commons_terms': ['Thuan Phuoc Bridge Da Nang', 'Cầu Thuận Phước']
    },
    {
        'id': 'dn-cau-tinh-yeu-ca-chep',
        'name': 'Cầu Tình Yêu & Tượng Cá Chép Hóa Rồng',
        'wiki_terms': [],
        'commons_terms': ['Dragon Carp Da Nang', 'Cá Chép Hóa Rồng Đà Nẵng', 'Love Bridge Da Nang']
    },
    {
        'id': 'dn-cong-vien-apec',
        'name': 'Công Viên APEC & Mái Vòm Cánh Diều Bay Cao',
        'wiki_terms': [],
        'commons_terms': ['APEC Park Da Nang', 'Công viên APEC Đà Nẵng']
    },
    {
        'id': 'dn-cho-han',
        'name': 'Chợ Hàn Đà Nẵng',
        'wiki_terms': ['Chợ Hàn'],
        'commons_terms': ['Han Market Da Nang', 'Chợ Hàn Đà Nẵng']
    },
    {
        'id': 'dn-cho-con',
        'name': 'Chợ Cồn (Thiên Đường Ẩm Thực Đà Nẵng)',
        'wiki_terms': ['Chợ Cồn'],
        'commons_terms': ['Con Market Da Nang', 'Chợ Cồn Đà Nẵng']
    },
    {
        'id': 'dn-cho-dem-helio',
        'name': 'Chợ Đêm Helio & Tổ Hợp Giải Trí Helio Center',
        'wiki_terms': [],
        'commons_terms': ['Helio Night Market Da Nang', 'Helio Center Da Nang']
    },
    {
        'id': 'dn-kdl-nui-than-tai',
        'name': 'Công Viên Suối Khoáng Nóng Núi Thần Tài',
        'wiki_terms': [],
        'commons_terms': ['Nui Than Tai Da Nang', 'Núi Thần Tài']
    },
    {
        'id': 'dn-kdl-hoa-phu-thanh',
        'name': 'Khu Du Lịch Sinh Thái Trượt Thác Hòa Phú Thành',
        'wiki_terms': [],
        'commons_terms': ['Hoa Phu Thanh Da Nang', 'Hòa Phú Thành']
    },
    {
        'id': 'dn-dinh-lang-tuy-loan',
        'name': 'Đình Làng Cổ Túy Loan & Làng Bánh Tráng Túy Loan',
        'wiki_terms': ['Đình Túy Loan'],
        'commons_terms': ['Dinh Tuy Loan Da Nang', 'Đình làng Túy Loan']
    }
]

print(f"Resolving verified photos for {len(danang_search_specs)} Da Nang places...")
resolved = []

for spec in danang_search_specs:
    best_match = None
    # 1. Try Wikipedia pages
    for w_term in spec['wiki_terms']:
        res = query_wikipedia(w_term, 'vi')
        if not res:
            res = query_wikipedia(w_term, 'en')
        if res and res.get('thumbUrl'):
            status, ctype = test_url_status(res['thumbUrl'])
            if status == 200:
                best_match = {
                    'url': res['thumbUrl'],
                    'source': res['source'],
                    'license': res['license'],
                    'verified': True
                }
                break
    
    # 2. Try Commons search
    if not best_match:
        for c_term in spec['commons_terms']:
            candidates = query_commons(c_term)
            for cand in candidates:
                url_to_test = cand['thumbUrl']
                status, ctype = test_url_status(url_to_test)
                if status == 200:
                    best_match = {
                        'url': url_to_test,
                        'source': f"Wikimedia Commons: {cand['title']}",
                        'license': cand['license'],
                        'artist': cand['artist'],
                        'verified': True
                    }
                    break
            if best_match:
                break
                
    resolved.append({
        'id': spec['id'],
        'name': spec['name'],
        'match': best_match
    })
    status_str = f"FOUND: {best_match['url'][:55]}..." if best_match else "NOT FOUND ON WIKI"
    print(f"- {spec['id']} ({spec['name']}) -> {status_str}")
    time.sleep(0.1)

with open('scripts/danang_resolved.json', 'w', encoding='utf-8') as f:
    json.dump(resolved, f, ensure_ascii=False, indent=2)

print("\nSaved Da Nang resolution to scripts/danang_resolved.json")
