# Running the Application

## Windows

### Backend Service

1. Install `virtualenv`:
    ```bash
    pip install virtualenv
    ```

2. Create a new virtual environment named `demo`:
    ```bash
    virtualenv demo
    ```

3. Activate the virtual environment:
    ```bash
    demo\Scripts\activate
    ```

4. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

5. Install all required Python modules:
    ```bash
    pip install -r requirements.txt
    ```

6. Create a `.env` file in the `backend` directory with the following content:
    ```
    HUGGING_FACE_TOKEN=your_huggingface_access_token
    ```

7. Run the `server.py` file:
    ```bash
    python server.py
    ```

### Frontend Website

1. Open a new terminal.

2. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

3. Install the necessary JavaScript modules using `npm`:
    ```bash
    npm install
    ```

4. Run the website:
    ```bash
    npm run dev
    ```

## Linux / macOS

### Backend Service

1. Install `virtualenv`:
    ```bash
    pip install virtualenv
    ```

2. Create a new virtual environment named `demo`:
    ```bash
    python3 -m venv demo
    ```

3. Activate the virtual environment:
    ```bash
    source demo/bin/activate
    ```

4. Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

5. Install all required Python modules:
    ```bash
    pip install -r requirements.txt
    ```

6. Create a `.env` file in the `backend` directory with the following content:
    ```
    HUGGING_FACE_TOKEN=your_huggingface_access_token
    ```

7. Run the `server.py` file:
    ```bash
    python3 server.py
    ```

### Frontend Website

1. Open a new terminal.

2. Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

3. Install the necessary JavaScript modules using `npm`:
    ```bash
    npm install
    ```

4. Run the website:
    ```bash
    npm run dev
    ```

## Additional Notes

- For Linux and macOS users, ensure you have Python 3 and `npm` installed. If you encounter permission issues during the `npm install` step, consider using `sudo npm install`.
- For Windows users, ensure Python and `npm` are added to your system's PATH variable.
- The `HUGGING_FACE_TOKEN` environment variable is required for the backend to function. Replace
`your_huggingface_access_token` with your actual Hugging Face access token.
- The `server.py` file uses the `huggingface_hub` library to interact with the
Hugging Face model hub. This library requires an access token to function.