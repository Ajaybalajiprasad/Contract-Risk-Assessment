import os
import torch
from dotenv import load_dotenv
import pdfplumber
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceEndpoint

load_dotenv()

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

def init_llm():
    global llm_hub, embeddings

    os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    
    llm_hub = HuggingFaceEndpoint(
        repo_id=model_id,
        task="text-generation",
        max_length=2000,         
        temperature=0.4,
        top_p=0.9,
        add_to_git_credential=True
    )

    embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def process_document(document_path):
    global conversation_retrieval_chain

    loader = PyPDFLoader(document_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
    texts = text_splitter.split_documents(documents)

    persist_directory = "./chroma"
    db = Chroma.from_documents(texts, persist_directory=persist_directory,embeddings)
    db.persist()
    retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 2})

    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        input_key="question"
    )

def process_prompt(prompt):
    global conversation_retrieval_chain
    global chat_history

    if conversation_retrieval_chain is None:
        raise ValueError("The document must be processed before querying.")

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
    summary_prompt = f"Based on the following extraction and the question, provide a detailed summary if the question is available in the pdf else tell:\n\nExtraction:\n{extraction}\n\nQuestion:\n{prompt}\n\nSummary:"
    response = llm_hub.generate(prompts=[summary_prompt])
    
    if isinstance(response, type(response)):
        generated_text = response.generations[0][0].text
    else:
        raise ValueError("Unexpected response type from llm_hub.generate()")
    print(generated_text.strip())
    return generated_text.strip()

def generate_reference_clause(document_path, extraction):
    with pdfplumber.open(document_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and extraction in text:
                words = page.extract_words()
                for word in words:
                    if 'bold' in word['fontname'].lower():
                        return word['text']
    return extraction.split('\n')[0]

init_llm()