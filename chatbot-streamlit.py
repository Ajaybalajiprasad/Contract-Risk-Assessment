import os
import torch
import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceEndpoint

# Load environment variables from .env file
load_dotenv()

# Check for GPU availability and set the appropriate device for computation.
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables
conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

# Streamlit interface
st.title("Document QA System")

# Initialize the language model
if "initialized" not in st.session_state:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"

    llm_hub = HuggingFaceEndpoint(
        repo_id=model_id,
        task="text-generation",  # Specify the task explicitly
        max_length=2000,         # Increase max_length for longer responses
        temperature=0.7,         # Adjust temperature for more detailed responses
        top_p=0.9,               # Adjust top_p for more varied responses
        add_to_git_credential=True
    )

    embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    st.session_state.initialized = True
    st.session_state.llm_hub = llm_hub
    st.session_state.embeddings = embeddings

# Upload a PDF document
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    document_path = "uploaded_file.pdf"
    loader = PyPDFLoader(document_path)
    documents = loader.load()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)

    # Create an embeddings database using Chroma from the split text chunks
    db = Chroma.from_documents(texts, embedding=st.session_state.embeddings)

    # Build the QA chain, which utilizes the LLM and retriever for answering questions
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=st.session_state.llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
        return_source_documents=True,  # Retrieve source documents for extraction
        input_key="question"
    )
    
    st.session_state.conversation_retrieval_chain = conversation_retrieval_chain

# Process a user prompt
prompt = st.text_input("Ask a question about the document:")

if prompt and "conversation_retrieval_chain" in st.session_state:
    conversation_retrieval_chain = st.session_state.conversation_retrieval_chain
    chat_history = st.session_state.chat_history if "chat_history" in st.session_state else []

    if conversation_retrieval_chain is None:
        st.error("The document must be processed before querying.")
    else:
        # Query the model
        output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
        answer = output["result"]
        sources = output["source_documents"]

        # Create extraction and summary
        extraction = "\n".join([source.page_content for source in sources])

        # Use the LLM to generate a summary based on the extracted text and prompt
        summary_prompt = f"Based on the following extraction and the question, provide a detailed summary:\n\nExtraction:\n{extraction}\n\nQuestion:\n{prompt}\n\nSummary:"
        response = st.session_state.llm_hub.generate(prompts=[summary_prompt])

        # Extract the generated text from the first generation
        if isinstance(response, type(response)):
            generated_text = response.generations[0][0].text
        else:
            st.error("Unexpected response type from llm_hub.generate()")
            generated_text = ""

        summary = generated_text.strip()

        # Simple heuristic to extract reference clause, this should be adjusted based on document structure
        reference_clause = extraction.split('\n')[0]  # Assume the first line contains the reference clause

        # Update the chat history
        chat_history.append((prompt, answer))
        st.session_state.chat_history = chat_history

        # Display the structured response
        st.subheader("Question:")
        st.write(prompt)
        st.subheader("Reference clause:")
        st.write(reference_clause)
        st.subheader("Extraction:")
        st.write(extraction)
        st.subheader("Summary:")
        st.write(summary)
