import os
import config
from dashboard import console

def run_checks():
    if not os.path.exists(config.GALLERY_DL_PATH):
        console.print(f"\ngallery-dl.exe missing.\n\nExpected at: {config.USER_GALLERY_DL}\nPlease download from gallery-dl releases.\n", style="red")
        return False
        
    if not os.path.exists(config.LINKS_FILE):
        console.print(f"\nLinks.txt missing.\n\nPlease place it at: {config.LINKS_FILE}\n", style="red")
        return False
        
    if not os.path.exists(config.COOKIE_FILE):
        console.print("\nCookie.txt missing.\n", style="red")
        return False
        
    with open(config.COOKIE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not lines:
            console.print("\nCookie.txt is empty.\n\nHow to get your cookies:\n  1. Install a browser extension like 'Get cookies.txt LOCALLY'.\n  2. Go to pinterest.com and log in.\n  3. Export the cookies and paste them into Cookie.txt.\n", style="red")
            return False
            
        first_line = lines[0].rstrip('\n').rstrip('\r')
        if first_line != config.EXPECTED_COOKIE_HEADER:
            console.print(f"\nCookie.txt header mismatch.\n\nExpected: '{config.EXPECTED_COOKIE_HEADER}'\nFound: '{first_line}'\n", style="red")
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
            console.print("\nNo Pinterest cookie found.\n\nPlease log in to Pinterest and re-export cookies.\n", style="red")
            return False
            
    os.makedirs(config.OUTPUT_BASE, exist_ok=True)
    os.makedirs(config.METADATA_DIR, exist_ok=True)
    os.makedirs(config.LOGS_DIR, exist_ok=True)
    
    return True