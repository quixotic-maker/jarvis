import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface InputBoxProps {
  onSubmit: (input: string) => Promise<void>
  placeholder?: string
}

export default function InputBox({ onSubmit, placeholder = '输入您的指令...' }: InputBoxProps) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    setLoading(true)
    try {
      await onSubmit(input)
      setInput('')
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        disabled={loading}
        className="w-full bg-slate-700 text-white px-6 py-4 pr-14 rounded-xl border border-slate-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder-slate-400 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={!input.trim() || loading}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
      >
        {loading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </button>
    </form>
  )
}
