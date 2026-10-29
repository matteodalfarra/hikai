import { useEffect, useState } from 'react'

function App() {
  const [status, setStatus] = useState('...')

  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
  }, [])

  return <h1>Backend status: {status}</h1>
}

export default App