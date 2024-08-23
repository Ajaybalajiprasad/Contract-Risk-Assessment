import os
import torch
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceEndpoint

# Load environment variables
load_dotenv()

# Set the device (GPU if available, else CPU)
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables
conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

def init_llm():
    global llm_hub, embeddings

    os.environ["HUGGINGFACEHUB_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')

    llm_hub = HuggingFaceEndpoint(
        repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        task="text-generation",
        max_length=2000,
        temperature=0.4,
        top_p=0.9,
    )

    embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def process_document(document_path):
    global conversation_retrieval_chain

    persist_directory = "./contract"

    if os.path.exists(persist_directory):
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print("Loaded existing Chroma vector store from the directory.")
    else: 
        loader = PyPDFLoader(document_path)
        documents = loader.load()

        text_splitter = SemanticChunker(embeddings)
        texts = text_splitter.split_documents(documents)

        db = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=persist_directory)

        db.persist()
        print("Created and persisted new Chroma vector store.")
        
    retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 2})

    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="map_rerank",
        retriever=retriever,
        return_source_documents=True,
        input_key="question"
    )

def process_prompt(prompt):
    global conversation_retrieval_chain, chat_history

    if conversation_retrieval_chain is None:
        raise ValueError("Document must be processed before querying.")

    output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    answer = output["result"]
    sources = output["source_documents"]

    extraction = "\n".join([source.page_content for source in sources])
    summary = generate_summary(extraction, prompt)

    chat_history.append((prompt, answer))

    return {
        "Question": prompt,
        "Reference": generate_reference_clause(extraction),
        "Extraction": extraction,
        "Summary": summary
    }

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

def generate_reference_clause(extraction):
    matching_prompt = (
        f"Identify and return the most relevant heading and name it as Heading. The heading should be selected based on the presence of a line that starts with either a number, a Roman numeral, or a newline character and ends with a colon, or starts and ends with two newline characters.\n\n"
        f"Text:\n{extraction}\n\n"
        f"Relevant Heading:"
    )
    response = llm_hub.generate(prompts=[matching_prompt])
    matching_term = response.generations[0][0].text.strip() if response and response.generations else "Reference not found."
    return f"Heading: {matching_term}"

# Initialize the LLM and embeddings
init_llm()