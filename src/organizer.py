import os
import shutil
import json
import config

def organize_metadata():
    extracted_metadata = []
    processed_pin_ids = set()
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
                    
            native_creator = data.get("native_creator") or {}
            closeup_attr = data.get("closeup_attribution") or {}
            closeup_unified = data.get("closeup_unified_attribution") or {}
            third_party = data.get("third_party_pin_owner") or {}
            origin_pinner = data.get("origin_pinner") or {}
            pinner = data.get("pinner") or {}
            board = data.get("board") or {}
            owner = board.get("owner") or {}

            account_name = "unknown_user"
            full_name = None
            
            for entity in [native_creator, closeup_attr, closeup_unified, third_party, origin_pinner, pinner, owner]:
                if entity and entity.get("username"):
                    account_name = entity.get("username")
                    full_name = entity.get("full_name") or account_name
                    break

            ext = media_filename.split('.')[-1].lower() if '.' in media_filename else 'unknown'
            
            pin_id = data.get("id")
            new_entry = {
                "pin_id": pin_id,
                "username": full_name,
                "account_name": account_name,
                "board_name": board.get("name"),
                "board_url": board.get("url"),
                "title": data.get("grid_title") or data.get("title") or data.get("seo_title"),
                "description": data.get("description") or data.get("closeup_description"),
                "file_type": ext,
                "repin_count": data.get("repin_count"),
                "created_at": data.get("created_at")
            }
            if new_entry not in extracted_metadata:
                extracted_metadata.append(new_entry)

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
                
            if os.path.exists(media_path):
                os.rename(media_path, new_media_path)
                
            if pin_id and pin_id not in processed_pin_ids:
                processed_pin_ids.add(pin_id)
                new_json_filename = f"{account_name}_{pin_id}.json"
                dst_json_path = os.path.join(config.METADATA_DIR, new_json_filename)
                shutil.move(json_path, dst_json_path)
            else:
                try:
                    os.remove(json_path)
                except OSError:
                    pass
            
    return extracted_metadata