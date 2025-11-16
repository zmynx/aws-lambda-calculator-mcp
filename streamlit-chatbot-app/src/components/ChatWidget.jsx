import { useState, useRef, useEffect } from 'react'
import './ChatWidget.css'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
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
  const [unreadCount, setUnreadCount] = useState(0)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return

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

      // Increment unread if widget is closed
      if (!isOpen) {
        setUnreadCount(prev => prev + 1)
      }
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

  const toggleWidget = () => {
    setIsOpen(prev => !prev)
    if (!isOpen) {
      setUnreadCount(0)
    }
  }

  return (
    <div className="chat-widget">
      {/* Floating chat bubble */}
      <button
        className={`chat-bubble ${isOpen ? 'open' : ''}`}
        onClick={toggleWidget}
        aria-label="Toggle chat"
      >
        {!isOpen ? (
          <>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0035 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            {unreadCount > 0 && (
              <span className="unread-badge">{unreadCount}</span>
            )}
          </>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-window-header">
            <div className="header-info">
              <h3>Lambda Cost Advisor</h3>
              <p>Powered by AWS Bedrock</p>
            </div>
            <button className="close-button" onClick={toggleWidget}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>

          <div className="chat-window-messages">
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

          <div className="chat-window-input">
            <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatWidget
