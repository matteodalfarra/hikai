import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import Markdown from 'react-markdown'
import { streamChat, type Message } from './api/chat'
import './App.css'

const EXAMPLES = [
  'A half-day loop with a mountain hut for lunch',
  'An easy walk with kids, max 1.5 hours',
  'I am an expert, a via ferrata in the Sella group',
  'A summit above 3000 m',
]

type Theme = 'light' | 'dark'

function getInitialTheme(): Theme {
  const saved = localStorage.getItem('theme')
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia('(prefers-color-schema: dark)').matches ? 'dark' : 'light'
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(text: string) {
    const content = text.trim()
    if (!content || loading) return

    const history: Message[] = [
      ...messages.filter((message) => message.content),
      { role: 'user', content },
    ]
    setMessages([...history, { role: 'assistant', content: '' }])
    setInput('')
    setError('')
    setLoading(true)

    try {
      await streamChat(history, (event) => {
        if (event.type === 'token') {
          setMessages((current) => {
            const last = current[current.length - 1]
            return [...current.slice(0, -1), { ...last, content: last.content + event.text }]
          })
        } else if (event.type === 'error') {
          setError(event.text)
        }
      })
    } catch {
      setError('Cannot reach the server. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    send(input)
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send(input)
    }
  }

  function newChat() {
    setMessages([])
    setError('')
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 20l6-11 4 6 2-3 6 8z" />
          </svg>
          Hikai
        </span>
        <div className="actions">
          <button
            className="icon-button"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <svg key={theme} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
            ) : (
              <svg key={theme} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
              </svg>
            )}
          </button>
          <button className="new-chat" onClick={newChat} disabled={loading || messages.length === 0}>
            + New chat
          </button>
        </div>
      </header>

      <main className="content">
        {messages.length === 0 ? (
          <div className="empty">
            <h1>Where do you want to hike?</h1>
            <p>Describe your ideal hike in the Dolomites, in Italian or English.</p>
            <div className="examples">
              {EXAMPLES.map((example) => (
                <button key={example} className="example" onClick={() => send(example)}>
                  {example}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((message, index) => {
              if (!message.content && !loading) return null
              return (
                <div key={index} className={`message ${message.role}`}>
                  <div className="bubble">
                    {message.role === 'user' ? (
                      message.content
                    ) : message.content ? (
                      <Markdown>{message.content}</Markdown>
                    ) : (
                      <p className="thinking">Searching trails and weather…</p>
                    )}
                  </div>
                </div>
              )
            })}
            {error && <p className="error">{error}</p>}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <footer className="composer">
        <form onSubmit={handleSubmit}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your hike..."
            rows={1}
            disabled={loading}
          />
          <button type="submit" className="send" disabled={loading || !input.trim()} aria-label="Send">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 19V5M5 12l7-7 7 7" />
            </svg>
          </button>
        </form>
        <p className="credits">
          Weather data by <a href="https://open-meteo.com/">Open-Meteo.com</a>
        </p>
      </footer>
    </div>
  )
}

export default App