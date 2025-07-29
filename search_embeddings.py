import json
import numpy as np
import os
from create_embeddings import EmbeddingProcessor, search_embeddings

def load_embeddings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert lists to numpy arrays for similarity calculations
    for item in data:
        item['embedding'] = np.array(item['embedding'])
    return data

def main():
    embeddings_file = "embeddings/embeddings.json"
    
    # Check if embeddings file exists
    if not os.path.exists(embeddings_file):
        print("Error: Embeddings file not found. Please run create_embeddings.py first.")
        return
    
    # Load embeddings
    print("Loading embeddings...")
    embeddings_data = load_embeddings(embeddings_file)
    print(f"Loaded {len(embeddings_data)} embeddings")
    
    # Interactive search loop
    while True:
        # Get search query from user
        query = input("\nEnter your search query (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        # Perform search with higher top_k to account for filtered results
        results = search_embeddings(query, embeddings_data, top_k=6)
        
        # Filter out results with "Estimated reading: 0 minutes"
        results = [r for r in results if "Estimated reading: 0 minutes" not in r['content']][:3]
        
        # Print results
        print(f"\nSearch results for: {query}")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity Score: {result['similarity']:.4f}")
            if result['source_url']:
                print(f"Source: {result['source_url']}")
            print(f"File: {result['file_path']}")
            print("-" * 40)
            print(f"Content preview: {result['content'][:300]}...")
            print("-" * 80)

if __name__ == "__main__":
    main()