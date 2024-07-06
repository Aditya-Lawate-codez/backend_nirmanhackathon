import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [inputString, setInputString] = useState('');
  const [response, setResponse] = useState('');

  const handleChange = (e) => {
    setInputString(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('https://backend-nirmanhackathon.onrender.com/getres', { input_string: inputString });
      setResponse(res.data);
    } catch (error) {
      console.error("Error: ", error);
      setResponse("An error occurred while processing your request.");
    }
  };

  return (
    <div className="App">
      <h1>Customer Service Assistant</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={inputString}
          onChange={handleChange}
          placeholder="Type your message here..."
        />
        <button type="submit">Send</button>
      </form>
      {response && (
        <div>
          <h2>Response:</h2>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
