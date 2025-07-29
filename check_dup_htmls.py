import os
import hashlib
from collections import defaultdict
from tqdm import tqdm

def hash_file(filepath):
    """Generate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Read file in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicate_htmls(root_dir='data'):
    """Find duplicate HTML files by comparing their hashes."""
    hash_dict = defaultdict(list)
    
    # First count total HTML files for the progress bar
    total_files = sum(1 for dirpath, _, filenames in os.walk(root_dir)
                     for filename in filenames if filename.lower().endswith('.html'))
    
    # Walk through all directories and files with progress bar
    with tqdm(total=total_files, desc="Hashing files") as pbar:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.lower().endswith('.html'):
                    filepath = os.path.join(dirpath, filename)
                    file_hash = hash_file(filepath)
                    hash_dict[file_hash].append(filepath)
                    pbar.update(1)
    
    # Filter out unique files (hashes with only one file)
    duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
    return duplicates

def main():
    duplicates = find_duplicate_htmls()
    
    if not duplicates:
        print("No duplicate HTML files found.")
        return
    
    print("Found duplicate HTML files:")
    for hash_value, file_list in duplicates.items():
        print(f"\nFiles with hash {hash_value}:")
        for filepath in file_list:
            print(f"  - {filepath}")

if __name__ == '__main__':
    main()
