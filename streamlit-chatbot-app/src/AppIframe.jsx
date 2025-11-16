import './AppIframe.css'

function AppIframe() {
  return (
    <div className="iframe-demo-page">
      <header className="iframe-demo-header">
        <h1>Your GitHub Pages Website</h1>
        <p>This demonstrates the chatbot embedded as an iframe</p>
      </header>

      <main className="iframe-demo-content">
        <section className="content-section">
          <h2>Page Content</h2>
          <p>
            This is your regular page content. The chatbot is embedded below
            as an iframe component that integrates into the page layout.
          </p>
        </section>

        <section className="chatbot-section">
          <h2>AWS Lambda Cost Advisor</h2>
          <p>Ask questions about Lambda pricing, costs, and optimizations:</p>

          {/* Embedded chatbot iframe */}
          <div className="chatbot-iframe-container">
            <iframe
              src="/chatbot.html"
              title="AWS Lambda Cost Advisor Chatbot"
              className="chatbot-iframe"
            />
          </div>
        </section>

        <section className="content-section">
          <h2>More Content Below</h2>
          <p>
            Your website content continues after the chatbot.
            This layout works well for dedicated sections or landing pages.
          </p>
          <ul>
            <li>Integrated into page flow</li>
            <li>Fixed height or responsive sizing</li>
            <li>Can be placed anywhere in content</li>
            <li>Good for dedicated chatbot pages</li>
          </ul>
        </section>
      </main>
    </div>
  )
}

export default AppIframe
