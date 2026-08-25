from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

QUERY = 'Tesla when:2d'
RSS_URL = (
    'https://news.google.com/rss/search?q='
    + urllib.parse.quote(QUERY)
    + '&hl=en-US&gl=US&ceid=US:en'
)

POSITIVE = {
    'surge','surges','rise','rises','gain','gains','beat','beats','record',
    'growth','grow','launch','launches','approval','approved','expands',
    'strong','profit','profits','upgrade','upgraded','wins','win'
}
NEGATIVE = {
    'fall','falls','drop','drops','decline','declines','recall','probe',
    'investigation','lawsuit','crash','cuts','cut','delay','delays',
    'weak','loss','losses','downgrade','downgraded','ban','warning',
    'risk','risks','slump','slumps'
}

def clean_title(title: str) -> str:
    return re.sub(r'\s+-\s+[^-]+$', '', title).strip()

def sentiment(title: str) -> str:
    words = set(re.findall(r"[a-zA-Z']+", title.lower()))
    p = len(words & POSITIVE)
    n = len(words & NEGATIVE)
    if p > n:
        return 'positive'
    if n > p:
        return 'negative'
    return 'neutral'

def fetch():
    req = urllib.request.Request(
        RSS_URL,
        headers={'User-Agent':'Mozilla/5.0 TSLA-Daily/1.0'}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    rows = []
    seen = set()
    for item in root.findall('./channel/item'):
        raw_title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        source_el = item.find('source')
        source = (source_el.text or 'Unknown').strip() if source_el is not None else 'Unknown'
        pub = (item.findtext('pubDate') or '').strip()
        title = clean_title(raw_title)
        key = re.sub(r'[^a-z0-9]+',' ',title.lower()).strip()
        if not title or not link or key in seen:
            continue
        seen.add(key)
        try:
            dt = parsedate_to_datetime(pub).astimezone(timezone.utc)
            iso = dt.isoformat()
            display = dt.astimezone().strftime('%m.%d %H:%M')
        except Exception:
            iso, display = '', pub
        rows.append({
            'title': title,
            'source': source,
            'link': link,
            'published': iso,
            'published_display': display,
            'sentiment': sentiment(title),
            'summary': f'{source}에서 수집한 Tesla 관련 최신 기사입니다.'
        })
        if len(rows) >= 30:
            break
    return rows

def main():
    items = fetch()
    now = datetime.now().astimezone()
    data = {
        'updated_at': now.isoformat(),
        'updated_display': now.strftime('%Y.%m.%d %H:%M'),
        'query': QUERY,
        'items': items
    }
    Path('news.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f'Updated news.json with {len(items)} items')

if __name__ == '__main__':
    main()
