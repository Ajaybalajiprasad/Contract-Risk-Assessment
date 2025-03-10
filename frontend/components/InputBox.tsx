import { SendIcon, MicIcon } from './SvgIcons';

interface InputBoxProps {
  userMessage: string;
  setUserMessage: (message: string) => void;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  handleSendMessage: () => void;
  startListening: () => void;
  listening: boolean;
}

const InputBox: React.FC<InputBoxProps> = ({
  userMessage,
  setUserMessage,
  handleKeyDown,
  handleSendMessage,
  startListening,
  listening,
}) => {
  return (
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
          disabled={!userMessage.trim()}
          className={`ml-4 px-4 py-2 rounded-lg text-white ${
          userMessage.trim() ? 'bg-gray-900 hover:bg-gray-600' : 'bg-gray-400 cursor-not-allowed'
        }`}        >
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
  );
};

export default InputBox;
