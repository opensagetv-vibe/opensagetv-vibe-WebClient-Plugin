"""Read-only candidate guard shared by physical field runners; no server access."""
import json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,parse_qs

class _Scripts(HTMLParser):
    def __init__(self):super().__init__();self.sources=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':self.sources.append(dict(attrs).get('src',''))

def playback_revision(root):
    root=Path(root)
    metadata=json.loads((root/'BUILD_INFO.json').read_text(encoding='utf-8'))
    version=metadata.get('version','');asset=metadata.get('asset_versions',{}).get('playback','')
    if not re.fullmatch(r'\d+\.\d+\.\d+',version) or not re.fullmatch(r'web\d+\.\d+',asset):
        raise ValueError('Missing or invalid current playback metadata')
    parser=_Scripts();parser.feed((root/'src/main/webapp/miniclient.html').read_text(encoding='utf-8'))
    scripts=[urlparse(source) for source in parser.sources if urlparse(source).path=='js/miniclient-playback.js']
    expected=version+'-'+asset
    if len(scripts)!=1 or parse_qs(scripts[0].query).get('v')!=[expected]:
        raise ValueError('Playback metadata/source mismatch; do not run a stale candidate gate')
    return 'v='+expected
