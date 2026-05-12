import os
import config
from dashboard import console
from rich.panel import Panel

def run_checks():
    if not os.path.exists(config.GALLERY_DL_PATH):
        console.print(Panel(f"gallery-dl.exe missing.\nExpected at: {config.USER_GALLERY_DL}\nPlease download from gallery-dl releases.", style="red"))
        return False
        
    if not os.path.exists(config.LINKS_FILE):
        console.print(Panel(f"Links.txt missing.\nPlease place it at: {config.LINKS_FILE}", style="red"))
        return False
        
    if not os.path.exists(config.COOKIE_FILE):
        console.print(Panel("Cookie.txt missing.", style="red"))
        return False
        
    with open(config.COOKIE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not lines:
            console.print(Panel("Cookie.txt is empty.", style="red"))
            return False
            
        first_line = lines[0].rstrip('\n').rstrip('\r')
        if first_line != config.EXPECTED_COOKIE_HEADER:
            console.print(Panel(f"Cookie.txt header mismatch.\nExpected: '{config.EXPECTED_COOKIE_HEADER}'\nFound: '{first_line}'", style="red"))
            return False
            
        has_pinterest = False
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split('\t')
            if len(parts) > 0 and ('pinterest.com' in parts[0] or '.pinterest.com' in parts[0]):
                has_pinterest = True
                break
                
        if not has_pinterest:
            console.print(Panel("No Pinterest cookie found.\nPlease log in to Pinterest and re-export cookies.", style="red"))
            return False
            
    os.makedirs(config.OUTPUT_BASE, exist_ok=True)
    os.makedirs(config.METADATA_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    return True