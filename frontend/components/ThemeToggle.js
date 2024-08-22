import React from 'react';

const ThemeToggle = ({ darkMode, toggleTheme }) => (
  <button
    onClick={toggleTheme}
    className="ml-2 text-sm bg-gray-300 hover:bg-gray-400 text-black font-semibold py-2 px-4 rounded-full"
  >
    {darkMode ? 'Light Mode' : 'Dark Mode'}
  </button>
);

export default ThemeToggle;

