import { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatAPI, ChatMessage, ChatSession } from '../api/client'
import Layout from '../components/Layout'
import { 
  Send, Plus, MessageSquare, Trash2, Bot, User, Mic, MicOff,
  Calendar, Bell, Mail, Cloud, Code, FileText, MapPin, Newspaper,
  Loader2, Copy, Check, ChevronRight, Sun, Moon, CloudRain, Volume2,
  Settings, Search, Sparkles, Heart, Coffee
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

// 流式消息类型
interface StreamMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean
  intent?: string
  agent_used?: string
  created_at: string
}

// 获取时间问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 7) return { text: '早起的鸟儿有虫吃 🌅', emoji: '🌅' }
  if (hour >= 7 && hour < 12) return { text: '早上好！新的一天，新的开始', emoji: '☀️' }
  if (hour >= 12 && hour < 14) return { text: '中午好！记得吃午饭哦', emoji: '🍚' }
  if (hour >= 14 && hour < 18) return { text: '下午好！来杯咖啡提提神？', emoji: '☕' }
  if (hour >= 18 && hour < 22) return { text: '晚上好！辛苦一天了', emoji: '🌙' }
  return { text: '夜深了，注意休息', emoji: '😴' }
}

// 获取当前日期信息
const getDateInfo = () => {
  const now = new Date()
  const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()]
  return {
    date: format(now, 'M月d日', { locale: zhCN }),
    weekDay,
    time: format(now, 'HH:mm')
  }
}

// 快捷操作卡片
const QuickActionCard = ({ 
  icon: Icon, 
  label, 
  description,
  onClick,
  color = 'blue'
}: {
  icon: React.ElementType
  label: string
  description?: string
  onClick: () => void
  color?: string
}) => {
  const colorClasses = {
    blue: 'bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border-blue-500/20',
    green: 'bg-green-500/10 hover:bg-green-500/20 text-green-400 border-green-500/20',
    purple: 'bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border-purple-500/20',
    orange: 'bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 border-orange-500/20',
    pink: 'bg-pink-500/10 hover:bg-pink-500/20 text-pink-400 border-pink-500/20',
    cyan: 'bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border-cyan-500/20',
  }

  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}
    >
      <div className="p-2 rounded-lg bg-current/10">
        <Icon className="w-5 h-5" />
      </div>
      <div className="text-left">
        <p className="font-medium text-sm text-slate-200">{label}</p>
        {description && <p className="text-xs text-slate-500">{description}</p>}
      </div>
    </button>
  )
}

// 流式Markdown渲染组件 - 支持边流式传输边渲染
const StreamingMarkdown = ({ 
  content, 
  isStreaming = false 
}: { 
  content: string
  isStreaming?: boolean 
}) => {
  const [copied, setCopied] = useState<string | null>(null)

  const handleCopy = async (code: string, id: string) => {
    await navigator.clipboard.writeText(code)
    setCopied(id)
    setTimeout(() => setCopied(null), 2000)
  }

  // 智能分割内容：已完成的部分 vs 正在输入的部分
  const { completedContent, pendingContent } = useMemo(() => {
    if (!isStreaming || !content) {
      return { completedContent: content, pendingContent: '' }
    }

    // 查找最后一个完整的段落/块边界
    // 完整块的标志：双换行、代码块结束、列表项结束等
    const lines = content.split('\n')
    let lastCompleteIndex = -1
    let inCodeBlock = false
    let codeBlockLang = ''

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const trimmedLine = line.trim()
      
      // 检测代码块开始/结束
      if (trimmedLine.startsWith('```')) {
        if (!inCodeBlock) {
          inCodeBlock = true
          codeBlockLang = trimmedLine.slice(3)
        } else {
          inCodeBlock = false
          lastCompleteIndex = i
        }
        continue
      }

      // 如果在代码块内，继续
      if (inCodeBlock) continue

      // 空行表示段落结束
      if (trimmedLine === '' && i > 0) {
        lastCompleteIndex = i - 1
      }
      
      // 完整的列表项（下一行不是缩进的延续）
      if (/^[-*+]\s/.test(trimmedLine) || /^\d+\.\s/.test(trimmedLine)) {
        if (i < lines.length - 1) {
          const nextLine = lines[i + 1]
          if (nextLine.trim() === '' || /^[-*+]\s/.test(nextLine.trim()) || /^\d+\.\s/.test(nextLine.trim())) {
            lastCompleteIndex = i
          }
        }
      }

      // 标题行总是完整的
      if (/^#{1,6}\s/.test(trimmedLine)) {
        lastCompleteIndex = i
      }
    }

    // 如果在代码块中间，不分割
    if (inCodeBlock) {
      return { completedContent: '', pendingContent: content }
    }

    // 如果找到完整块边界
    if (lastCompleteIndex >= 0) {
      const completed = lines.slice(0, lastCompleteIndex + 1).join('\n')
      const pending = lines.slice(lastCompleteIndex + 1).join('\n')
      return { completedContent: completed, pendingContent: pending }
    }

    // 没有找到完整边界，全部作为pending
    return { completedContent: '', pendingContent: content }
  }, [content, isStreaming])

  // Markdown渲染配置
  const markdownComponents = useMemo(() => ({
    code({ className, children, ...props }: any) {
      const match = /language-(\w+)/.exec(className || '')
      const codeString = String(children).replace(/\n$/, '')
      const codeId = `code-${Math.random().toString(36).substr(2, 9)}`
      
      if (match) {
        return (
          <div className="relative group my-3">
            <div className="flex items-center justify-between bg-slate-900 px-4 py-2 rounded-t-lg border-b border-slate-700">
              <span className="text-xs text-slate-400">{match[1]}</span>
              <button
                onClick={() => handleCopy(codeString, codeId)}
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-white transition-colors"
              >
                {copied === codeId ? (
                  <><Check className="w-3 h-3" /> 已复制</>
                ) : (
                  <><Copy className="w-3 h-3" /> 复制</>
                )}
              </button>
            </div>
            <pre className="!mt-0 !rounded-t-none">
              <code className={className} {...props}>{children}</code>
            </pre>
          </div>
        )
      }
      return (
        <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm text-pink-400" {...props}>
          {children}
        </code>
      )
    },
    table({ children }: any) {
      return (
        <div className="overflow-x-auto my-3">
          <table className="min-w-full border-collapse border border-slate-600 rounded-lg">
            {children}
          </table>
        </div>
      )
    },
    th({ children }: any) {
      return <th className="bg-slate-700 px-4 py-2 text-left text-sm font-medium border border-slate-600">{children}</th>
    },
    td({ children }: any) {
      return <td className="px-4 py-2 text-sm border border-slate-600">{children}</td>
    },
    a({ href, children }: any) {
      return <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{children}</a>
    },
    ul({ children }: any) {
      return <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>
    },
    ol({ children }: any) {
      return <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>
    },
    blockquote({ children }: any) {
      return <blockquote className="border-l-4 border-blue-500 pl-4 my-3 text-slate-400 italic">{children}</blockquote>
    },
    // 段落：添加平滑过渡
    p({ children }: any) {
      return <p className="my-2 leading-relaxed transition-all duration-75">{children}</p>
    },
    // 标题
    h1({ children }: any) {
      return <h1 className="text-xl font-bold mt-4 mb-2">{children}</h1>
    },
    h2({ children }: any) {
      return <h2 className="text-lg font-bold mt-3 mb-2">{children}</h2>
    },
    h3({ children }: any) {
      return <h3 className="text-base font-semibold mt-2 mb-1">{children}</h3>
    },
  }), [copied, handleCopy])

  return (
    <div className="streaming-markdown">
      {/* 已完成的部分 - 完整渲染 */}
      {completedContent && (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={markdownComponents}
        >
          {completedContent}
        </ReactMarkdown>
      )}
      
      {/* 正在输入的部分 - 简化渲染或纯文本 */}
      {pendingContent && (
        <span className="text-slate-100 whitespace-pre-wrap">{pendingContent}</span>
      )}
      
      {/* 流式光标 */}
      {isStreaming && (
        <span className="inline-block w-2 h-4 bg-emerald-400 animate-pulse ml-0.5 rounded-sm" />
      )}
    </div>
  )
}

// 保留原有MarkdownContent作为非流式场景的备用
const MarkdownContent = ({ content }: { content: string }) => (
  <StreamingMarkdown content={content} isStreaming={false} />
)

// 消息气泡组件
const MessageBubble = ({ message }: { message: StreamMessage }) => {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${
        isUser ? 'bg-gradient-to-br from-blue-500 to-purple-600' : 'bg-gradient-to-br from-emerald-500 to-teal-600'
      }`}>
        {isUser ? <User className="w-5 h-5 text-white" /> : <Sparkles className="w-5 h-5 text-white" />}
      </div>
      
      {/* 消息内容 */}
      <div className={`max-w-[75%] ${isUser ? 'text-right' : 'text-left'}`}>
        <div className={`inline-block px-4 py-3 rounded-2xl ${
          isUser 
            ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white' 
            : 'bg-slate-800 text-slate-100 border border-slate-700'
        }`}>
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
          ) : (
            <div className="prose prose-sm prose-invert max-w-none text-sm">
              {message.isStreaming && !message.content ? (
                <div className="flex items-center gap-2 text-slate-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>思考中...</span>
                </div>
              ) : (
                <StreamingMarkdown 
                  content={message.content} 
                  isStreaming={message.isStreaming} 
                />
              )}
            </div>
          )}
        </div>
        {/* 时间和元信息 */}
        <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
          <span>{format(new Date(message.created_at), 'HH:mm')}</span>
          {message.agent_used && !isUser && (
            <span className="px-1.5 py-0.5 bg-slate-800 rounded text-slate-400">
              {message.agent_used}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

// 欢迎界面
const WelcomeScreen = ({ onQuickAction }: { onQuickAction: (text: string) => void }) => {
  const greeting = getGreeting()
  const dateInfo = getDateInfo()
  
  const quickActions = [
    { icon: Calendar, label: '今日日程', action: '查看今天的日程安排', color: 'blue' },
    { icon: Bell, label: '设置提醒', action: '帮我设置一个提醒', color: 'orange' },
    { icon: Cloud, label: '天气查询', action: '今天天气怎么样', color: 'cyan' },
    { icon: Mail, label: '写邮件', action: '帮我写一封邮件', color: 'purple' },
    { icon: Newspaper, label: '看新闻', action: '今天有什么重要新闻', color: 'green' },
    { icon: Code, label: '写代码', action: '帮我写段Python代码', color: 'pink' },
  ]

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      {/* Logo和问候 */}
      <div className="text-center mb-8">
        <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
          <Sparkles className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-2">
          {greeting.emoji} {greeting.text}
        </h1>
        <p className="text-slate-400">
          今天是 {dateInfo.date} {dateInfo.weekDay}，我是Jarvis，有什么可以帮你的吗？
        </p>
      </div>

      {/* 快捷操作 */}
      <div className="w-full max-w-2xl">
        <p className="text-sm text-slate-500 mb-3 px-1">💡 快捷操作</p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {quickActions.map((action, i) => (
            <QuickActionCard
              key={i}
              icon={action.icon}
              label={action.label}
              onClick={() => onQuickAction(action.action)}
              color={action.color}
            />
          ))}
        </div>
      </div>

      {/* 提示 */}
      <div className="mt-8 text-center text-sm text-slate-500">
        <p>💬 试试输入 &quot;帮我安排明天的日程&quot; 或 &quot;翻译成英文&quot;</p>
      </div>
    </div>
  )
}

export default function ChatV2() {
  const queryClient = useQueryClient()
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [inputValue, setInputValue] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [localMessages, setLocalMessages] = useState<StreamMessage[]>([])
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // 获取会话列表
  const { data: sessions = [] } = useQuery({
    queryKey: ['chat-sessions'],
    queryFn: async () => (await chatAPI.getSessions()).data,
  })

  // 获取当前会话的消息
  const { data: serverMessages = [] } = useQuery({
    queryKey: ['chat-messages', currentSessionId],
    queryFn: async () => {
      if (!currentSessionId) return []
      return (await chatAPI.getMessages(currentSessionId)).data
    },
    enabled: !!currentSessionId,
  })

  // 合并服务器消息和本地消息
  const messages = currentSessionId 
    ? [...serverMessages.map((m: ChatMessage) => ({ ...m, isStreaming: false })), ...localMessages]
    : localMessages

  // 删除会话
  const deleteSession = useMutation({
    mutationFn: (sessionId: string) => chatAPI.deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      if (currentSessionId) {
        setCurrentSessionId(null)
        setLocalMessages([])
      }
    },
  })

  // 滚动到底部
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // 流式发送消息
  const handleSend = async (text?: string) => {
    const messageToSend = text || inputValue.trim()
    if (!messageToSend || isStreaming) return
    
    setInputValue('')
    setIsStreaming(true)
    
    const userMsgId = `local-user-${Date.now()}`
    const assistantMsgId = `local-assistant-${Date.now()}`
    
    // 添加用户消息
    setLocalMessages(prev => [...prev, {
      id: userMsgId,
      role: 'user',
      content: messageToSend,
      created_at: new Date().toISOString()
    }])

    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('http://localhost:8000/api/chat/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend,
          session_id: currentSessionId,
          user_id: 'default_user'
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) throw new Error('请求失败')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''
      let newSessionId = currentSessionId

      // 添加助手消息占位
      setLocalMessages(prev => [...prev, {
        id: assistantMsgId,
        role: 'assistant',
        content: '',
        isStreaming: true,
        created_at: new Date().toISOString()
      }])

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              switch (data.type) {
                case 'session':
                  if (data.session_id) {
                    newSessionId = data.session_id
                    setCurrentSessionId(data.session_id)
                  }
                  break
                  
                case 'content':
                  fullContent += data.content
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId ? { ...m, content: fullContent } : m
                  ))
                  break
                  
                case 'complete':
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId ? { 
                      ...m, 
                      content: fullContent,
                      isStreaming: false,
                      intent: data.intent,
                      agent_used: data.agent_used
                    } : m
                  ))
                  break
                  
                case 'error':
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId ? { ...m, content: `❌ ${data.content}`, isStreaming: false } : m
                  ))
                  break
              }
            } catch { /* ignore */ }
          }
        }
      }

      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      if (newSessionId) {
        queryClient.invalidateQueries({ queryKey: ['chat-messages', newSessionId] })
      }

    } catch (error: unknown) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setLocalMessages(prev => prev.map(m => 
          m.id === assistantMsgId ? { ...m, content: '😅 抱歉，出了点问题，请重试', isStreaming: false } : m
        ))
      }
    } finally {
      setIsStreaming(false)
      setTimeout(() => {
        setLocalMessages([])
        queryClient.invalidateQueries({ queryKey: ['chat-messages', currentSessionId] })
      }, 500)
    }
  }

  // 语音识别（使用Web Speech API）
  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('您的浏览器不支持语音识别')
      return
    }

    if (isListening) {
      setIsListening(false)
      return
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => setIsListening(true)
    recognition.onend = () => setIsListening(false)
    recognition.onerror = () => setIsListening(false)
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript
      setInputValue(transcript)
    }

    recognition.start()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    setCurrentSessionId(null)
    setInputValue('')
    setLocalMessages([])
  }

  const handleStop = () => {
    abortControllerRef.current?.abort()
    setIsStreaming(false)
  }

  return (
    <Layout>
      <div className="flex h-[calc(100vh-64px)]">
        {/* 侧边栏 */}
        <div className="w-72 bg-slate-900/50 backdrop-blur-xl border-r border-slate-700/50 flex flex-col">
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl transition-all shadow-lg shadow-emerald-900/20"
            >
              <Plus className="w-5 h-5" />
              新对话
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-2">
            <p className="px-3 py-2 text-xs text-slate-500 font-medium">历史对话</p>
            {sessions.length === 0 ? (
              <div className="px-3 py-8 text-center">
                <MessageSquare className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-sm text-slate-500">暂无对话记录</p>
              </div>
            ) : (
              sessions.map((session: ChatSession) => (
                <div
                  key={session.id}
                  className={`group flex items-center gap-2 px-3 py-3 rounded-xl cursor-pointer transition-all mb-1 ${
                    currentSessionId === session.id
                      ? 'bg-slate-700/50 text-white'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  }`}
                  onClick={() => {
                    setCurrentSessionId(session.id)
                    setLocalMessages([])
                  }}
                >
                  <MessageSquare className="w-4 h-4 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{session.title || '新对话'}</p>
                    <p className="text-xs text-slate-500 truncate">
                      {formatDistanceToNow(new Date(session.last_activity), {
                        addSuffix: true,
                        locale: zhCN
                      })}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      if (confirm('确定删除此对话？')) {
                        deleteSession.mutate(session.id)
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 rounded-lg transition-all"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 主聊天区域 */}
        <div className="flex-1 flex flex-col bg-gradient-to-b from-slate-900 to-slate-950">
          {/* 消息区域 */}
          {messages.length === 0 && !currentSessionId ? (
            <WelcomeScreen onQuickAction={(text) => handleSend(text)} />
          ) : (
            <div className="flex-1 overflow-y-auto p-6">
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message as StreamMessage} />
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}

          {/* 输入区域 */}
          <div className="border-t border-slate-800 bg-slate-900/80 backdrop-blur-xl p-4">
            <div className="max-w-4xl mx-auto">
              <div className="relative flex items-end gap-3">
                {/* 语音按钮 */}
                <button
                  onClick={toggleVoice}
                  className={`p-3 rounded-xl transition-all ${
                    isListening 
                      ? 'bg-red-500 text-white animate-pulse' 
                      : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'
                  }`}
                >
                  {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>

                {/* 输入框 */}
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={isListening ? '正在聆听...' : '有什么我能帮你的？'}
                    className="w-full px-4 py-3 pr-12 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
                    rows={1}
                    style={{ minHeight: '48px', maxHeight: '200px' }}
                  />
                </div>

                {/* 发送/停止按钮 */}
                {isStreaming ? (
                  <button
                    onClick={handleStop}
                    className="p-3 bg-red-600 hover:bg-red-500 text-white rounded-xl transition-all"
                  >
                    <div className="w-5 h-5 flex items-center justify-center">
                      <div className="w-3 h-3 bg-white rounded-sm" />
                    </div>
                  </button>
                ) : (
                  <button
                    onClick={() => handleSend()}
                    disabled={!inputValue.trim()}
                    className="p-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-xl transition-all shadow-lg shadow-emerald-900/20"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                )}
              </div>

              {/* 快捷提示 */}
              <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                <span>按 Enter 发送，Shift+Enter 换行</span>
                <span>•</span>
                <span>试试说 &quot;帮我...&quot; 或 &quot;查询...&quot;</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
