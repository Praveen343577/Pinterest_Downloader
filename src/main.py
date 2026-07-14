import sys
import time
import random
from preflight import run_checks
from parser import parse_links
from downloader import download_url
from organizer import organize_metadata
from logger import Logger
from dashboard import print_header, print_preflight_success, print_summary, DashboardManager, console
import config

def main():
    if not run_checks():
        sys.exit(1)
        
    valid_urls, invalid_urls = parse_links()
    total_detected = len(valid_urls) + len(invalid_urls)
    
    if not valid_urls:
        console.print("[red]No valid URLs found in Links.txt[/red]")
        sys.exit(1)
        
    session_logger = Logger(total_detected)
    
    print_header(len(valid_urls), session_logger.log_name)
    print_preflight_success("- gallery-dl verified\n- Required files present\n- Cookie.txt format & domain validated\n- Output directories mapped")
    
    for line_num, url in invalid_urls:
        session_logger.record({
            "url": url,
            "status": "INVALID_URL",
            "items_downloaded": 0,
            "error_message": "Failed domain/format validation check",
            "duration": 0.0
        })

    start_time = time.time()
    
    with DashboardManager(len(valid_urls)) as dash:
        failed_links = valid_urls.copy()
        
        for pass_num in range(1, getattr(config, 'MAX_RETRIES', 3) + 1):
            if not failed_links:
                break
                
            if pass_num > 1:
                dash.add_line_space()
                
            current_links = failed_links.copy()
            failed_links = []
            is_retry = (pass_num > 1)
            
            for i, url in enumerate(current_links):
                orig_i = valid_urls.index(url)
                dash.new_link(orig_i, url, pass_num)
                
                def cb(count):
                    dash.update_item_count(count)
                    
                result = download_url(url, callback=cb)
                result['extracted_metadata'] = organize_metadata()
                session_logger.record(result)
                
                status = result['status']
                success = status in ['SUCCESS', 'EXISTS', 'EMPTY']
                dash.complete_link(status, result['duration'], is_retry)
                dash.print_result(status, result['items_downloaded'], url)
                
                if not success and status != 'DEADLINK':
                    failed_links.append(url)
                
                if i < len(current_links) - 1:
                    if (orig_i + 1) % config.SESSION_SIZE == 0:
                        cooldown_dur = random.uniform(config.MIN_COOLDOWN, config.MAX_COOLDOWN)
                        elapsed = 0
                        while elapsed < cooldown_dur:
                            dash.set_cooldown(cooldown_dur - elapsed, cooldown_dur)
                            time.sleep(1)
                            elapsed += 1
                    else:
                        delay_dur = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
                        elapsed = 0
                        while elapsed < delay_dur:
                            dash.set_delay(delay_dur - elapsed)
                            time.sleep(0.1)
                            elapsed += 0.1

    session_logger.write()
    print_summary(time.time() - start_time, dash.success_count, dash.fail_count, dash.exists_count, dash.empty_count, dash.deadlink_count)
    # dash.flush_results()

if __name__ == "__main__":
    main()