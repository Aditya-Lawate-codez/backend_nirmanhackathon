import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [inputString, setInputString] = useState('');
  const [response, setResponse] = useState('');
  const [audioURL, setAudioURL] = useState('');
  const [transcript, setTranscript] = useState('');
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  const handleChange = (e) => {
    setInputString(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('https://backend-nirmanhackathon.onrender.com/getres', { input_string: inputString });
      setResponse(res.data.response);
      synthesizeText(res.data.response);
    } catch (error) {
      console.error("Error: ", error);
      setResponse("An error occurred while processing your request.");
    }
  };

  const synthesizeText = async (text) => {
    try {
      const res = await axios.post('https://backend-nirmanhackathon.onrender.com/synthesize', { text });
      const audioContent = res.data.audioContent;
      const audioBlob = new Blob([new Uint8Array(atob(audioContent).split('').map(char => char.charCodeAt(0)))], { type: 'audio/mp3' });
      const url = URL.createObjectURL(audioBlob);
      setAudioURL(url);
    } catch (error) {
      console.error("Error synthesizing text: ", error);
    }
  };

  const startRecording = async () => {
    setRecording(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    setMediaRecorder(recorder);

    let chunks = [];
    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = () => {
      const audioBlob = new Blob(chunks, { type: 'audio/wav' });
      chunks = [];
      recognizeSpeech(audioBlob);
    };

    recorder.start();
  };

  const stopRecording = () => {
    mediaRecorder.stop();
    setRecording(false);
  };

  const recognizeSpeech = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    try {
      const res = await axios.post('https://backend-nirmanhackathon.onrender.com/recognize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setTranscript(res.data.transcript);
      setInputString(res.data.transcript);
    } catch (error) {
      console.error("Error recognizing speech: ", error);
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
          {audioURL && (
            <div>
              <audio controls src={audioURL}></audio>
            </div>
          )}
        </div>
      )}
      <div>
        <h2>Voice Input:</h2>
        <button onClick={recording ? stopRecording : startRecording}>
          {recording ? 'Stop Recording' : 'Start Recording'}
        </button>
        {transcript && (
          <div>
            <h3>Transcript:</h3>
            <pre>{transcript}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
