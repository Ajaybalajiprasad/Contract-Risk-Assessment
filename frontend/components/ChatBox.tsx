import ChatMessage from './ChatMessage';
import { Loader } from './SvgIcons';

interface ChatMessageType {
  sender: 'user' | 'bot';
  text?: string;
  reference?: string;
  extraction?: string;
  summary?: string;
}

interface ChatBoxProps {
  chatMessages: ChatMessageType[];
  botTyping: boolean;
  chatContainerRef: React.RefObject<HTMLDivElement>;
}

const ChatBox: React.FC<ChatBoxProps> = ({ chatMessages, botTyping, chatContainerRef }) => {
  return (
    <div
      ref={chatContainerRef}
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
