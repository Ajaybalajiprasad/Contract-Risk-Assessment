import logging
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import huggingface_worker as worker  # Import the worker module
from pydantic import BaseModel

# Initialize FastAPI app and CORS
app = FastAPI()

class Message(BaseModel):
    userMessage: str

# Set up CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define the route for processing messages
@app.post("/api/chat")
async def process_message_route(message: Message):
    user_message = message.userMessage
    logger.debug(f"user_message: {user_message}")

    if not user_message:
        raise HTTPException(status_code=400, detail="Please provide a message to process.")

    try:
        # Process the user's message using the worker module
        bot_response = worker.process_prompt(user_message)
        return JSONResponse(content={"botResponse": bot_response}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="There was an error processing your message.")

# Define the route for processing documents
@app.post("/process-document")
async def process_document_route(file: UploadFile = File(...)):
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file selected. Please try again.")

    # Define the path where the file will be saved in the uploads directory
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        logger.debug(f"Saving file to {file_path}")
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        logger.debug(f"File saved successfully to {file_path}")

        # Process the document using the worker module
        worker.process_document(file_path)

        return JSONResponse(content={
            "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any questions regarding it!"
        }, status_code=200)
    except Exception as e:
        logger.error(f"Error saving or processing document: {e}")
        raise HTTPException(status_code=500, detail="There was an error processing your document.")

# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
