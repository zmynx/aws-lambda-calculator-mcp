import { useState } from 'react'
import App from './App.jsx'
import AppWidget from './AppWidget.jsx'
import AppIframe from './AppIframe.jsx'
import './IndexPage.css'

function IndexPage() {
  const [selectedDemo, setSelectedDemo] = useState(null)

  if (selectedDemo === 'fullpage') {
    return <App />
  }

  if (selectedDemo === 'widget') {
    return <AppWidget />
  }

  if (selectedDemo === 'iframe') {
    return <AppIframe />
  }

  return (
    <div className="index-page">
      <header className="index-header">
        <div className="header-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <h1>AWS Lambda Cost Advisor</h1>
        <p>Choose how you want to integrate the chatbot</p>
      </header>

      <main className="demo-selector">
        <div className="demo-cards">
          <button
            className="demo-card"
            onClick={() => setSelectedDemo('fullpage')}
          >
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <path d="M9 9H15M9 12H15M9 15H12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <h2>Full Page</h2>
            <p>Dedicated chatbot page with full viewport</p>
            <ul>
              <li>Best for focused interactions</li>
              <li>Full-screen experience</li>
              <li>Direct link: /chatbot</li>
            </ul>
            <span className="try-button">Try Demo →</span>
          </button>

          <button
            className="demo-card"
            onClick={() => setSelectedDemo('widget')}
          >
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0035 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h2>Floating Widget</h2>
            <p>Chat bubble that opens as a popup</p>
            <ul>
              <li>Available on all pages</li>
              <li>Non-intrusive design</li>
              <li>Bottom-right corner</li>
            </ul>
            <span className="try-button">Try Demo →</span>
          </button>

          <button
            className="demo-card"
            onClick={() => setSelectedDemo('iframe')}
          >
            <div className="card-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="3" width="20" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <path d="M2 8H22" stroke="currentColor" strokeWidth="2"/>
                <path d="M8 3V8" stroke="currentColor" strokeWidth="2"/>
                <path d="M16 3V8" stroke="currentColor" strokeWidth="2"/>
              </svg>
            </div>
            <h2>Embedded (iframe)</h2>
            <p>Integrated into page layout</p>
            <ul>
              <li>Part of content flow</li>
              <li>Customizable placement</li>
              <li>Section-specific chat</li>
            </ul>
            <span className="try-button">Try Demo →</span>
          </button>
        </div>

        <div className="info-section">
          <h3>Integration Guide</h3>
          <div className="info-cards">
            <div className="info-card">
              <h4>For GitHub Pages</h4>
              <p>
                All versions work with GitHub Pages static hosting.
                Choose based on your site's design and user experience goals.
              </p>
            </div>
            <div className="info-card">
              <h4>Backend Required</h4>
              <p>
                To connect to your AgentCore runtime, you'll need an API Gateway
                endpoint. See deployment docs for setup instructions.
              </p>
            </div>
            <div className="info-card">
              <h4>Responsive Design</h4>
              <p>
                All versions are fully responsive and work great on mobile,
                tablet, and desktop devices.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default IndexPage
