import logging
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import gpt4o_worker as wk  # Import this for openai
import huggingface_worker as worker2  # Import this for huggingface

# Initialize FastAPI app and CORS
app = FastAPI()
worker = wk.Worker()  # Default to gpt-4-0
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

templates = Jinja2Templates(directory="/backend/templates")

# Define the route for the index page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define the route for setting the model
@app.post("/set-model")
async def set_model_route(model_name: str = Form(...)):
    global worker
    if model_name == "gpt-4-0":
        worker = wk.Worker()  # Initialize with GPT-4-0
    elif model_name == "mistral":
        worker = worker2.Worker()  # Initialize with Mistral
    else:
        raise HTTPException(status_code=400, detail="Invalid model name")
    return JSONResponse(content={"message": f"Model set to {model_name}"}, status_code=200)

# Define the route for processing messages
@app.post("/process-message")
async def process_message_route(userMessage: str = Form(...)):
    logger.debug(f"user_message: {userMessage}")

    if not userMessage:
        raise HTTPException(status_code=400, detail="Please provide a message to process.")

    bot_response = worker.process_prompt(userMessage)  # Process the user's message using the worker module
    return JSONResponse(content={"botResponse": bot_response}, status_code=200)

# Define the route for processing documents
@app.post("/process-document")
async def process_document_route(file: UploadFile = File(...)):
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file selected. Please try again.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        logger.debug(f"Saving file to {file_path}")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        logger.debug(f"File saved successfully to {file_path}")

        worker.process_document(file_path)  # Process the document using the worker module

        return JSONResponse(content={
            "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any questions regarding it!",
        }, status_code=200)
    except Exception as e:
        logger.error(f"Error saving or processing document: {e}")
        raise HTTPException(status_code=500, detail="There was an error processing your document.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=False)
