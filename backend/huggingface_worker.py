import os
import torch
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceEndpoint
from langchain.docstore.document import Document
import logging

# Load environment variables
load_dotenv()

# Check for GPU availability and set the appropriate device for computation
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Global variables
conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None
docs = False

def init_llm():
    global llm_hub, embeddings

    # Set up the environment variable for HuggingFace and initialize the desired model
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')

    # Initialize the model with the correct task
    llm_hub = HuggingFaceEndpoint(
        repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        task="text-generation",
        temperature=0.4,
        top_p=0.9,
    )

    # Initialize embeddings using a pre-trained model to represent the text data
    embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_faiss_index():
    global conversation_retrieval_chain
    if os.path.isdir("./faiss_index"):
        # Load the saved FAISS index with dangerous deserialization allowed
        db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)

        # Build the QA chain, which utilizes the LLM and retriever for answering questions
        conversation_retrieval_chain = RetrievalQA.from_chain_type(
            llm=llm_hub,
            chain_type="stuff",
            retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
            return_source_documents=True,
            input_key="question"
        )
        logger.debug("FAISS index loaded successfully")

# Function to process a PDF document
def process_document(document_path):
    global conversation_retrieval_chain, docs

    # Load the document with PyMuPDF
    doc = fitz.open(document_path)
    combined_text = ""

    # Iterate over each page to extract text
    for page in doc:
        text = page.get_text("text")
        combined_text += text + "\n\n"

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(combined_text)
    documents = [Document(page_content=text) for text in texts]

    # Load or create FAISS index
    if os.path.isdir("./faiss_index"):
        db = FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)
        db.add_documents(documents)
    else:
        db = FAISS.from_documents(documents=documents, embedding=embeddings)

    # Save FAISS index
    db.save_local("./faiss_index")

    # Create RetrievalQA chain
    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 6, 'lambda_mult': 0.25}),
        return_source_documents=True,
        input_key="question"
    )
    docs = True
    logger.debug("Document processed and added to FAISS index")

def generate_summary(extraction, prompt):
    summary_prompt = (
        f"Based on the following extraction and the question, provide a detailed summary if the question is available in the PDF, otherwise indicate unavailability:\n\n"
        f"Extraction:\n{extraction}\n\n"
        f"Question:\n{prompt}\n\n"
        f"Summary:"
    )
    response = llm_hub.generate(prompts=[summary_prompt])
    generated_text = response.generations[0][0].text if response and response.generations else "Summary not available."
    return generated_text.strip()

def process_prompt(prompt):
    global conversation_retrieval_chain, chat_history, docs

    if not conversation_retrieval_chain:
        raise Exception("No document has been processed yet")

    # Query the model to get the answer and source documents
    try:
        output = conversation_retrieval_chain.invoke({"question": prompt, "chat_history": chat_history})
        answer = output["result"]
        sources = output["source_documents"]
        extraction = "\n".join([source.page_content for source in sources])

        return generate_summary(extraction, prompt)
    except Exception as e:
        logger.error(f"Error processing prompt: {e}")
        raise


# Initialize the language model
init_llm()

# Load the FAISS index
load_faiss_index()
