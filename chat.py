import os
import torch
from dotenv import load_dotenv
import streamlit as st
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

def init_llm():
    global llm_hub, embeddings

    # Set up the environment variable for HuggingFace and initialize the desired model
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    
    # Initialize the model with the correct task without overriding
    llm_hub = HuggingFaceEndpoint(
        repo_id=model_id,
        task="text-generation",  # Specify the task explicitly
        max_length=2000,         # Increase max_length for longer responses
        temperature=0.7,         # Adjust temperature for more detailed responses
        top_p=0.9                # Adjust top_p for more varied responses
    )

    # Initialize embeddings using a pre-trained model to represent the text data
    embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to process a PDF document
def process_document(document_path):
    global conversation_retrieval_chain

    # Load the document
    loader = PyPDFLoader(document_path)
    documents = loader.load()

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)

    # Create an embeddings database using Chroma from the split text chunks
    db = Chroma.from_documents(texts, embedding=embeddings)

    # Build the QA chain, which utilizes the LLM and retriever for answering questions
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
        return_source_documents=True,  # Retrieve source documents for extraction
        input_key="question"
    )

# Function to process a user prompt
def process_prompt(prompt):
    global conversation_retrieval_chain
    global chat_history

    if conversation_retrieval_chain is None:
        raise ValueError("The document must be processed before querying.")

    # Query the model
    output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    answer = output["result"]
    sources = output["source_documents"]

    # Create extraction and summary
    extraction = "\n".join([source.page_content for source in sources])
    summary = generate_summary(extraction, prompt)

    # Update the chat history
    chat_history.append((prompt, answer))

    # Return the structured response
    return {
        "Question": prompt,
        "Reference": generate_reference_clause(extraction),
        "Extraction": extraction,
        "Summary": summary
    }

def generate_summary(extraction, prompt):
    # Use the LLM to generate a summary based on the extracted text and prompt
    summary_prompt = f"Based on the following extraction and the question, provide a detailed summary:\n\nExtraction:\n{extraction}\n\nQuestion:\n{prompt}\n\nSummary:"
    response = llm_hub.generate(prompts=[summary_prompt])
    
    # Extract the generated text from the first generation
    generated_text = response.generations[0][0].text
    
    return generated_text.strip()

def generate_reference_clause(extraction):
    # Simple heuristic to extract reference clause, this should be adjusted based on document structure
    reference_clause = extraction.split('\n')[0]  # Assume the first line contains the reference clause
    return reference_clause

# Initialize the language model
init_llm()

# Streamlit application
st.title("PDF Document Q&A")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    document_path = f"temp_{uploaded_file.name}"
    with open(document_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("PDF uploaded successfully")

    process_document(document_path)
    st.success("PDF processed successfully")

    user_question = st.text_input("Ask a question about the document:")
    #Result
    if st.button("Submit"):
        response = process_prompt(user_question)
        st.write("### Question:")
        st.write(response["Question"])
        st.write("### Reference:")
        st.write(response["Reference"])
        st.write("### Extraction:")
        st.write(response["Extraction"])
        st.write("### Summary:")
        st.write(response["Summary"])

        # Clean up uploaded file
        os.remove(document_path)
