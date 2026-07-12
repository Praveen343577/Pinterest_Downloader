import subprocess
import time
import urllib.request
import config

def resolve_url(url):
    if "pin.it" in url.lower():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            resp = urllib.request.urlopen(req, timeout=15)
            resolved = resp.geturl()
            resp.close()
            return resolved
        except Exception:
            pass
    return url

def download_url(url, callback=None):
    start_time = time.time()
    
    actual_url = resolve_url(url)
    
    template = "{id}_{num}.{extension}"
    
    cmd = [
        config.GALLERY_DL_PATH,
        "--cookies", config.COOKIE_FILE,
        "--download-archive", config.ARCHIVE_FILE,
        "--directory", config.OUTPUT_BASE,
        "-o", "directory=[\".\"]",
        "--filename", template,
        "--write-metadata",
        "--sleep-request", "1-3",
        actual_url
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
    except FileNotFoundError:
        return {
            "url": url, 
            "status": "FAILED", 
            "items_downloaded": 0, 
            "error_message": f"Binary not found: {config.GALLERY_DL_PATH}", 
            "duration": time.time() - start_time
        }

    items = 0
    while True:
        line = process.stdout.readline()
        if not line:
            break
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):
            items += 1
            if callback:
                callback(items)
                
    try:
        process.wait(timeout=config.TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        return {
            "url": url, 
            "status": "TIMEOUT", 
            "items_downloaded": items, 
            "error_message": f"Timeout after {config.TIMEOUT_SEC}s", 
            "duration": time.time() - start_time
        }
        
    stderr = process.stderr.read()
    rc = process.returncode
    
    if rc == 0:
        if items == 0:
            status = "EXISTS"
        else:
            status = "SUCCESS"
        error_message = None
    else:
        stderr_lower = stderr.lower()
        if "403" in stderr_lower or "forbidden" in stderr_lower:
            status = "HTTP_403"
        elif "404" in stderr_lower or "not found" in stderr_lower:
            status = "HTTP_404"
        else:
            status = "FAILED"
        error_message = stderr.strip() if stderr.strip() else f"Process exited with code {rc}"
        
    return {
        "url": url,
        "status": status,
        "items_downloaded": items,
        "error_message": error_message,
        "duration": time.time() - start_time
    }