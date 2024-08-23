'use client';
import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import FileUploader from '../components/FileUploader';
import ChatBox from '../components/ChatBox';
import InputBox from '../components/InputBox';

interface ChatMessage {
  sender: 'user' | 'bot';
  text?: string;
  reference?: string;
  extraction?: string;
  summary?: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onstart: () => void;
  onend: () => void;
  onresult: (event: any) => void;
  onerror: (event: any) => void;
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [userMessage, setUserMessage] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [botTyping, setBotTyping] = useState<boolean>(false);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const [listening, setListening] = useState<boolean>(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages, botTyping]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files ? e.target.files[0] : null);
  };

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

  const handleSendMessage = useCallback(async (message?: string) => {
    const finalMessage = String(userMessage || message).trim();
    if (!finalMessage) {
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

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const speechRecognition = new (window as any).webkitSpeechRecognition() as SpeechRecognition;
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
  }, [handleSendMessage]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
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
        <FileUploader handleFileChange={handleFileChange} handleUpload={handleUpload} />
        <ChatBox chatMessages={chatMessages} botTyping={botTyping} chatContainerRef={chatContainerRef} />
        <InputBox
          userMessage={userMessage}
          setUserMessage={setUserMessage}
          handleKeyDown={handleKeyDown}
          handleSendMessage={handleSendMessage}
          startListening={startListening}
          listening={listening}
        />
      </div>
    </div>
  );
};

export default App;
