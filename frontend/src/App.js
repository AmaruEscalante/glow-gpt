import React, { useEffect, useRef, useState } from 'react';

const styles = {
  container: {
    backgroundColor: '#2E1a47',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    marginTop: '20px',
    color: '#ffffff',
    fontSize: '2xl',
    fontWeight: 'bold',
    lineHeight: '4',
    textAlign: 'center',
    letterSpacing: 'tight',
  },
  chatbox: {
    backgroundColor: '#493266',
    padding: '20px',
    borderRadius: '10px',
    width: '500px',
    height: '600px',
    overflowY: 'scroll',
    overflowX: 'hidden',
  },
  input: {
    width: '100%',
    padding: '10px',
    marginBottom: '10px',
    borderRadius: '5px',
    borderColor: '#Ebd4df',
    color: '#Ebd4df',
    backgroundColor: '#2E1a47',
  },
  button: {
    backgroundColor: '#Ebd4df',
    padding: '10px 20px',
    borderRadius: '5px',
    border: 'none',
    cursor: 'pointer',
    width: '100%',
  },
  message: (from) => ({
    color: '#Ebd4df',
    borderRadius: '5px',
    padding: '10px',
    marginBottom: '10px',
    backgroundColor: from === 'user' ? '#770f4b' : '#aa0061',
    alignSelf: from === 'user' ? 'flex-end' : 'flex-start',
  }),
  thinking: {
    alignSelf: 'flex-start',
    color: '#Ebd4df',
  }
};

function App() {
  const [message, setMessage] = useState('');
  const [userId, setUserId] = useState('');
  const [messages, setMessages] = useState([]);
  const [isThinking, setThinking] = useState(false); // Add new state for bot thinking

  // Scroll hook reference
  const messagesEndRef = useRef(null)

  // Add automatic scroll to bottom functionality
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // Trigger scroll to bottom every time a new message is sent
  useEffect(scrollToBottom, [messages]);
  

  const sendMessage = async () => {
    setMessages(messages => [...messages, { message, from: 'user' }]);
    setMessage(''); // Clear the message input after sending
    setThinking(true); // set thinking state to true
    
    const response = await fetch(`http://localhost:8000/chat?user_id=${userId}&message=${encodeURIComponent(message)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    setMessages(messages => [...messages, { message: data.message, from: 'bot' }]); // Add bot response
    setThinking(false); // set thinking state back to false
  };

  if (!userId) {
    return (
      <div style={styles.container}>
        <div style={styles.title}>GlowGPT</div>
        <div style={styles.chatbox}>
          <input
            type="text"
            placeholder="Enter user_id"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            style={styles.input}
          />
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.title}>GlowGPT</div>
      <div style={styles.chatbox}>
        <div style={{ flexGrow: '1', overflow: 'auto' }}> 
          {messages.map((m, index) => (
            <div style={styles.message(m.from)} key={index}>
              <p>{m.from === 'user' ? '🙂' : '🤖'}</p>
              <p>{m.message}</p>
            </div>
          ))}
          {isThinking && <p style={styles.thinking}>Bot is typing...</p>}
          <div ref={messagesEndRef} />  
        </div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={styles.input}
        />
        <button onClick={sendMessage} style={styles.button}>Send Message</button>
      </div>
    </div>
  );
}

export default App;
