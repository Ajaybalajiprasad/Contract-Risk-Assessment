import React from 'react';
import ChatMessage from './ChatMessage';
import { Loader } from '../components/SvgIcons';

const ChatBox = ({ chatMessages, botTyping, chatContainerRef }) => {
  return (
    <div
      ref={chatContainerRef} // Attach ref to the chat container
      className="flex-grow overflow-y-auto mb-4 p-4 border border-gray-300 rounded-lg bg-gray-50"
    >
      {chatMessages.map((message, index) => (
        <ChatMessage key={index} message={message} />
      ))}
      {botTyping && <Loader />}
    </div>
  );
};

export default ChatBox;
