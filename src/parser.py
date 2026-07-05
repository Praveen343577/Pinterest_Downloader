import re
import config
import subprocess
from rich.console import Console

console = Console()

def expand_url(url):
    cmd = [
        config.GALLERY_DL_PATH,
        "--cookies", config.COOKIE_FILE,
        "-N", "https://in.pinterest.com/pin/{id}/",
        url
    ]
    creationflags = 0x08000000 
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            creationflags=creationflags
        )
        stdout, _ = process.communicate(timeout=120)
        urls = [line.strip() for line in stdout.split('\n') if line.strip().startswith("http")]
        return urls if urls else [url]
    except Exception:
        return [url]

def parse_links():
    valid_urls = []
    invalid_urls = []
    
    pattern = re.compile(r'^https?://(?:.*pinterest\.(com|co\.uk|ca|fr|de|es|it|at|be|ch|se|dk|pt|nz|ph|ru|jp|kr|com\.au|com\.mx|com\.br)|pin\.it).*')
    
    raw_valid = []
    with open(config.LINKS_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if pattern.match(line):
                raw_valid.append(line)
            else:
                invalid_urls.append((i, line))
                
    if raw_valid:
        console.print("[yellow]Extracting individual pin URLs from boards/profiles...[/yellow]")
        for url in raw_valid:
            valid_urls.extend(expand_url(url))
            
    return valid_urls, invalid_urls

def get_cookie_path():
    return config.COOKIE_FILE