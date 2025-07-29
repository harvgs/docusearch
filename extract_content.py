import os
from bs4 import BeautifulSoup
import json
from pathlib import Path

def extract_content_from_html(html_file):
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find the main content div
        content_div = soup.find('div', class_='doc-middle-content')
        if content_div:
            post_div = content_div.find('div', id='post')
            if post_div:
                # Extract text while preserving some structure
                text = ''
                for element in post_div.stripped_strings:
                    text += element + '\n'
                return text.strip()
        return None
    except Exception as e:
        print(f"Error processing {html_file}: {str(e)}")
        return None

def process_connections_folder(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Keep track of processed files
    processed_files = 0
    failed_files = []
    
    # Walk through all directories in the connections folder
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.html'):
                html_path = os.path.join(root, file)
                
                # Create corresponding output path
                relative_path = os.path.relpath(root, input_folder)
                output_path = os.path.join(output_folder, relative_path)
                os.makedirs(output_path, exist_ok=True)
                
                # Get corresponding JSON metadata file
                json_file = Path(html_path).with_suffix('.json')
                original_url = None
                if json_file.exists():
                    with open(json_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        original_url = metadata.get('original_url')
                
                # Extract content
                content = extract_content_from_html(html_path)
                
                if content:
                    # Save content with metadata
                    output_file = os.path.join(output_path, Path(file).stem + '.txt')
                    with open(output_file, 'w', encoding='utf-8') as f:
                        if original_url:
                            f.write(f"Source URL: {original_url}\n\n")
                        f.write(content)
                    processed_files += 1
                else:
                    failed_files.append(html_path)
    
    # Print summary
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_files} files")
    if failed_files:
        print(f"Failed to process {len(failed_files)} files:")
        for file in failed_files:
            print(f"- {file}")

if __name__ == "__main__":
    input_folder = "connections"  # Your input folder with HTML files
    output_folder = "extracted_content"  # Where to save the extracted content
    
    process_connections_folder(input_folder, output_folder)