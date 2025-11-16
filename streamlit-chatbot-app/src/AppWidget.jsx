import ChatWidget from './components/ChatWidget'
import './AppWidget.css'

function AppWidget() {
  return (
    <div className="demo-page">
      <header className="demo-header">
        <h1>Your GitHub Pages Website</h1>
        <p>This is a demo showing how the chatbot widget appears on your site</p>
      </header>

      <main className="demo-content">
        <section>
          <h2>About This Page</h2>
          <p>
            This demonstrates the floating chat widget in the bottom-right corner.
            Click the chat bubble to open the AWS Lambda Cost Advisor chatbot.
          </p>
        </section>

        <section>
          <h2>Widget Features</h2>
          <ul>
            <li>Fixed position in bottom-right corner</li>
            <li>Expands into a popup window when clicked</li>
            <li>Unread message counter</li>
            <li>Doesn't interfere with page content</li>
            <li>Fully responsive on mobile devices</li>
          </ul>
        </section>

        <section>
          <h2>Example Content</h2>
          <p>
            Your website content continues normally. The chat widget stays accessible
            from any page without taking up main content space.
          </p>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua.
          </p>
        </section>
      </main>

      {/* The floating chat widget */}
      <ChatWidget />
    </div>
  )
}

export default AppWidget
