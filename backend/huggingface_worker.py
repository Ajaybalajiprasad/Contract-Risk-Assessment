import os
import torch
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
# Load environment variables
load_dotenv()

# Set the device (GPU if available, else CPU)
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables

class Worker:
    def __init__(self):
        self.conversation_retrieval_chain = None
        self.chat_history = []
        self.llm_hub = None
        self.embeddings = None
        os.environ["HUGGINGFACEHUB_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')

        self.llm_hub = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.3",
            task="text-generation",
            max_length=2000,
            temperature=0.4,
            top_p=0.9,
        )
        #self.llm_hub = ChatOpenAI(temperature=0.4,model="gpt-4o",)

        self.embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#         self.embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-large"
#     # With the `text-embedding-3` class
#     # of models, you can specify the size
#     # of the embeddings you want returned.
#     # dimensions=1024
# )
       
    def process_document(self,document_path):
        persist_directory = "./.chroma"

        if os.path.exists(persist_directory):
            db = Chroma(persist_directory=persist_directory, embedding_function=self.embeddings)
            print("Loaded existing Chroma vector store from the directory.")
        else: 
            loader = PyPDFLoader(document_path)
            documents = loader.load()

            text_splitter = SemanticChunker(self.embeddings)
            texts = text_splitter.split_documents(documents)

            db = Chroma.from_documents(documents=texts, embedding=self.embeddings, persist_directory=persist_directory)

            db.persist()
            print("Created and persisted new Chroma vector store.")
        retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 2})

        self.conversation_retrieval_chain = RetrievalQA.from_chain_type(
            llm=self.llm_hub,
            chain_type="map_rerank",
            retriever=retriever,
            return_source_documents=True,
            input_key="question"
        )
   

    def process_prompt(self,prompt):

        if self.conversation_retrieval_chain is None:
            raise ValueError("Document must be processed before querying.")

        output = self.conversation_retrieval_chain({"question": prompt, "chat_history": self.chat_history})
        answer = output["result"]
        sources = output["source_documents"]

        extraction = "\n".join([source.page_content for source in sources])
        summary = self.generate_summary(extraction, prompt)

        self.chat_history.append((prompt, answer))

        return {
            "Question": prompt,
            "Reference": self.generate_reference_clause(extraction),
            "Extraction": extraction,
            "Summary": summary
        }

    def generate_summary(self,extraction, prompt):
        summary_prompt = (
            f"Based on the following extraction and the question, provide a detailed summary if the question is available in the PDF, otherwise indicate unavailability:\n\n"
            f"Extraction:\n{extraction}\n\n"
            f"Question:\n{prompt}\n\n"
            f"Summary:"
        )
        response = self.llm_hub.generate(prompts=[summary_prompt])
        generated_text = response.generations[0][0].text if response and response.generations else "Summary not available."
        return generated_text.strip()

    def generate_reference_clause(self,extraction):
        matching_prompt = (
            f"Identify and return the most relevant heading and name it as Heading. The heading should be selected based on the presence of a line that starts with either a number, a Roman numeral, or a newline character and ends with a colon, or starts and ends with two newline characters.\n\n"
            f"Text:\n{extraction}\n\n"
            f"Relevant Heading:"
        )
        response = self.llm_hub.generate(prompts=[matching_prompt])
        matching_term = response.generations[0][0].text.strip() if response and response.generations else "Reference not found."
        return f"Heading: {matching_term}"

# # Initialize the LLM and self.embeddings
# init_llm()