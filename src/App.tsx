// src/App.tsx
import React, { useState } from 'react';

// Define a type for each message in the chat
type Message = {
  sender: "User" | "Bot";
  text: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message to the chat
    setMessages((prev) => [...prev, { sender: "User", text: input }]);

    try {
      // Send request to the FastAPI backend
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await response.json();

      // Add response from backend to the chat
      setMessages((prev) => [...prev, { sender: "Bot", text: data.answer }]);
    } catch (error) {
      console.error("Error fetching from backend:", error);
    }

    setInput("");  // Clear input after sending
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>RAG Chatbot</h1>
      <div style={{ border: "1px solid #ddd", padding: "1rem", height: "300px", overflowY: "scroll" }}>
        {messages.map((msg, index) => (
          <p key={index} style={{ textAlign: msg.sender === "User" ? "right" : "left" }}>
            <strong>{msg.sender}:</strong> {msg.text}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Type your message..."
        style={{ width: "80%", marginRight: "0.5rem" }}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;
