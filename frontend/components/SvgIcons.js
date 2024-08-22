// SVG Icons
export const UploadIcon = (props) => (
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

export const SendIcon = (props) => (
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

export const MicIcon = (props) => (
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

export const Avatar = ({ src, alt, fallback }) => (
  <div className="w-10 h-10 rounded-full overflow-hidden bg-gray-300 flex items-center justify-center">
    {src ? <img src={src} alt={alt} className="w-full h-full object-cover" /> : fallback}
  </div>
);

export const Button = ({ children, onClick, className }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-white bg-gray-800 hover:bg-gray-900 transition duration-200 focus:outline-none ${className}`}
  >
    {children}
  </button>
);

export const LoadingIndicator = () => (
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


export const Loader = () => (
<div className="flex justify-center items-center space-x-2 mt-2">
  <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse"></div>
  <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse delay-200"></div>
  <div className="w-2.5 h-2.5 bg-gray-600 rounded-full animate-pulse delay-400"></div>
</div>
);