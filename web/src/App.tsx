import { FormEvent, useState } from 'react'

type Source = { id: string; label: string; category?: string; document_type: string }
type Related = { question: string; answer?: string; score: number; category?: string }
type Detail = { id: string; label: string; score: number; category?: string; document_type: string }
type ChatResponse = {
  answer: string
  response_type: 'direct_answer' | 'related_results' | 'no_reliable_answer'
  confidence: number
  sources: Source[]
  related: Related[]
  response_mode: 'retrieval' | 'generative'
  retrieval_details: Detail[]
}

const suggestions = [
  'Can I show a CTA while my video is playing?',
  'What analytics does Vidzy provide?',
  'Can I export captured leads?',
  'How do I embed a Vidzy video?',
]

const categoryLabels: Record<string, string> = {
  account: 'Accounts',
  analytics: 'Video analytics',
  cta: 'Timed CTAs',
  customization: 'Player customization',
  'custom-domain': 'Custom domains',
  embed: 'Video embeds',
  'email-preview': 'Email previews',
  integration: 'Integrations',
  'lead-capture': 'Lead capture',
  plans: 'Plans & limits',
  player: 'Video player',
  popup: 'Video popups',
  security: 'Video access',
  video: 'Video sources',
}

function formatCategory(category?: string) {
  if (!category) return 'General'
  return categoryLabels[category] ?? category.split('-').map((word) => `${word[0]?.toUpperCase() ?? ''}${word.slice(1)}`).join(' ')
}

function sourceDisplayLabel(source: Source) {
  return source.category ? formatCategory(source.category) : 'Vidzy product knowledge'
}

function App() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<ChatResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [debug, setDebug] = useState(false)

  async function ask(question: string) {
    const trimmed = question.trim()
    if (trimmed.length < 2) return
    setMessage(trimmed)
    setLoading(true)
    setError('')
    setResult(null)
    setDebug(false)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })
      if (!response.ok) throw new Error('The knowledge service could not answer right now.')
      setResult((await response.json()) as ChatResponse)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void ask(message)
  }

  return (
    <main>
      <header className="nav">
        <a className="brand" href="/" aria-label="Vidzy Knowledge home">
          <span className="brand-mark">V</span>
          <span>Vidzy <em>Knowledge</em></span>
        </a>
        <div className="verified"><i /> Verified public knowledge</div>
      </header>

      <section className={`hero${result ? ' has-result' : ''}`}>
        <div className="eyebrow">Retrieval-first product guide</div>
        <h1>Ask Vidzy.<br /><span>Get grounded answers.</span></h1>
        <p className="lede">Explore Vidzy capabilities through answers retrieved from verified product knowledge—with safe no-answer behavior when evidence is missing.</p>

        <form className="ask" onSubmit={submit}>
          <label htmlFor="question">Your question</label>
          <div className="input-row">
            <textarea
              id="question"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              maxLength={500}
              placeholder="Can I add a call-to-action during playback?"
              rows={2}
            />
            <button disabled={loading || message.trim().length < 2} type="submit" aria-label="Ask question">
              {loading ? <span className="spinner" /> : <span>Ask <b>↗</b></span>}
            </button>
          </div>
          <div className="counter">{message.length} / 500</div>
        </form>

        {!result && !loading && !error && (
          <div className="suggestions">
            <span>Try asking</span>
            <div>{suggestions.map((item) => <button key={item} onClick={() => void ask(item)}>{item}</button>)}</div>
          </div>
        )}

        {loading && <div className="status-card"><span className="pulse" /><div><b>Searching verified knowledge</b><small>Comparing your question with canonical answers…</small></div></div>}
        {error && <div className="error-card"><b>We hit a snag.</b><span>{error}</span></div>}

        {result && (
          <article className={`answer ${result.response_type}`}>
            <div className="answer-top">
              <span className="answer-state">{result.response_type === 'direct_answer' ? 'Verified answer' : result.response_type === 'related_results' ? 'Related information' : 'No reliable answer'}</span>
            </div>
            <p>{result.answer}</p>
            {result.sources.length > 0 && <div className="sources"><b>Source</b>{result.sources.map((source) => <span key={source.id}><i aria-hidden="true">✓</i>{sourceDisplayLabel(source)}</span>)}</div>}
            {result.related.length > 0 && <div className="related"><b>Related questions</b>{result.related.map((item) => <button key={item.question} onClick={() => void ask(item.question)}><span>{item.question}</span><i>→</i></button>)}</div>}
            {result.retrieval_details.length > 0 && (
              <div className="debug">
                <button type="button" className="debug-toggle" aria-expanded={debug} onClick={() => setDebug(!debug)}>{debug ? 'Hide' : 'Show'} retrieval details <i aria-hidden="true">⌄</i></button>
                {debug && (
                  <div className="debug-panel">
                    <div className="debug-mode"><span>Response mode</span><b>{result.response_mode}</b></div>
                    <div className="debug-grid">
                      {result.retrieval_details.map((item, index) => (
                        <div className="debug-item" key={item.id || `${item.label}-${index}`}>
                          <div className="debug-item-top"><span>Match {String(index + 1).padStart(2, '0')}</span><b>{(item.score * 100).toFixed(1)}% similarity</b></div>
                          <p>{item.label}</p>
                          <dl>
                            <div><dt>Category</dt><dd>{formatCategory(item.category)}</dd></div>
                            <div><dt>Document</dt><dd>{item.document_type === 'canonical_question' ? 'Canonical question' : 'Public knowledge'}</dd></div>
                            <div><dt>Source ID</dt><dd>{item.id}</dd></div>
                          </dl>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </article>
        )}
      </section>

      <footer>
        <span>Local embeddings</span><i /> <span>LangChain retrieval</span><i /> <span>Chroma vector store</span>
        <p>Answers are limited to reviewed public knowledge. Internal material is isolated from this assistant.</p>
      </footer>
    </main>
  )
}

export default App
