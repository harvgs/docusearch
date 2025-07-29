import streamlit as st
import json
import numpy as np
import os
import warnings
import torch
import base64
from openai import OpenAIError, AuthenticationError, PermissionDeniedError
import tiktoken
from pathlib import Path
import sys

# Add the parent directory to system path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent
sys.path.append(str(parent_directory))

# Import the lighter embedding functions
try:
    from create_embeddings_light import search_embeddings, load_embeddings
except ImportError:
    # Fallback to original if light version not available
    from create_embeddings import search_embeddings, load_embeddings

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Health check for Railway
if os.getenv('RAILWAY_HEALTH_CHECK'):
    st.write("OK")
    st.stop()

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="onnxruntime")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sentence_transformers")
warnings.filterwarnings("ignore", message="Examining the path of torch.classes raised")
warnings.filterwarnings("ignore", message="Unsupported Windows version")

# Monkey patch torch.classes to avoid the warning
torch.classes = type('dummy', (), {'__getattr__': lambda self, attr: None})()

def test_network_connectivity():
    """Test basic network connectivity"""
    try:
        import requests
        response = requests.get("https://api.openai.com", timeout=5)
        return True, "Network connectivity OK"
    except requests.exceptions.ConnectionError:
        return False, "No internet connection"
    except requests.exceptions.Timeout:
        return False, "Network timeout"
    except Exception as e:
        return False, f"Network error: {str(e)}"

def validate_openai_key(api_key):
    """Test if the OpenAI API key is valid and working"""
    if not api_key or api_key == "your-openai-api-key-here":
        return False, "Please enter a valid OpenAI API key"
    
    # First test network connectivity
    network_ok, network_msg = test_network_connectivity()
    if not network_ok:
        return False, network_msg
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=10.0)
        # Try a simple test call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True, "API key is valid"
    except Exception as e:
        return False, f"API key validation failed: {str(e)}"

# Try to load OpenAI API key from config file or environment variable
project_api_key = None

# First try environment variable (Railway will set this)
project_api_key = os.getenv('OPENAI_API_KEY')

# If not in environment, try config files
if not project_api_key:
    config_paths = [
        r"C:\python\chat_bot\openai_config.json",
        os.path.join(parent_directory, "openai_config.json"),
        os.path.join(parent_directory, "config", "openai_config.json")
    ]

    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path) as json_file:
                    data = json.load(json_file)
                    project_api_key = data.get('openai', {}).get('api_key')
                    if project_api_key:
                        break
            except Exception as e:
                st.warning(f"Could not load config from {config_path}: {str(e)}")

# If no API key found, allow user to input it
if not project_api_key:
    st.sidebar.warning("OpenAI API key not found in environment or config files.")
    project_api_key = st.sidebar.text_input(
        "Enter your OpenAI API key:", 
        type="password",
        help="You can also set the OPENAI_API_KEY environment variable or create an openai_config.json file with your API key"
    )

# Add API key validation in sidebar
if project_api_key:
    is_valid, validation_msg = validate_openai_key(project_api_key)
    if is_valid:
        st.sidebar.success("✅ API key is valid")
    else:
        st.sidebar.error(f"❌ {validation_msg}")
        if "your-openai-api-key-here" in project_api_key:
            st.sidebar.info("💡 Please replace 'your-openai-api-key-here' with your actual API key")
        
        # Add troubleshooting help
        with st.sidebar.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            
            1. **No internet connection** - Check your network
            2. **Invalid API key** - Get a new key from [OpenAI](https://platform.openai.com/api-keys)
            3. **Rate limits** - Wait a moment and try again
            4. **Quota exceeded** - Check your OpenAI account balance
            5. **Corporate firewall** - Contact your IT department
            
            **Test your connection:**
            """)
            if st.button("Test Network"):
                network_ok, network_msg = test_network_connectivity()
                if network_ok:
                    st.success(network_msg)
                else:
                    st.error(network_msg)

@st.cache_data
def load_embeddings_data():
    # Try multiple possible paths for embeddings file
    embeddings_files = [
        "embeddings/embeddings_light.json",  # Current directory
        "embeddings/embeddings.json",        # Current directory
        os.path.join(parent_directory, "embeddings", "embeddings_light.json"),
        os.path.join(parent_directory, "embeddings", "embeddings.json"),
        "/app/embeddings/embeddings_light.json",  # Railway Docker path
        "/app/embeddings/embeddings.json",        # Railway Docker path
        "./embeddings/embeddings_light.json",     # Relative to current
        "./embeddings/embeddings.json"            # Relative to current
    ]
    
    for embeddings_file in embeddings_files:
        if os.path.exists(embeddings_file):
            try:
                st.info(f"Loading embeddings from: {embeddings_file}")
                return load_embeddings(embeddings_file)
            except Exception as e:
                st.warning(f"Failed to load {embeddings_file}: {str(e)}")
                continue
    
    # If no embeddings file found, create a minimal fallback
    st.warning("No embeddings file found. Creating minimal fallback embeddings...")
    
    try:
        # Create a minimal embeddings structure
        minimal_embeddings = {
            "embeddings": [],
            "documents": [
                {
                    "content": "This is a fallback document. Please upload your embeddings file or text files to generate proper embeddings.",
                    "source_url": "fallback",
                    "file_path": "fallback.txt"
                }
            ]
        }
        
        # Save the minimal embeddings
        os.makedirs("embeddings", exist_ok=True)
        with open("embeddings/embeddings_light.json", "w") as f:
            json.dump(minimal_embeddings, f)
        
        st.success("Created minimal fallback embeddings!")
        return minimal_embeddings
        
    except Exception as e:
        st.error(f"Failed to create fallback embeddings: {str(e)}")
    
    # If we get here, show debug info
    st.error("Error: No embeddings file found and could not create fallback.")
    
    # Debug: Show what files exist
    st.write("🔍 Debug: Checking for embeddings files...")
    for path in ["embeddings", "/app/embeddings", "./embeddings"]:
        if os.path.exists(path):
            st.write(f"Directory exists: {path}")
            try:
                files = os.listdir(path)
                st.write(f"Files in {path}: {files}")
            except Exception as e:
                st.write(f"Error listing {path}: {e}")
        else:
            st.write(f"Directory does not exist: {path}")
    
    st.stop()

def search_database(query, embeddings_data, k=5):
    results = search_embeddings(query, embeddings_data, top_k=k)
    return results

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

def create_download_button(source, key_prefix):
    key = f"{key_prefix}_{source}"
    # Try to find the source file in the extracted_content directory
    source_paths = [
        os.path.join(parent_directory, "extracted_content", source),
        os.path.join(parent_directory, "connections", source),
        source  # Try as absolute path
    ]
    
    for source_path in source_paths:
        if os.path.exists(source_path):
            with open(source_path, "rb") as file:
                btn = st.download_button(
                    label=f"Download {os.path.basename(source)}",
                    data=file,
                    file_name=os.path.basename(source),
                    mime="application/octet-stream",
                    key=key
                )
            return
    
    st.warning(f"Source file not found: {source}")

def get_chat_response(query, chat_history, embeddings_data):
    if not project_api_key:
        return "Please enter your OpenAI API key in the sidebar to enable chat functionality.", []
    
    try:
        from openai import OpenAI
        import requests
        
        # Search for relevant documents
        search_results = search_embeddings(query, embeddings_data, top_k=3)
        
        # Prepare context from search results
        context = ""
        sources = []
        for result in search_results:
            context += f"\n\nDocument: {result.get('source_url', result.get('file_path', 'Unknown'))}\nContent: {result['content'][:1000]}"
            sources.append({
                'source': result.get('source_url', result.get('file_path', 'Unknown')),
                'file_path': result.get('file_path', 'Unknown')
            })
        
        # Prepare chat history for the API
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that answers questions based on the provided documentation. Use only the information from the documents below to answer questions. If the information is not in the documents, say so.\n\nDocumentation:\n{context}"
            }
        ]
        
        # Add chat history
        for message in chat_history[-6:]:  # Keep last 6 messages for context
            messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        # Call OpenAI API with timeout and retry settings
        client = OpenAI(
            api_key=project_api_key,
            timeout=30.0,  # 30 second timeout
            max_retries=2
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        # Convert sources to Document format for compatibility
        source_docs = []
        for source in sources:
            # Create a simple document object without langchain
            doc = type('Document', (), {
                'page_content': "Source document",
                'metadata': source
            })()
            source_docs.append(doc)
        
        return answer, source_docs
        
    except ImportError as e:
        st.error(f"Missing required packages: {str(e)}")
        return "Please install required packages: pip install openai", []
    except AuthenticationError:
        st.error("Authentication failed. Please check your OpenAI API key.")
        return "I'm sorry, but there was an authentication error. Please check your API key.", []
    except PermissionDeniedError:
        st.error("Permission denied. Your API key may not have access to this model.")
        return "I'm sorry, but I don't have permission to access this feature. Please check your API key.", []
    except OpenAIError as e:
        error_msg = str(e)
        if "Connection error" in error_msg:
            st.error("Connection error. Please check your internet connection and try again.")
            return "I'm sorry, but I couldn't connect to OpenAI. Please check your internet connection and try again.", []
        elif "rate_limit" in error_msg.lower():
            st.error("Rate limit exceeded. Please wait a moment and try again.")
            return "I'm sorry, but the API rate limit has been exceeded. Please wait a moment and try again.", []
        elif "quota" in error_msg.lower():
            st.error("API quota exceeded. Please check your OpenAI account.")
            return "I'm sorry, but your OpenAI API quota has been exceeded. Please check your account.", []
        else:
            st.error(f"OpenAI API error: {error_msg}")
            return f"I'm sorry, but I encountered an error: {error_msg}", []
    except requests.exceptions.ConnectionError:
        st.error("Network connection error. Please check your internet connection.")
        return "I'm sorry, but I couldn't connect to the internet. Please check your connection and try again.", []
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return "I'm sorry, but the request timed out. Please try again.", []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        # Fallback to simple search-based response
        try:
            search_results = search_embeddings(query, embeddings_data, top_k=2)
            if search_results:
                response = "Based on the documentation:\n\n"
                for result in search_results:
                    response += f"- {result['content'][:200]}...\n\n"
                    if result.get('source_url'):
                        response += f"Source: {result['source_url']}\n\n"
                return response, []
            else:
                return "I couldn't find relevant information in the documentation for your query.", []
        except:
            return "I'm sorry, but I encountered an unexpected error. Please try again later.", []

def calculate_cost(prompt, response):
    try:
        model = "gpt-4o-mini"
        encoding = tiktoken.encoding_for_model(model)
        
        prompt_tokens = len(encoding.encode(prompt))
        response_tokens = len(encoding.encode(response))
        
        # Prices as of October 2024 for gpt-4o-mini
        input_price_per_1k = 0.000150
        output_price_per_1k = 0.000600
        
        prompt_cost = (prompt_tokens / 1000) * input_price_per_1k
        response_cost = (response_tokens / 1000) * output_price_per_1k
        
        total_cost = prompt_cost + response_cost
        return total_cost
    except Exception:
        return 0.0

st.title("Document Search and Chat (Light Version)")

# Load the embeddings
embeddings_data = load_embeddings_data()

# Sidebar for mode selection
mode = st.sidebar.radio("Choose mode:", ("Search", "Chat", "Documents"))

if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# Sidebar for configuration
with st.sidebar:
    st.title("🔧 Configuration")
    
    # OpenAI API Key input
    st.subheader("🔑 OpenAI API Key")
    api_key = st.text_input(
        "Enter your OpenAI API key",
        value=project_api_key or "",
        type="password",
        help="Get your API key from https://platform.openai.com/api-keys"
    )
    
    # Validate API key
    if api_key and api_key != project_api_key:
        is_valid, message = validate_openai_key(api_key)
        if is_valid:
            st.success("✅ " + message)
            project_api_key = api_key
        else:
            st.error("❌ " + message)
    
    # Model selection
    st.subheader("🤖 Model Selection")
    model = st.selectbox(
        "Choose the model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        help="gpt-4o-mini is recommended for cost and speed"
    )
    
    # Temperature setting
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative, lower values more focused"
    )
    
    # Max tokens setting
    max_tokens = st.slider(
        "Max tokens",
        min_value=100,
        max_value=4000,
        value=1000,
        step=100,
        help="Maximum length of the response"
    )
    
    # Search results count
    search_results = st.slider(
        "Search results",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
        help="Number of relevant documents to include in context"
    )

if mode == "Search":
    # Create a search box
    query = st.text_input("Enter your search query:")

    if query:
        results = search_database(query, embeddings_data)
        
        for i, result in enumerate(results, 1):
            st.subheader(f"Result {i}")
            st.write(f"**Similarity Score:** {result['similarity']:.4f}")
            st.write("**Content:**")
            st.write(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
            
            if result.get('source_url'):
                st.markdown(f"**Source:** [{result['source_url']}]({result['source_url']})")
            
            if result.get('file_path'):
                create_download_button(result['file_path'], f"search_{i}")
            
            st.markdown("---")

elif mode == "Chat":
    st.subheader("Chat with your documents")
    
    if not project_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to enable chat functionality.")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Display total session cost
    st.sidebar.markdown(f"**Total session cost: ${st.session_state.total_cost:.4f}**")

    # Accept user input
    if prompt := st.chat_input("What would you like to know about the documents?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chat response
        response, source_docs = get_chat_response(prompt, st.session_state.messages, embeddings_data)

        # Calculate cost
        cost = calculate_cost(prompt, response)
        
        # Update total cost
        st.session_state.total_cost += cost

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
            st.markdown("---")
            st.markdown("**Sources:**")
            
            # Remove duplicate sources
            unique_sources = {}
            for doc in source_docs:
                source = doc.metadata.get('source', 'Unknown')
                if source not in unique_sources:
                    unique_sources[source] = doc

            # Display unique sources and create download buttons
            for i, (source, doc) in enumerate(unique_sources.items()):
                st.markdown(f"- {source}")
                if doc.metadata.get('file_path'):
                    create_download_button(doc.metadata['file_path'], f"chat_{i}")
            
            st.markdown(f"**Cost of this interaction: ${cost:.4f}**")
            st.markdown(f"**Total session cost: ${st.session_state.total_cost:.4f}**")

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Update sidebar with new total cost
        st.sidebar.markdown(f"**Total session cost: ${st.session_state.total_cost:.4f}**")

else:  # Documents mode
    st.subheader("Document List")
    
    # Display document information from embeddings
    st.write(f"**Total documents loaded:** {len(embeddings_data)}")
    
    # Group documents by directory
    documents_by_dir = {}
    for item in embeddings_data:
        file_path = item.get('file_path', 'Unknown')
        dir_name = os.path.dirname(file_path) if file_path != 'Unknown' else 'Unknown'
        
        if dir_name not in documents_by_dir:
            documents_by_dir[dir_name] = []
        
        documents_by_dir[dir_name].append({
            'file_path': file_path,
            'source_url': item.get('source_url'),
            'content_preview': item['content'][:200] + "..." if len(item['content']) > 200 else item['content']
        })
    
    # Display documents grouped by directory
    for dir_name, docs in documents_by_dir.items():
        st.markdown(f"### {dir_name or 'Root Directory'}")
        st.write(f"**Number of documents:** {len(docs)}")
        
        for i, doc in enumerate(docs[:5]):  # Show first 5 documents per directory
            st.markdown(f"**{i+1}.** {os.path.basename(doc['file_path'])}")
            if doc['source_url']:
                st.markdown(f"Source: [{doc['source_url']}]({doc['source_url']})")
            st.markdown(f"Preview: {doc['content_preview']}")
            create_download_button(doc['file_path'], f"doc_list_{dir_name}_{i}")
            st.markdown("---")
        
        if len(docs) > 5:
            st.write(f"... and {len(docs) - 5} more documents")

st.sidebar.markdown("## About")
st.sidebar.info("This app searches and chats with documents using the 'all-MiniLM-L6-v2' model for embeddings and GPT-4o-mini for chat.")