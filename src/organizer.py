import os
import shutil
import config

def organize_metadata():
    for filename in os.listdir(config.OUTPUT_BASE):
        if filename.endswith(".json"):
            src = os.path.join(config.OUTPUT_BASE, filename)
            if not os.path.isfile(src):
                continue
                
            base_name, ext = os.path.splitext(filename)
            dst_filename = filename
            counter = 1
            
            while os.path.exists(os.path.join(config.METADATA_DIR, dst_filename)):
                dst_filename = f"{base_name}_{counter}{ext}"
                counter += 1
                
            shutil.move(src, os.path.join(config.METADATA_DIR, dst_filename))