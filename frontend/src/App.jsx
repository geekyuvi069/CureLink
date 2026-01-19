import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="chat-container">
      <ChatInterface role="patient" />
    </div>
  );
}

export default App;
