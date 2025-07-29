import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urldefrag
import re
import urllib3
import hashlib
import json
from datetime import datetime
import mimetypes
import urllib.parse
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

# only takes 40 minutes to scrape

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add a thread-local storage for database connections
thread_local = threading.local()

def setup_database(output_folder):
    db_path = os.path.join(output_folder, 'scrape_data.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            url TEXT PRIMARY KEY,
            content_hash TEXT,
            last_scraped TEXT,
            last_updated TEXT,
            UNIQUE(content_hash)
        )
    ''')
    conn.commit()
    return conn

def get_db_connection(output_folder):
    if not hasattr(thread_local, "connection"):
        thread_local.connection = setup_database(output_folder)
    return thread_local.connection

def scrape_connections(base_url, output_folder, max_workers=5):
    os.makedirs(output_folder, exist_ok=True)
    visited_urls = set()
    to_visit = set()
    url_lock = threading.Lock()  # Lock for thread-safe URL set operations
    
    # Setup initial database connection
    conn = setup_database(output_folder)
    
    # Load previously scraped URLs and to_visit queue
    scrape_record_file = os.path.join(output_folder, 'scrape_record.json')
    to_visit_file = os.path.join(output_folder, 'to_visit.json')
    
    if os.path.exists(scrape_record_file):
        with open(scrape_record_file, 'r') as f:
            scrape_record = json.load(f)
        visited_urls = set(scrape_record.keys())
    else:
        scrape_record = {}

    if os.path.exists(to_visit_file):
        with open(to_visit_file, 'r') as f:
            to_visit = set(json.load(f))
    
    # If to_visit is empty, start with the base_url
    if not to_visit:
        to_visit.add(base_url)

    def is_valid_url(url):
        parsed = urlparse(url)
        base_parsed = urlparse(base_url)
        # Remove the fragment (anchor) from the URL
        url_without_fragment, _ = urldefrag(url)
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        
        # Check if there are any query parameters other than 'docs'
        has_other_params = any(key != 'docs' for key in query_params.keys())
        
        return (parsed.netloc == base_parsed.netloc and 
                url_without_fragment not in visited_urls and 
                url_without_fragment not in to_visit and
                not url_without_fragment.startswith('http://connections/?page_id=7621') and
                not url_without_fragment.startswith('http://connections?format=calendar') and
                not url_without_fragment.startswith('http://connections?time=week') and
                not has_other_params)  # Exclude URLs with any query parameters except 'docs'

    def normalize_url(url):
        # Remove the fragment (anchor) from the URL
        url_without_fragment, _ = urldefrag(url)
        # Convert to http and normalize URL encoding
        normalized = url_without_fragment.replace('https://', 'http://')
        
        # Parse the URL to normalize the query parameters
        parsed = urlparse(normalized)
        if parsed.query:
            # Parse and rebuild query parameters to ensure consistent encoding
            query_params = parse_qs(parsed.query)
            if 'docs' in query_params:
                # Normalize the docs parameter by decoding and re-encoding consistently
                docs_value = query_params['docs'][0]
                docs_decoded = urllib.parse.unquote(docs_value)
                query_params['docs'] = [docs_decoded]
            
            # Rebuild the query string with sorted parameters
            normalized_query = urllib.parse.urlencode(query_params, doseq=True)
            # Rebuild the URL with normalized query
            normalized = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                normalized_query,
                None  # fragment is already removed
            ))
        
        return normalized

    def create_safe_filename(url):
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        path = urlparse(url).path.strip('/')
        last_part = path.split('/')[-1] if path else 'index'
        safe_name = f"{url_hash}_{last_part}"
        safe_name = re.sub(r'[<>:"/\\|?*&=#]', '_', safe_name)
        return safe_name[:240]

    def extract_update_date(soup):
        update_text = soup.find(string=re.compile(r'Updated on'))
        if update_text:
            date_match = re.search(r'Updated on (\w+ \d+, \d{4})', update_text)
            if date_match:
                return datetime.strptime(date_match.group(1), '%B %d, %Y').date()
        return None

    def scrape_page(url):
        time.sleep(1)  # Add a 1-second delay between requests
        url = normalize_url(url)
        conn = get_db_connection(output_folder)
        cursor = conn.cursor()
        
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').split(';')[0]
            
            if content_type != 'text/html':
                print(f"Skipping {url}: Not an HTML file")
                return

            # Calculate content hash
            content_hash = hashlib.md5(response.content).hexdigest()
            
            # Check if content already exists
            cursor.execute('SELECT url FROM pages WHERE content_hash = ?', (content_hash,))
            existing_url = cursor.fetchone()
            
            if existing_url:
                print(f"Skipping {url}: Content already exists at {existing_url[0]}")
                return

            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            docs_param = query_params.get('docs', [''])[0]

            folder_path = os.path.join(output_folder, *docs_param.split('/')[:2])  # Limit depth
            os.makedirs(folder_path, exist_ok=True)

            safe_name = create_safe_filename(url)
            
            file_path = os.path.join(folder_path, safe_name + '.html')
            json_file_path = os.path.join(folder_path, safe_name + '.json')
            
            # Save content
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # Extract update date
            soup = BeautifulSoup(response.text, 'html.parser')
            update_date = extract_update_date(soup)

            # Check if we need to update based on the extracted date
            if url in scrape_record and update_date:
                last_updated = datetime.fromisoformat(scrape_record[url]['last_updated']) if scrape_record[url]['last_updated'] else None
                if last_updated and update_date <= last_updated.date():
                    print(f"Skipping {url}: No new updates")
                    return

            # Save metadata (including original URL) as JSON
            metadata = {
                'original_url': url,
                'content_type': content_type,
                'scraped_at': str(datetime.now()),
                'last_updated': str(update_date) if update_date else None
            }
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            # Parse HTML content for links
            soup = BeautifulSoup(response.text, 'html.parser')
            new_urls = set()
            for link in soup.find_all(['a', 'area'], href=True):
                next_url = normalize_url(urljoin(url, link['href']))
                if is_valid_url(next_url):
                    new_urls.add(next_url)

            # Thread-safe update of to_visit set
            with url_lock:
                to_visit.update(new_urls)
                print(f"Found {len(to_visit)} links to visit")

            # Save to database
            cursor.execute('''
                INSERT OR REPLACE INTO pages (url, content_hash, last_scraped, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (url, content_hash, str(datetime.now()), str(update_date) if update_date else None))
            conn.commit()

            # Thread-safe update of scrape record
            with url_lock:
                scrape_record[url] = {
                    'scraped_at': str(datetime.now()),
                    'last_updated': str(update_date) if update_date else None
                }
                # Save updated scrape record
                with open(scrape_record_file, 'w') as f:
                    json.dump(scrape_record, f, indent=2)

        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")

        # Thread-safe save of to_visit queue
        with url_lock:
            with open(to_visit_file, 'w') as f:
                json.dump(list(to_visit), f, indent=2)

    def process_urls():
        while True:
            # Thread-safe URL retrieval
            with url_lock:
                if not to_visit:
                    break
                url = to_visit.pop()
                if url in visited_urls:
                    continue
                visited_urls.add(url)

            scrape_page(url)

    # Use ThreadPoolExecutor for concurrent scraping
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Start with multiple workers
        futures = [executor.submit(process_urls) for _ in range(max_workers)]
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

    # Clear the to_visit file when scraping is complete
    if os.path.exists(to_visit_file):
        os.remove(to_visit_file)

    # Close all database connections
    for thread in threading.enumerate():
        if hasattr(thread_local, "connection"):
            thread_local.connection.close()

if __name__ == "__main__":
    base_url = "http://connections/"
    output_folder = "connections"
    scrape_connections(base_url, output_folder, max_workers=5)
