import { useState, useRef, useEffect } from 'react'
import './App.css'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import ChatHeader from './components/ChatHeader'

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hello! I'm your AWS Lambda Cost Optimization Advisor. Ask me about Lambda costs, architecture comparisons, or pricing information.",
      timestamp: new Date()
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return

    // Add user message to chat
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    // Add "Thinking..." message
    const thinkingId = Date.now() + 1
    const thinkingMsg = {
      id: thinkingId,
      type: 'assistant',
      content: 'Thinking...',
      timestamp: new Date(),
      isThinking: true
    }
    setMessages(prev => [...prev, thinkingMsg])

    try {
      // TODO: Replace with your actual API Gateway endpoint
      const API_ENDPOINT = import.meta.env.VITE_API_ENDPOINT || '/api/chat'

      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          sessionId: sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // Replace "Thinking..." message with actual response
      setMessages(prev =>
        prev.map(msg =>
          msg.id === thinkingId
            ? {
                ...msg,
                content: data.response || 'Sorry, I encountered an error processing your request.',
                isThinking: false
              }
            : msg
        )
      )
    } catch (error) {
      console.error('Error sending message:', error)

      // Replace "Thinking..." with error message
      setMessages(prev =>
        prev.map(msg =>
          msg.id === thinkingId
            ? {
                ...msg,
                type: 'error',
                content: `Error: ${error.message}. Please make sure the API endpoint is configured correctly.`,
                isThinking: false
              }
            : msg
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <ChatHeader />
      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="message assistant loading">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
      </div>
    </div>
  )
}

export default App
