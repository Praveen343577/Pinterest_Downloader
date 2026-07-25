import re
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
        # Remove duplicates while preserving order
        urls = list(dict.fromkeys(urls))
        return urls if urls else [url]
    except Exception:
        return [url]

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
                for expanded_url in expanded_map.get(url, []):
                    valid_urls.append({'url': expanded_url, 'force': force})
                
    # Remove duplicates globally while preserving order and force flags
    unique_valid_urls = []
    seen = set()
    for item in valid_urls:
        if item['url'] not in seen:
            unique_valid_urls.append(item)
            seen.add(item['url'])
        elif item['force']:
            for u in unique_valid_urls:
                if u['url'] == item['url']:
                    u['force'] = True
                    break
    valid_urls = unique_valid_urls
            
    return valid_urls, invalid_urls

def get_cookie_path():
    return config.COOKIE_FILE