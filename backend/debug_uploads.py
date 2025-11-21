
import os
import json
import sys

CHUNKS_FOLDER = r'f:\GameManager\backend\uploads\chunks'
GAMES_FOLDER = r'f:\GameManager\backend\uploads\games'

def inspect_uploads():
    print(f"Inspecting {CHUNKS_FOLDER}...")
    if not os.path.exists(CHUNKS_FOLDER):
        print("Chunks folder not found.")
        return

    upload_dirs = os.listdir(CHUNKS_FOLDER)
    print(f"Found {len(upload_dirs)} upload sessions.")

    for upload_id in upload_dirs:
        upload_dir = os.path.join(CHUNKS_FOLDER, upload_id)
        if not os.path.isdir(upload_dir):
            continue

        metadata_path = os.path.join(upload_dir, 'metadata.json')
        if not os.path.exists(metadata_path):
            print(f"[{upload_id}] No metadata.json")
            continue

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            total = metadata.get('totalChunks', 0)
            uploaded = len(metadata.get('uploadedChunks', []))
            file_name = metadata.get('fileName', 'Unknown')
            
            print(f"[{upload_id}] {file_name}: {uploaded}/{total} chunks.")
            
            if uploaded == total:
                print(f"    WARNING: 100% uploaded but still in chunks folder!")
                # Check if chunks actually exist
                missing_chunks = []
                for i in range(total):
                    if not os.path.exists(os.path.join(upload_dir, f'chunk_{i}')):
                        missing_chunks.append(i)
                
                if missing_chunks:
                    print(f"    ERROR: Missing chunk files: {missing_chunks[:10]}...")
                else:
                    print(f"    READY TO MERGE.")

        except Exception as e:
            print(f"[{upload_id}] Error reading metadata: {e}")

if __name__ == "__main__":
    inspect_uploads()
