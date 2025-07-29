try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
import torch
import os
import json
from tqdm import tqdm
import numpy as np
from pathlib import Path
import requests
import warnings
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure environment to disable SSL verification
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['REQUESTS_CA_BUNDLE'] = ""
os.environ['TRANSFORMERS_OFFLINE'] = "1"  # First download will be with SSL disabled, then use offline mode

class EmbeddingProcessor:
    def __init__(self, model_name="hkunlp/instructor-xl"):
        # Initialize the embedding model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={
                'device': device
            },
            encode_kwargs={'normalize_embeddings': True},
        )
    
    def create_embedding(self, text):
        return self.embeddings.embed_query(text)

def process_text_files(input_folder, output_file, batch_size=32):
    processor = EmbeddingProcessor()
    embeddings_data = []
    current_batch = []
    
    # Get total number of files for progress bar
    total_files = sum(1 for _, _, files in os.walk(input_folder) 
                     for file in files if file.endswith('.txt'))
    
    with tqdm(total=total_files, desc="Processing files") as pbar:
        # Walk through all directories in the input folder
        for root, _, files in os.walk(input_folder):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # Read the entire content
                            lines = f.readlines()
                            
                            # Extract source URL if it exists
                            source_url = None
                            content_start = 0
                            if lines and lines[0].startswith("Source URL:"):
                                source_url = lines[0].replace("Source URL:", "").strip()
                                content_start = 2  # Skip the URL line and the blank line
                            
                            # Join the remaining lines for the content
                            content = "".join(lines[content_start:]).strip()
                            
                            if content:
                                # Create embedding
                                embedding = processor.create_embedding(content)
                                
                                # Store the data
                                embeddings_data.append({
                                    'file_path': os.path.relpath(file_path, input_folder),
                                    'source_url': source_url,
                                    'embedding': embedding,
                                    'content': content
                                })
                                
                                pbar.update(1)
                    
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
                        pbar.update(1)
    
    # Save embeddings to file
    save_embeddings(embeddings_data, output_file)
    print(f"\nProcessing complete! Saved {len(embeddings_data)} embeddings to {output_file}")

def save_embeddings(embeddings_data, output_file):
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # The embeddings are already lists, so we can save directly
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(embeddings_data, f)

def load_embeddings(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert lists to numpy arrays for similarity calculations
    for item in data:
        item['embedding'] = np.array(item['embedding'])
    return data

def search_embeddings(query, embeddings_data, top_k=5):
    # Initialize the embedding processor
    processor = EmbeddingProcessor()
    
    # Create query embedding
    query_embedding = np.array(processor.create_embedding(query))  # Convert to numpy array
    
    # Convert embeddings to numpy array for faster computation
    embeddings = np.array([data['embedding'] for data in embeddings_data])
    
    # Calculate cosine similarity
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    # Get top k results
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'similarity': float(similarities[idx]),
            'content': embeddings_data[idx]['content'],
            'source_url': embeddings_data[idx]['source_url'],
            'file_path': embeddings_data[idx]['file_path']
        })
    
    return results

if __name__ == "__main__":
    input_folder = "extracted_content"  # Your folder with extracted text files
    output_file = "embeddings/embeddings.json"  # Where to save the embeddings
    
    # Create embeddings
    process_text_files(input_folder, output_file)
    
    # Example search
    embeddings_data = load_embeddings(output_file)
    query = "how do i check for pay plans?"
    results = search_embeddings(query, embeddings_data)
    
    # Print results
    print(f"\nSearch results for: {query}")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result['similarity']:.4f}")
        print(f"Source: {result['source_url']}")
        print(f"Content preview: {result['content'][:200]}...")