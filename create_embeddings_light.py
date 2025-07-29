import torch
import os
import json
from tqdm import tqdm
import numpy as np
from pathlib import Path
import requests
import warnings
import urllib3
from sentence_transformers import SentenceTransformer

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure environment to disable SSL verification
os.environ['CURL_CA_BUNDLE'] = ""
os.environ['REQUESTS_CA_BUNDLE'] = ""

class LightEmbeddingProcessor:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        # Force CPU usage for Railway deployment
        device = "cpu"
        
        # Use the smallest available model for minimal size
        self.model = SentenceTransformer(model_name, device=device)
        
        # Optimize for CPU inference
        self.model.eval()
        if hasattr(self.model, 'half'):
            # Use half precision if available to reduce memory
            self.model = self.model.half()
    
    def create_embedding(self, text):
        # Ensure we're using CPU
        with torch.no_grad():
            return self.model.encode(text, convert_to_tensor=False).tolist()

def process_text_files(input_folder, output_file, batch_size=32):
    processor = LightEmbeddingProcessor()
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
    """Load embeddings from file"""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Embeddings file not found: {output_file}")
        return []
    except Exception as e:
        print(f"Error loading embeddings: {str(e)}")
        return []

def search_embeddings(query, embeddings_data, top_k=5):
    """Search embeddings using cosine similarity"""
    if not embeddings_data:
        return []
    
    # Initialize the embedding processor
    processor = LightEmbeddingProcessor()
    
    # Create query embedding
    query_embedding = processor.create_embedding(query)
    
    # Calculate similarities
    similarities = []
    for item in embeddings_data:
        embedding = item['embedding']
        similarity = np.dot(query_embedding, embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
        similarities.append((similarity, item))
    
    # Sort by similarity and return top_k results
    similarities.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for similarity, item in similarities[:top_k]:
        results.append({
            'similarity': float(similarity),
            'content': item['content'],
            'file_path': item['file_path'],
            'source_url': item.get('source_url')
        })
    
    return results

if __name__ == "__main__":
    # Example usage
    input_folder = "extracted_content"
    output_file = "embeddings/embeddings_light.json"
    
    if os.path.exists(input_folder):
        process_text_files(input_folder, output_file)
    else:
        print(f"Input folder not found: {input_folder}")