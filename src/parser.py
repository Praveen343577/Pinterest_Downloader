import re
import config
import subprocess
from rich.console import Console
from rich.progress import Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn
import rich._spinners

rich._spinners.SPINNERS["my_dots"] = {
    "interval": 400,
    "frames": ["   ", ".  ", ".. ", "..."]
}

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
            if pattern.match(line):
                raw_valid.append(line)
            else:
                invalid_urls.append((i, line))
                
    if raw_valid:
        needs_expansion = [u for u in raw_valid if not pin_pattern.search(u)]
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
                    
        for url in raw_valid:
            if pin_pattern.search(url):
                valid_urls.append(url)
            else:
                valid_urls.extend(expanded_map[url])
                
    # Remove duplicates globally while preserving order
    valid_urls = list(dict.fromkeys(valid_urls))
            
    return valid_urls, invalid_urls

def get_cookie_path():
    return config.COOKIE_FILE