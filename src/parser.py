import re
import config

def parse_links():
    valid_urls = []
    invalid_urls = []
    
    # pattern = re.compile(r'^https?://.*pinterest\.(com|co\.uk|ca|fr|de|es|it|at|be|ch|se|dk|pt|nz|ph|ru|jp|kr|com\.au|com\.mx|com\.br).*')
    pattern = re.compile(r'^https?://(?:.*pinterest\.(com|co\.uk|ca|fr|de|es|it|at|be|ch|se|dk|pt|nz|ph|ru|jp|kr|com\.au|com\.mx|com\.br)|pin\.it).*')
    
    with open(config.LINKS_FILE, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if pattern.match(line):
                valid_urls.append(line)
            else:
                invalid_urls.append((i, line))
                
    return valid_urls, invalid_urls

def get_cookie_path():
    return config.COOKIE_FILE