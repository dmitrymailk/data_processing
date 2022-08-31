import { MemoryRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { useState, useEffect } from 'react';
const ipcRenderer = window.electron.ipcRenderer;

const Hello = () => {
  const [text, setText] = useState('qqq');
  useEffect(() => {
    async function fetchData() {
      const result = await ipcRenderer.invoke('my-invokable-ipc');
      // console.log(result);
      setText(result);
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1>Some data</h1>
      <p>{text}</p>
    </div>
  );
};

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Hello />} />
      </Routes>
    </Router>
  );
}
