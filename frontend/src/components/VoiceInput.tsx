import { useState, useRef, useEffect } from 'react'
import { Button, Badge } from './ui'
import { Mic, MicOff, Send, Volume2 } from 'lucide-react'

export interface VoiceInputProps {
  onSend?: (text: string) => void
  onVoiceStart?: () => void
  onVoiceEnd?: () => void
  placeholder?: string
  disabled?: boolean
}

const VoiceInput = ({
  onSend,
  onVoiceStart,
  onVoiceEnd,
  placeholder = '说点什么...',
  disabled = false,
}: VoiceInputProps) => {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [volume, setVolume] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  // 模拟音量变化
  useEffect(() => {
    if (!isRecording) return

    const interval = setInterval(() => {
      setVolume(Math.random() * 100)
    }, 100)

    return () => clearInterval(interval)
  }, [isRecording])

  const handleVoiceToggle = () => {
    if (isRecording) {
      setIsRecording(false)
      onVoiceEnd?.()
      // 这里应该停止语音识别
    } else {
      setIsRecording(true)
      onVoiceStart?.()
      // 这里应该启动语音识别
      // 模拟语音识别
      setTimeout(() => {
        setTranscript('这是语音识别的结果...')
      }, 2000)
    }
  }

  const handleSend = () => {
    const text = transcript || inputRef.current?.value || ''
    if (text.trim()) {
      onSend?.(text.trim())
      setTranscript('')
      if (inputRef.current) {
        inputRef.current.value = ''
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="w-full">
      {/* 语音识别状态 */}
      {isRecording && (
        <div className="mb-4 p-4 rounded-xl bg-slate-800/50 border border-emerald-500/30">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
              <span className="text-sm font-medium text-white">正在录音...</span>
            </div>
            <Badge variant="error" dot>
              录音中
            </Badge>
          </div>

          {/* 音量可视化 */}
          <div className="flex items-center gap-1 h-12">
            {Array.from({ length: 40 }).map((_, i) => {
              const height = Math.max(10, (Math.sin((i + volume) * 0.2) + 1) * 20)
              return (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-emerald-500 to-teal-400 rounded-full transition-all duration-75"
                  style={{ height: `${height}%` }}
                />
              )
            })}
          </div>

          {/* 识别结果预览 */}
          {transcript && (
            <div className="mt-3 p-3 rounded-lg bg-slate-900/50 border border-slate-700">
              <p className="text-sm text-slate-300">{transcript}</p>
            </div>
          )}
        </div>
      )}

      {/* 输入框 */}
      <div className="flex items-end gap-2">
        {/* 语音按钮 */}
        <Button
          variant={isRecording ? 'danger' : 'outline'}
          size="lg"
          onClick={handleVoiceToggle}
          disabled={disabled}
          className="shrink-0"
        >
          {isRecording ? (
            <MicOff className="w-5 h-5" />
          ) : (
            <Mic className="w-5 h-5" />
          )}
        </Button>

        {/* 文本输入 */}
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            placeholder={placeholder}
            disabled={disabled || isRecording}
            onKeyPress={handleKeyPress}
            defaultValue={transcript}
            className="
              w-full px-4 py-3 pr-12
              bg-slate-800 border border-slate-700
              rounded-xl text-white placeholder-slate-500
              focus:outline-none focus:ring-2 focus:ring-emerald-500
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          />

          {/* 音量指示器 */}
          {isRecording && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <Volume2 className="w-5 h-5 text-emerald-400 animate-pulse" />
            </div>
          )}
        </div>

        {/* 发送按钮 */}
        <Button
          variant="primary"
          size="lg"
          onClick={handleSend}
          disabled={disabled || isRecording}
          className="shrink-0"
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>

      {/* 提示文字 */}
      <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
        <span>支持语音输入和文字输入</span>
        <span>按 Enter 发送</span>
      </div>
    </div>
  )
}

export default VoiceInput
