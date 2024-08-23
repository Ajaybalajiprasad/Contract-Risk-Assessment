import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Avatar } from './SvgIcons';

interface ChatMessageProps {
  message: {
    sender: 'user' | 'bot';
    text?: string;
    reference?: string;
    extraction?: string;
    summary?: string;
  };
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  return (
    <div
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
          message.sender === 'user' ? 'bg-blue-200 text-black' : 'bg-gray-200'
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
  );
};

export default ChatMessage;
