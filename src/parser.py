import re
import urllib.request
import config
import subprocess
from rich.console import Console
from rich.progress import Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn
# from rich.text import Text
import rich._spinners

rich._spinners.SPINNERS["my_dots"] = {
    "interval": 400,
    "frames": ["   ", ".  ", ".. ", "..."]
}

console = Console()

# class CustomTimeElapsedColumn(TimeElapsedColumn):
#     def render(self, task):
#         elapsed = task.finished_time if task.finished else task.elapsed
#         if elapsed is None:
#             return Text("--:--:--", style="progress.elapsed")
#         elapsed = int(elapsed)
#         m, s = divmod(elapsed, 60)
#         h, m = divmod(m, 60)
#         return Text(f"{h:02d}:{m:02d}:{s:02d}", style="progress.elapsed")

# class CustomTimeRemainingColumn(TimeRemainingColumn):
#     def render(self, task):
#         if task.time_remaining is None:
#             return Text("--:--:--", style="progress.remaining")
#         time_remaining = int(task.time_remaining)
#         m, s = divmod(time_remaining, 60)
#         h, m = divmod(m, 60)
#         return Text(f"{h:02d}:{m:02d}:{s:02d}", style="progress.remaining")

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
        # Intentionally keeping duplicates so they show as EXISTS
        return urls if urls else [url]
    except Exception:
        return [url]

def fetch_board_pin_count(url):
    cmd = [
        config.GALLERY_DL_PATH,
        "--cookies", config.COOKIE_FILE,
        "--dump-json",
        "--range", "1-1",
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
        stdout, _ = process.communicate(timeout=60)
        
        try:
            import json
            data = json.loads(stdout)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list) and len(data[0]) > 0:
                first_item = data[0][0]
                if 'board' in first_item and 'pin_count' in first_item['board']:
                    return int(first_item['board']['pin_count'])
        except Exception:
            pass
            
        m = re.search(r'"pin_count"\s*:\s*(\d+)', stdout)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None

def parse_links():
    valid_urls = []
    invalid_urls = []
    
    pattern = re.compile(r'^https?://(?:.*pinterest\.(com|co\.uk|ca|fr|de|es|it|at|be|ch|se|dk|pt|nz|ph|ru|jp|kr|com\.au|com\.mx|com\.br)|pin\.it).*')
    pin_pattern = re.compile(r'/pin/\d+')
    
    raw_valid = []
    with open(config.LINKS_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            force = False
            if line.startswith('!') or line.upper().startswith('[FORCE]'):
                force = True
                line = re.sub(r'^(!|\[FORCE\])\s*', '', line, flags=re.IGNORECASE).strip()

            if pattern.match(line):
                raw_valid.append({'url': line, 'force': force})
            else:
                invalid_urls.append((i, line))
                
    if raw_valid:
        needs_expansion = [item['url'] for item in raw_valid if not pin_pattern.search(item['url'])]
        expanded_map = {}
        
        if needs_expansion:
            with Progress(
                TextColumn("[yellow]Extracting individual pin URLs from boards/profiles[/yellow]"),
                SpinnerColumn("my_dots", style="yellow"),
                TextColumn(" | [cyan]Elapsed:[/cyan]"),
                TimeElapsedColumn(),
                TextColumn(" | [cyan]ETA:[/cyan]"),
                TimeRemainingColumn(),
                console=console
            ) as progress:
                task = progress.add_task("", total=len(needs_expansion))
                for url in needs_expansion:
                    expanded_map[url] = expand_url(url)
                    progress.update(task, advance=1)
                    
        for item in raw_valid:
            url = item['url']
            force = item['force']
            if pin_pattern.search(url):
                valid_urls.append({'url': url, 'force': force})
            else:
                expanded = expanded_map.get(url, [])
                for expanded_url in expanded:
                    valid_urls.append({'url': expanded_url, 'force': force})
                
                if expanded and not (len(expanded) == 1 and expanded[0] == url):
                    official_count = fetch_board_pin_count(url)
                    if official_count and official_count > len(expanded):
                        diff = official_count - len(expanded)
                        for _ in range(diff):
                            valid_urls.append({'url': 'Ghost/Deleted Pin', 'force': False, 'is_ghost': True})
                
    # Deliberately removed global deduplication to allow duplicates to be processed
    # as EXISTS natively by gallery-dl, bringing counts closer to Pinterest's UI.
            
    return valid_urls, invalid_urls

def get_cookie_path():
    return config.COOKIE_FILE