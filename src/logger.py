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
                m = re.match(r"Log (\d+)\.json", f)
                if m:
                    num = int(m.group(1))
                    if num > max_num:
                        max_num = num
        self.log_num = max_num + 1
        self.log_name = f"Log {self.log_num}.json"
        self.log_path = os.path.join(config.LOGS_DIR, self.log_name)

    def record(self, result_dict):
        self.link_details.append(result_dict)

    def write(self):
        success_count = sum(1 for d in self.link_details if d['status'] == 'SUCCESS')
        failed_count = len(self.link_details) - success_count
        total_execution_time = round(time.time() - self.start_time, 2)
        
        data = {
            "session_id": self.session_id,
            "total_links_detected": self.total_links_detected,
            "successful_links": success_count,
            "failed_links": failed_count,
            "total_execution_time": total_execution_time,
            "link_details": self.link_details
        }
        
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)