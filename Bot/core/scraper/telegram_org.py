import re, httpx
from urllib.parse import quote
from Bot import LOGGER

URL = "https://my.telegram.org"

def _h(t: str = None) -> dict:
    h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": URL,
        "Referer": f"{URL}/auth",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "DNT": "1",
    }
    if t: h["Cookie"] = f"stel_token={t}"
    return h

def _ph(t: str) -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": f"stel_token={t}",
        "Referer": f"{URL}/",
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }

async def send_code(p: str) -> dict:
    try:
        ep = quote(p, safe="")
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{URL}/auth/send_password", data=f"phone={ep}", headers=_h())
            if r.status_code == 200:
                try: return r.json()
                except: return {"error": r.text.strip()}
            return {}
    except Exception as e:
        LOGGER.error(f"sc err: {e}")
        return {}

async def login_and_fetch(p: str, rh: str, cd: str) -> dict | None:
    try:
        ep = quote(p, safe="")
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{URL}/auth/login", data=f"phone={ep}&random_hash={rh}&password={cd}", headers=_h())
            t = r.cookies.get("stel_token")
            if not t: return None
            ar = await c.get(f"{URL}/apps", headers=_ph(t))
            cr = _pc(ar.text)
            if cr: return cr
            hm = re.search(r'<input\s+type="hidden"\s+name="hash"\s+value="([^"]+)"', ar.text)
            if not hm: return None
            fh = hm.group(1)
            await c.post(f"{URL}/apps/create", data=f"hash={fh}&app_title=MyApp&app_shortname=myapp&app_url=&app_platform=android&app_desc=", headers={**_h(t), "Referer": f"{URL}/apps", "Accept": "*/*"})
            ar = await c.get(f"{URL}/apps", headers=_ph(t))
            return _pc(ar.text)
    except Exception as e:
        LOGGER.error(f"lf err: {e}")
        return None

def _pc(h: str) -> dict | None:
    im = re.search(r'api_id.*?<span[^>]*class="[^"]*uneditable-input[^"]*"[^>]*>(.*?)</span>', h, re.DOTALL | re.IGNORECASE)
    hm = re.search(r'api_hash.*?<span[^>]*class="[^"]*uneditable-input[^"]*"[^>]*>(.*?)</span>', h, re.DOTALL | re.IGNORECASE)
    if im and hm:
        id = re.sub(r'<[^>]+>', '', im.group(1)).strip()
        hs = re.sub(r'<[^>]+>', '', hm.group(1)).strip()
        if id.isdigit() and len(hs) == 32: return {"api_id": id, "api_hash": hs}
    v = [re.sub(r'<[^>]+>', '', v).strip() for v in re.findall(r'<span[^>]*class="[^"]*uneditable-input[^"]*"[^>]*>(.*?)</span>', h, re.DOTALL)]
    if len(v) >= 2 and v[0].isdigit() and len(v[1]) == 32: return {"api_id": v[0], "api_hash": v[1]}
    i2 = re.search(r'api_id.*?>(\d{5,12})<', h, re.DOTALL)
    h2 = re.search(r'api_hash.*?([a-f0-9]{32})', h, re.DOTALL | re.IGNORECASE)
    if i2 and h2: return {"api_id": i2.group(1), "api_hash": h2.group(1)}
    return None
