import os
import json
import re
import datetime
import time
import config

class Logger:
    def __init__(self, total_links_detected):
        self.start_time = time.time()
        self.session_id = datetime.datetime.now().isoformat()
        self.total_links_detected = total_links_detected
        self.link_details = []
        
        max_num = 0
        if os.path.exists(config.LOGS_DIR):
            for f in os.listdir(config.LOGS_DIR):
                m = re.match(r"Log (\d+)(?: \d{4}_\d{2}_\d{2})?\.json", f)
                if m:
                    num = int(m.group(1))
                    if num > max_num:
                        max_num = num
        self.log_num = max_num + 1
        current_date = datetime.datetime.now().strftime("%Y_%m_%d")
        self.log_name = f"Log {self.log_num} {current_date}.json"
        self.log_path = os.path.join(config.LOGS_DIR, self.log_name)

    def record(self, result_dict):
        url = result_dict.get('url')
        for existing in self.link_details:
            if existing.get('url') == url:
                existing.update(result_dict)
                existing['attempt_count'] = existing.get('attempt_count', 1) + 1
                return
        result_dict['attempt_count'] = 1
        self.link_details.append(result_dict)

    def write(self):
        success_count = sum(1 for d in self.link_details if d['status'] == 'SUCCESS')
        exists_count = sum(1 for d in self.link_details if d['status'] == 'EXISTS')
        empty_count = sum(1 for d in self.link_details if d['status'] == 'EMPTY')
        deadlink_count = sum(1 for d in self.link_details if d['status'] == 'DEADLINK')
        forced_count = sum(1 for d in self.link_details if d['status'] == 'FORCED')
        
        known_statuses = {'SUCCESS', 'EXISTS', 'EMPTY', 'DEADLINK', 'FORCED'}
        failed_count = sum(1 for d in self.link_details if d['status'] not in known_statuses)
        
        total_execution_time = round(time.time() - self.start_time, 2)
        
        data = {
            "session_id": self.session_id,
            "total_links_detected": self.total_links_detected,
            "successful_links": success_count,
            "failed_links": failed_count,
            "exists_links": exists_count,
            "empty_links": empty_count,
            "deadlink_links": deadlink_count,
            "forced_links": forced_count,
            "total_execution_time": total_execution_time,
            "link_details": self.link_details
        }
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)