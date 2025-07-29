import streamlit as st
import json
import numpy as np
import os
import sys
from pathlib import Path
import csv
from datetime import datetime

# Add the parent directory to system path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent
sys.path.append(str(parent_directory))

from create_embeddings import search_embeddings

def load_embeddings(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert lists to numpy arrays for similarity calculations
    for item in data:
        item['embedding'] = np.array(item['embedding'])
    return data

def main():
    # Add mode selection in sidebar
    mode = st.sidebar.radio("Choose mode:", ("Search", "Chat"))
    
    st.title("[Connections](http://connections/) Search")
    
    # Get absolute path to embeddings file
    embeddings_file = os.path.join(parent_directory, "embeddings", "embeddings.json")
    
    # Check if embeddings file exists
    if not os.path.exists(embeddings_file):
        st.error(f"Error: Embeddings file not found at {embeddings_file}. Please run create_embeddings.py first.")
        return
    
    # Load embeddings (only once when the app starts)
    @st.cache_data
    def load_cached_embeddings():
        return load_embeddings(embeddings_file)
    
    embeddings_data = load_cached_embeddings()
    
    if mode == "Search":
        search_interface(embeddings_data)
    else:  # Chat mode
        chat_interface(embeddings_data)

def search_interface(embeddings_data):
    # Search input
    query = st.text_input("Enter your search query:", key="search_input")
    
    if query:
        # Generate unique keys for each user's search results
        search_key = f"search_results_{query}"
        feedback_key = f"feedback_submitted_{query}"
        
        # Initialize results in session state if not already present
        if search_key not in st.session_state:
            # Perform search with higher top_k to account for filtered results
            results = search_embeddings(query, embeddings_data, top_k=4)
            
            # Filter out results with "Estimated reading: 0 minutes"
            results = [r for r in results if "Estimated reading: 0 minutes" not in r['content']][:2]
            
            # Store results in session state with query-specific key
            st.session_state[search_key] = results
            # Reset feedback state for new search
            st.session_state[feedback_key] = False
        
        # Display results from session state
        st.subheader(f"Search results for: {query}")
        
        for i, result in enumerate(st.session_state[search_key], 1):
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(f"**Score:** {result['similarity']:.4f}")
                with col2:
                    if result['source_url']:
                        st.markdown(f"**Source:** [{result['source_url']}]({result['source_url']})")
                
                st.write("**Content preview:**")
                st.write(result['content'][:300] + "...")
                st.markdown("---")
        
        # Initialize session state for feedback
        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = False
        
        # Modify feedback section
        if not st.session_state[feedback_key]:
            st.markdown("---")
            st.write("**Which source was most helpful?**")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            def submit_feedback(response, search_results, feedback_key):
                # Get the similarity score of the selected result
                if response == "First Source":
                    score = search_results[0]['similarity']
                elif response == "Second Source":
                    score = search_results[1]['similarity']
                else:  # Neither
                    score = None
                
                log_feedback(query, response, score)
                st.session_state[feedback_key] = True
            
            with col1:
                if st.button("First Source", key=f"first_{query}", 
                           on_click=submit_feedback, 
                           args=("First Source", st.session_state[search_key], feedback_key)):
                    pass
                    
            with col2:
                if st.button("Second Source", key=f"second_{query}", 
                           on_click=submit_feedback, 
                           args=("Second Source", st.session_state[search_key], feedback_key)):
                    pass
                    
            with col3:
                if st.button("Neither", key=f"neither_{query}", 
                           on_click=submit_feedback, 
                           args=("Neither", st.session_state[search_key], feedback_key)):
                    pass
        
        if st.session_state[feedback_key]:
            st.success("Thank you for your feedback!")

def chat_interface(embeddings_data):
    st.subheader("Chat with the documentation")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Search for relevant content
        results = search_embeddings(prompt, embeddings_data, top_k=3)
        
        # Construct response from search results
        response = "Based on the documentation:\n\n"
        for result in results:
            response += f"- {result['content'][:200]}...\n\n"
            if result['source_url']:
                response += f"Source: {result['source_url']}\n\n"

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

def log_feedback(query, feedback, similarity_score):
    csv_file = os.path.join(parent_directory, "search_feedback.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create file with headers if it doesn't exist
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Query', 'Feedback', 'Similarity Score'])
    
    # Append feedback
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, query, feedback, similarity_score])

if __name__ == "__main__":
    main()