import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import 'tailwindcss/tailwind.css';
import { UploadIcon, SendIcon, MicIcon, Avatar, Button } from './ui/SvgIcons';
import ReactMarkdown from 'react-markdown';

const Loader = () => (
  <div className="flex justify-center items-center space-x-2 mt-2">
    <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse"></div>
    <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse delay-200"></div>
    <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse delay-400"></div>
  </div>
);

const App = () => {
  const [file, setFile] = useState(null);
  const [userMessage, setUserMessage] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [botTyping, setBotTyping] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [listening, setListening] = useState(false);

  const chatContainerRef = useRef(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const speechRecognition = new window.webkitSpeechRecognition();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = false;
      speechRecognition.lang = 'en-US';

      speechRecognition.onstart = () => setListening(true);
      speechRecognition.onend = () => setListening(false);
      speechRecognition.onresult = (event) => {
        const speechToText = event.results[0][0].transcript;
        setUserMessage(speechToText);
        handleSendMessage(speechToText);
      };
      speechRecognition.onerror = (event) => {
        console.error('Speech recognition error', event);
        alert('Speech recognition error occurred. Please try again.');
      };

      setRecognition(speechRecognition);
    } else {
      alert('Speech recognition not supported in this browser');
    }
  }, []);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages, botTyping]);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = useCallback(async () => {
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
      alert('Error uploading file. Please try again.');
    } finally {
      setBotTyping(false);
    }
  }, [file]);

  const handleSendMessage = useCallback(async (message) => {
    const finalMessage = String(message || userMessage);
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
      alert('Failed to send message. Make sure a PDF is uploaded first.');
    } finally {
      setBotTyping(false);
    }
  }, [userMessage]);

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
        <div
          ref={chatContainerRef} // Attach ref to the chat container
          className="flex-grow overflow-y-auto mb-4 p-4 border border-gray-300 rounded-lg bg-gray-50"
        >
          {chatMessages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start transition-opacity duration-300 ${
                message.sender === 'user' ? 'flex-row-reverse' : ''
              } mb-4`}
            >
              <Avatar
                src={message.sender === 'user' ? '/user-avatar.jpg' : '/bot-avatar.jpg'}
                alt={message.sender}
                fallback={message.sender[0]}
              />
              <div
                className={`ml-3 mr-3 p-3 rounded-lg ${
                  message.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'
                } max-w-[60%] break-words shadow-md`}
              >
                <strong>{message.sender === 'user' ? 'You' : 'Bot'}: </strong>
                <div className="whitespace-pre-wrap">
                  {message.text && <p>{message.text}</p>}
                  {message.reference && (
                    <>
                      <p className="mt-2"><strong>Reference:</strong> <ReactMarkdown>{message.reference}</ReactMarkdown></p>
                    </>
                  )}
                  {message.extraction && (
                    <>
                      <p className="mt-2"><strong>Extraction:</strong></p>
                      <ReactMarkdown>{message.extraction}</ReactMarkdown>
                    </>
                  )}
                  {message.summary && (
                    <>
                      <p className="mt-2"><strong>Summary:</strong> <ReactMarkdown>{message.summary}</ReactMarkdown></p>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          {botTyping && <Loader />}
        </div>
        <div className="flex items-center relative shadow-lg rounded-lg mt-4">
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
