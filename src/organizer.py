import os
import shutil
import json
import config

def extract_account_name(data):
    for key in ['native_creator', 'pinner', 'origin_pinner', 'owner']:
        if key in data and data[key] and 'username' in data[key]:
            return data[key]['username']
    if 'board' in data and data['board'] and 'owner' in data['board'] and 'username' in data['board']['owner']:
        return data['board']['owner']['username']
    return "unknown_user"

def organize_metadata():
    extracted_metadata = []
    for filename in os.listdir(config.OUTPUT_BASE):
        if filename.endswith(".json"):
            json_path = os.path.join(config.OUTPUT_BASE, filename)
            if not os.path.isfile(json_path):
                continue
                
            media_filename = filename[:-5]
            media_path = os.path.join(config.OUTPUT_BASE, media_filename)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue
                    
            account_name = extract_account_name(data)
            ext = media_filename.split('.')[-1].lower() if '.' in media_filename else 'unknown'
            
            pinner = data.get("pinner") or {}
            native_creator = data.get("native_creator") or {}
            board = data.get("board") or {}

            extracted_metadata.append({
                "pin_id": data.get("id"),
                "username": pinner.get("full_name") or native_creator.get("full_name"),
                "account_name": account_name,
                "board_name": board.get("name"),
                "board_url": board.get("url"),
                "title": data.get("seo_title") or data.get("grid_title") or data.get("title"),
                "description": data.get("description") or data.get("closeup_description"),
                "file_type": ext,
                "repin_count": data.get("repin_count"),
                "created_at": data.get("created_at")
            })

            type_prefix = 'v' if ext in ['mp4', 'webm', 'mov', 'm4v', 'avi'] else 'p'
            
            seq_num = 1
            new_base_name = f"{account_name} {type_prefix}{seq_num}"
            new_media_filename = f"{new_base_name}.{ext}"
            new_media_path = os.path.join(config.OUTPUT_BASE, new_media_filename)
            
            while os.path.exists(new_media_path):
                seq_num += 1
                new_base_name = f"{account_name} {type_prefix}{seq_num}"
                new_media_filename = f"{new_base_name}.{ext}"
                new_media_path = os.path.join(config.OUTPUT_BASE, new_media_filename)
                
            new_json_filename = f"{new_base_name}.{ext}.json"
            
            if os.path.exists(media_path):
                os.rename(media_path, new_media_path)
                
            dst_json_path = os.path.join(config.METADATA_DIR, new_json_filename)
            shutil.move(json_path, dst_json_path)
            
    return extracted_metadata