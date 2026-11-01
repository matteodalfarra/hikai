export type Message = {
    role: 'user' | 'assistant'
    content: string
}

type StreamEvent =
    | { type: 'token'; text: string }
    | { type: 'error'; text: string }
    | { type: 'done' }

export async function streamChat(messages: Message[], onEvent: (event: StreamEvent) => void) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
    })

    if (!response.ok || !response.body){
        onEvent({ type: 'error', text: 'Server error. Please try again.' })
        return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true){
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''

        for (const part of parts) {
            if (part.startsWith('data: ')) {
                onEvent(JSON.parse(part.slice('data: '.length)))
            }
        }
    }
}