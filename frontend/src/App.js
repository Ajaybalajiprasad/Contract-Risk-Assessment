import React, { useState, useEffect } from 'react';
import axios from 'axios';
import 'tailwindcss/tailwind.css';

// SVG Icons
const UploadIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" x2="12" y1="3" y2="15" />
  </svg>
);

const SendIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const MicIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 1C10.895 1 10 1.895 10 3V12C10 13.105 10.895 14 12 14C13.105 14 14 13.105 14 12V3C14 1.895 13.105 1 12 1Z" />
    <path d="M19 10V11C19 15.418 15.418 19 11 19C6.582 19 3 15.418 3 11V10" />
    <path d="M12 19V23" />
    <path d="M8 23H16" />
  </svg>
);

const Avatar = ({ src, alt, fallback }) => (
  <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-300 flex items-center justify-center">
    {src ? <img src={src} alt={alt} className="w-full h-full object-cover" /> : fallback}
  </div>
);

const Button = ({ children, onClick, className }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white bg-gray-800 hover:bg-gray-900 transition duration-200 focus:outline-none ${className}`}
  >
    {children}
  </button>
);

const Textarea = ({ value, onChange, onKeyDown, placeholder, className }) => (
  <textarea
    value={value}
    onChange={onChange}
    onKeyDown={onKeyDown}
    placeholder={placeholder}
    className={`w-full p-3 border border-gray-300 rounded-lg resize-none ${className}`}
  />
);

const LoadingIndicator = () => (
  <div className="flex items-center justify-center p-3">
    <svg
      className="animate-spin h-5 w-5 text-gray-800"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      ></circle>
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
  </div>
);

const App = () => {
  const [file, setFile] = useState(null);
  const [userMessage, setUserMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [botTyping, setBotTyping] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [listening, setListening] = useState(false);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const speechRecognition = new window.webkitSpeechRecognition();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = false;
      speechRecognition.lang = 'en-US';

      speechRecognition.onstart = () => {
        setListening(true);
      };

      speechRecognition.onend = () => {
        setListening(false);
      };

      speechRecognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        setUserMessage(speechToText);
        handleSendMessage(speechToText);
      };

      speechRecognition.onerror = (event) => {
        console.error('Speech recognition error', event);
      };

      setRecognition(speechRecognition);
    } else {
      alert('Speech recognition not supported in this browser');
    }
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a PDF file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setBotTyping(true);

    try {
      const response = await axios.post('http://localhost:8000/process-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const botResponse = response.data.botResponse;

      setChatMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', text: botResponse },
      ]);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file');
    } finally {
      setBotTyping(false);
    }
  };

  const handleSendMessage = async (message) => {
    const finalMessage = message || userMessage;
    if (!finalMessage.trim()) {
      alert('Please enter a message');
      return;
    }

    setBotTyping(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/process-message',
        new URLSearchParams({ userMessage: finalMessage }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      const { Reference, Extraction, Summary } = response.data.botResponse;
      setChatMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'user', text: finalMessage },
        { sender: 'bot', reference: Reference, extraction: Extraction, summary: Summary },
      ]);
      setUserMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Upload pdf file first');
    } finally {
      setBotTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startListening = () => {
    if (recognition) {
      recognition.start();
    }
  };

  return (
    <div className="h-screen w-full flex flex-col justify-between items-center bg-gray-100 p-2">
      <div className="w-full h-full bg-white rounded-lg shadow-lg p-6 flex flex-col">
        <header className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-700">PDF Chatbot</h1>
        </header>
        <div className="flex items-center mb-6">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="p-2 border border-gray-300 rounded-lg"
          />
          <Button onClick={handleUpload} className="ml-2">
            Upload PDF
            <UploadIcon className="w-5 h-5 ml-2" />
          </Button>
        </div>
        <div className="flex-grow overflow-y-auto mb-4 p-4 border border-gray-300 rounded-lg bg-gray-50">
          {chatMessages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start ${message.sender === 'user' ? 'flex-row-reverse' : ''} mb-4`}
            >
              <Avatar
                src={message.sender === 'user' ? '/user-avatar.jpg' : '/bot-avatar.jpg'}
                alt={message.sender}
                fallback={message.sender[0]}
              />
              <div
                className={`ml-3 mr-3 p-3 rounded-lg ${
                  message.sender === 'user' ? 'bg-blue-200' : 'bg-gray-200'
                } max-w-[60%]`}
              >
                <strong>{message.sender === 'user' ? 'You' : 'Bot'}: </strong>
                <div>
                  {message.text && <p>{message.text}</p>}
                  {message.reference && (
                    <>
                      <p><strong>Reference:</strong> {message.reference}</p>
                      <br />
                    </>
                  )}
                  {message.extraction && (
                    <>
                      <p><strong>Extraction:</strong> {message.extraction}</p>
                      <br />
                    </>
                  )}
                  {message.summary && (
                    <>
                      <p><strong>Summary:</strong> {message.summary}</p>
                      <br />
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          {botTyping && <LoadingIndicator />}
        </div>
        <div className="flex items-center relative shadow-lg rounded-lg">
          <textarea
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the PDF"
            className="flex-grow p-4 rounded-lg border-2 border-gray-300 focus:border-gray-600 outline-none transition duration-200 ease-in-out"
            style={{ paddingRight: '5rem' }}
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-2">
            <button
              onClick={handleSendMessage}
              className="ml-2 bg-gray-900 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded-full inline-flex items-center"
            >
              Send
              <SendIcon className="w-5 h-5 ml-2" />
            </button>
            <button
              onClick={startListening}
              className={`ml-2 text-white font-bold py-2 px-4 rounded-full inline-flex items-center ${
                listening ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-900 hover:bg-gray-700'
              }`}
            >
              <MicIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
