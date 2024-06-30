import React, { useState } from 'react';
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

const Textarea = ({ value, onChange, placeholder, className }) => (
  <textarea
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`w-full p-3 border border-gray-300 rounded-lg resize-none ${className}`}
  />
);

const App = () => {
  const [file, setFile] = useState(null);
  const [userMessage, setUserMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);

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
    }
  };
  

  const handleSendMessage = async () => {
    if (!userMessage.trim()) {
      alert('Please enter a message');
      return;
    }

    try {
      const response = await axios.post(
        'http://localhost:8000/process-message',
        new URLSearchParams({ userMessage }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      const { Reference, Extraction, Summary } = response.data.botResponse;
      setChatMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'user', text: userMessage },
        { sender: 'bot', reference: Reference, extraction: Extraction, summary: Summary },
      ]);
      setUserMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message');
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
                  {message.res && (
                    <>
                    <p>{message.res}</p>
                    </>
                  )}
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
        </div>
        <div className="flex items-center">
          <Textarea
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            placeholder="Ask a question about the PDF"
            className="flex-grow"
          />
          <Button onClick={handleSendMessage} className="ml-2">
            Send
            <SendIcon className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default App;
