import os
import torch
import json
import asyncio
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
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

    # Set the Hugging Face API token
    os.environ["HUGGINGFACEHUB_TOKEN"] = os.getenv('HUGGING_FACE_TOKEN')

    # Initialize the language model
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"
    llm_hub = HuggingFaceEndpoint(
        repo_id=model_id,
        task="text-generation",
        max_length=2000,
        temperature=0.4,
        top_p=0.9,
    )

    # Initialize the embeddings model if not already initialized
    if embeddings is None:
        embeddings = HuggingFaceInstructEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

async def process_document(document_path):
    global conversation_retrieval_chain

    persist_directory = "./contract"

    # Check if the persistent directory already exists
    if os.path.exists(persist_directory):
        # Load the existing Chroma vector store from the directory
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print("Loaded existing Chroma vector store from the directory.")
    else:
        # Process the documents and create a new vector store
        loader = PyPDFLoader(document_path)
        documents = await loader.load_async()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
        texts = text_splitter.split_documents(documents)

        db = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        db.persist()
        print("Created and persisted new Chroma vector store.")

    # Create the retriever from the Chroma vector store
    retriever = db.as_retriever(search_type="similarity", search_kwargs={'k': 2})

    conversation_retrieval_chain = RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="map_rerank",
        retriever=retriever,
        return_source_documents=True,
        input_key="question"
    )

async def process_prompt(prompt):
    global conversation_retrieval_chain
    global chat_history

    if conversation_retrieval_chain is None:
        raise ValueError("The document must be processed before querying.")

    output = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    answer = output["result"]
    sources = output["source_documents"]
    
    extraction = "\n".join([source.page_content for source in sources])
    summary = await generate_summary(extraction, prompt)

    chat_history.append((prompt, answer))

    return {
        "Question": prompt,
        "Reference": await generate_reference_clause(extraction),
        "Extraction": extraction,
        "Summary": summary
    }

async def generate_summary(extraction, prompt):
    summary_prompt = (
        f"Based on the following extraction and the question, provide a detailed summary if the question is available in the pdf else tell:\n\n"
        f"Extraction:\n{extraction}\n\n"
        f"Question:\n{prompt}\n\n"
        f"Summary:"
    )
    response = await llm_hub.generate_async(prompts=[summary_prompt])

    generated_text = response.generations[0][0].text if response and response.generations else "Summary not available."
    return generated_text.strip()


index = [
    'Meaning of Terms',
    '1.0 Applicability',
    '1.01 Order of Precedence of Documents',
    '1.1 Interpretation',
    '1.2 Definition',
    '1.3 Singular And Plural',
    'Credentials of Contractors',
    'Application for Registration',
    'Tenders for Works',
    'Tender Forms',
    'Omissions and Discrepancies',
    'Earnest Money',
    'Care in Submission of Tenders',
    'Consideration of Tenders',
    '7. Right of Railway to Deal with Tenders',
    '7A. Two Packets System of Tendering',
    'Contract Documents',
    '8. Execution of Contract Documents',
    '9. Form of Contract Documents',
    'Annexures',
    'Annexure-I',
    'Tender Form:',
    'First Sheet',
    'Second Sheet',
    'Third Sheet',
    'Annexure-II Agreement for Zone Contract',
    'Annexure-III Work Order Under Zone Contract',
    'Annexure-IV Form for Contract Agreement of Works',
    'Annexure-V Format for Affidavit to be submitted / Uploaded Tenderer along with the tender documents',
    'Annexure-VI Tenderer’s Credentials (Bid Capacity)',
    # New headings from the first image
    'Definitions And Interpretation',
    '(1) Definitions',
    '(2) Singular and Plural',
    '(3) Headings and Marginal Headings',
    'General Obligations',
    'Execution, Co-Relation and Intent Of Contract Documents',
    '(1) Law Governing the Contract',
    '(2) Compliance to Regulations and Bye-Laws',
    'Communication to be in Writing',
    'Service of Notices on Contractors',
    'Occupation and Use Of Land',
    'Assignment or Subletting of Contract',
    'Assistance by Railway for the Stores to be Obtained by the Contractor',
    'Railway Passes',
    'Carriage Of Materials',
    'Use of Ballast Train',
    'Representation on Works',
    'Relics and Treasures',
    'Excavated Material',
    'Indemnity by Contractors',
    '(1) Security Deposit',
    '(2) Refund of Security Deposit',
    '(3) Interest on Amount',
    '(4) Performance Guarantee',
    'Force Majeure Clause',
    'Extension Of Time in Contracts',
    '(i) Extension due to Modification',
    '(ii) Extension for Delay not due to Railway or Contractor',
    '(iii) Extension for Delay due to Railways',
    'Extension Of Time for Delay due to Contractor',
    'Bonus for Early Completion of Work',
    'Illegal Gratification',
    'Execution Of Works',
    '(1) Contractor\'s Understanding',
    '(2) Commencement Of Works',
    # Additional headings from the second image
    'Demurrage and Wharfage Dues',
    'Rates for Extra Items of Works',
    '(1) Handing over of Works',
    '(2) Clearance of Site on Completion',
    '2% off loading of work',
    'Variations in Extent of Contract',
    'Modification to Contract to be in Writing',
    'Power of Modifications to Contract',
    'Valuation of Variations',
    'Claims',
    '(1) Quarterly Statement of Claims',
    '(2) Signing of No Claim Certificate',
    'Measurement, Certificates and Payments',
    'Quantities in Schedule Annexed to Contract',
    'Measurements of Works',
    '(1) "On Account" Payments',
    '(2) Rounding off Amounts',
    '(3) "On Account" Payments not Prejudicial to Final Settlement',
    '(4) Manner of Payment',
    'Price Variation Clause (PVC)',
    'Maintenance of Works',
    '(1) Certificate of Completion of Works',
    '(2) Contractor not Absolved by Completion Certificate',
    '(3) Final Supplementary Agreement',
    'Approval only by Maintenance Certificate',
    '(1) Maintenance Certificate',
    '(2) Cessation of Railway\'s Liability',
    '(3) Unfulfilled Obligations',
    '(1) Final Payment',
    '(2) Post Payment Audit',
    'Production of Vouchers etc. by the Contractor',
    'Withholding and Lien in Respect of Sums Claimed',
    'Lien in Respect of Claims in Other Contracts',
    'Signature on Receipts for Amounts',
    'Labour',
    'Wages to Labour',
    'Apprentices Act',
    'Provisions of Payments of Wages Act',
    # New headings from the third image
    'Provisions of Contract Labour (Regulation and Abolition) Act, 1970',
    'Provisions of Employees Provident Fund and Miscellaneous Provisions Act, 1952',
    'Shramikkalyan Portal',
    'Provisions of "The Building and Other Construction Workers (RECS) Act, 1996" and "The Building and Other Construction Workers’ Welfare Cess Act, 1996"',
    'Reporting of Accidents',
    'Provision of Workmen\'s Compensation Act',
    'Provision of Mines Act',
    'Railway not to Provide Quarters for Contractors',
    '(1) Labour Camps',
    '(2) Compliance to Rules for Employment of Labour',
    '(3) Preservation of Peace',
    '(4) Sanitary Arrangements',
    '(5) Outbreak of Infectious Diseases',
    '(6) Treatment of Contractor\'s Staff in Railway Hospitals',
    '(7) Medical Facilities at Site',
    '(8) Use of intoxicants',
    '(9) Restriction on the Employment of Retired Engineers of Govt. Services within One Year of their Retirement',
    '(1) Non-Employment of Labourers below the age of 15 Years',
    '(2) Medical Certificate of Fitness for Labour',
    '(3) Period of Validity of Medical Fitness Certificate',
    '(4) Medical Re-Examination of Labourer',
    'Determination of Contract',
    '(1) Right of Railway to Determine the Contract',
    '(2) Payment on Determination of Contract',
    '(3) No Claim on Compensation',
    '(1) Determination of Contract owing to Default of Contractor',
    '(2) Right of Railway after Rescission of Contract owing to Default of Contractor',
    'Settlement of Disputes',
    'Conciliation of Disputes',
    '(1) Matters finally Determined by the Railway',
    '(1) Demand for Arbitration',
    '(2) Obligations During Pendency of Arbitration',
    '(3) Appointment of Arbitrator',
    '(4), (5), (6) & (7) - Arbitral Award & General',
    # New headings from the fourth image
    'Annexures',
    'Annexure-VII Proforma for Time Extension',
    'Annexure-VIII Certificate of Fitness',
    'Annexure-IX Proforma of 7 Days\' Notice',
    'Annexure-X Proforma of 48 Hrs. Notice',
    'Annexure-XI Proforma of Termination Notice',
    'Annexure-XII Proforma of 48 Hrs. Notice (Part Termination)',
    'Annexure-XIII Proforma of termination Notice (Part Termination)',
    'Annexure-XIV Final Supplementary Agreement',
    'Annexure-XV Agreement towards Waiver Under Section 12(5) and Section 31(A)(5) of Arbitration and Conciliation (Amendment) Act',
    'Annexure-XVI Certification by Arbitrators appointed under Clause 63 & 64 of Indian Railways General Conditions of Contract'
]

async def generate_reference_clause(extraction):
    matching_prompt = (
        f"Identify and return the most relevant heading and name it as Heading and then from the following index list that present in the content in the given text. The heading should be selected based on the presence of whole heading from the index that is present in the extraction Text. If the exact heading isn't found, pick the closest match based on the content fron th Index. If there is a subheading above the given extraction name it as a subheading and then, mention it appropriately from the Index, but if no subheading is relevant, leave the subheading blank.\n\n"
        f"Index:\n{', '.join(index)}\n\n"
        f"Text:\n{extraction}\n\n"
        f"Relevant Heading:"
    )
    
    response = await llm_hub.generate_async(prompts=[matching_prompt])
    matching_term = response.generations[0][0].text.strip() if response and response.generations else "Reference not found in predefined terms"

    return matching_term

async def main():
    init_llm()

    # Uncomment the following lines to test the code
    # await process_document_async('./GCC_July_2020.pdf')
    # prompt = "What is the role of the GCC in the global economy?"
    # result = await process_prompt(prompt)
    # print(result)

if __name__ == "__main__":
    asyncio.run(main())