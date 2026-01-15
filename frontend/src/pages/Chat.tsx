import { useState, useRef, useEffect, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatAPI, ChatMessage, ChatSession } from '../api/client'
import Layout from '../components/Layout'
import { 
  Send, Plus, MessageSquare, Trash2, Clock, Bot, User, 
  Sparkles, Zap, Calendar, Bell, Mail, Cloud, Code, FileText,
  Loader2, Copy, Check
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
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

export default function Chat() {
  const queryClient = useQueryClient()
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [inputValue, setInputValue] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [localMessages, setLocalMessages] = useState<StreamMessage[]>([])
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
  }, [messages, streamingContent, scrollToBottom])

  // 流式发送消息
  const handleSendStream = async () => {
    if (!inputValue.trim() || isStreaming) return
    
    const userMessage = inputValue.trim()
    setInputValue('')
    setIsStreaming(true)
    setStreamingContent('')
    
    // 添加用户消息到本地
    const userMsgId = `local-user-${Date.now()}`
    const assistantMsgId = `local-assistant-${Date.now()}`
    
    setLocalMessages(prev => [
      ...prev,
      {
        id: userMsgId,
        role: 'user',
        content: userMessage,
        created_at: new Date().toISOString()
      }
    ])

    // 创建AbortController用于取消请求
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('http://localhost:8000/api/chat/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: currentSessionId,
          user_id: 'default_user'
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) throw new Error('Stream request failed')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''
      let newSessionId = currentSessionId

      // 添加助手消息占位
      setLocalMessages(prev => [
        ...prev,
        {
          id: assistantMsgId,
          role: 'assistant',
          content: '',
          isStreaming: true,
          created_at: new Date().toISOString()
        }
      ])

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
                  setStreamingContent(fullContent)
                  // 更新本地消息内容
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId 
                      ? { ...m, content: fullContent }
                      : m
                  ))
                  break
                  
                case 'complete':
                  // 更新消息的完整信息
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId 
                      ? { 
                          ...m, 
                          content: fullContent,
                          isStreaming: false,
                          intent: data.intent,
                          agent_used: data.agent_used
                        }
                      : m
                  ))
                  break
                  
                case 'error':
                  console.error('Stream error:', data.content)
                  setLocalMessages(prev => prev.map(m => 
                    m.id === assistantMsgId 
                      ? { ...m, content: `错误: ${data.content}`, isStreaming: false }
                      : m
                  ))
                  break
              }
            } catch {
              // 忽略JSON解析错误
            }
          }
        }
      }

      // 刷新会话列表
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] })
      if (newSessionId) {
        queryClient.invalidateQueries({ queryKey: ['chat-messages', newSessionId] })
      }

    } catch (error: unknown) {
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Stream error:', error)
        setLocalMessages(prev => prev.map(m => 
          m.id === assistantMsgId 
            ? { ...m, content: '抱歉，发生了错误，请重试。', isStreaming: false }
            : m
        ))
      }
    } finally {
      setIsStreaming(false)
      setStreamingContent('')
      // 清除本地消息，依赖服务器数据
      setTimeout(() => {
        setLocalMessages([])
        queryClient.invalidateQueries({ queryKey: ['chat-messages', currentSessionId] })
      }, 500)
    }
  }

  // 处理按键
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendStream()
    }
  }

  // 新建对话
  const handleNewChat = () => {
    setCurrentSessionId(null)
    setInputValue('')
    setLocalMessages([])
  }

  // 停止生成
  const handleStop = () => {
    abortControllerRef.current?.abort()
    setIsStreaming(false)
  }

  // 快捷操作
  const quickActions = [
    { icon: Calendar, label: '查看日程', action: '查看今天的日程安排' },
    { icon: Bell, label: '设置提醒', action: '帮我设置一个提醒' },
    { icon: Mail, label: '写邮件', action: '帮我写一封邮件' },
    { icon: Cloud, label: '查天气', action: '今天北京天气怎么样' },
    { icon: Code, label: '写代码', action: '用Python写一个快速排序算法' },
    { icon: FileText, label: '做总结', action: '帮我总结一下' },
  ]

  return (
    <Layout>
      <div className="flex h-[calc(100vh-64px)]">
        {/* 侧边栏 - 会话列表 */}
        <div className="w-72 bg-slate-900 border-r border-slate-700 flex flex-col">
          {/* 新建对话按钮 */}
          <div className="p-4">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5" />
              新对话
            </button>
          </div>

          {/* 会话列表 */}
          <div className="flex-1 overflow-y-auto">
            <div className="px-2 pb-2">
              <p className="px-3 py-2 text-xs text-slate-500 uppercase tracking-wider">历史对话</p>
              {sessions.length === 0 ? (
                <p className="px-3 py-4 text-sm text-slate-500 text-center">暂无对话</p>
              ) : (
                sessions.map((session: ChatSession) => (
                  <div
                    key={session.id}
                    className={`group flex items-center gap-2 px-3 py-3 rounded-lg cursor-pointer transition-colors ${
                      currentSessionId === session.id
                        ? 'bg-slate-700 text-white'
                        : 'text-slate-300 hover:bg-slate-800'
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
                          locale: zhCN,
                        })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSession.mutate(session.id)
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600 rounded transition-all"
                    >
                      <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-400" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* 主聊天区域 */}
        <div className="flex-1 flex flex-col bg-slate-850">
          {/* 消息区域 */}
          <div className="flex-1 overflow-y-auto">
            {messages.length === 0 && !currentSessionId ? (
              // 欢迎界面
              <div className="h-full flex flex-col items-center justify-center p-8">
                <div className="text-center max-w-2xl">
                  <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <h1 className="text-3xl font-bold text-white mb-3">你好，我是 Jarvis</h1>
                  <p className="text-slate-400 mb-8">
                    你的智能私人助手。我可以帮你管理日程、设置提醒、回答问题、写代码等等。
                    试着用自然语言告诉我你需要什么吧！
                  </p>
                  
                  {/* 快捷操作 */}
                  <div className="grid grid-cols-3 gap-3 mb-8">
                    {quickActions.map((item, index) => (
                      <button
                        key={index}
                        onClick={() => setInputValue(item.action)}
                        className="flex flex-col items-center gap-2 p-4 bg-slate-800 hover:bg-slate-700 rounded-xl transition-colors border border-slate-700 hover:border-slate-600"
                      >
                        <item.icon className="w-6 h-6 text-primary-400" />
                        <span className="text-sm text-slate-300">{item.label}</span>
                      </button>
                    ))}
                  </div>
                  
                  <p className="text-sm text-slate-500">
                    💡 提示：Jarvis会记住你的偏好和重要信息，越用越懂你！
                  </p>
                </div>
              </div>
            ) : (
              // 消息列表
              <div className="p-4 space-y-4">
                {messages.map((msg: StreamMessage) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* 输入区域 */}
          <div className="p-4 border-t border-slate-700">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-end gap-3 bg-slate-800 rounded-2xl p-2">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="输入消息..."
                  rows={1}
                  disabled={isStreaming}
                  className="flex-1 bg-transparent text-white placeholder-slate-400 resize-none outline-none px-3 py-2 max-h-32 disabled:opacity-50"
                  style={{ minHeight: '44px' }}
                />
                {isStreaming ? (
                  <button
                    onClick={handleStop}
                    className="p-3 rounded-xl bg-red-600 hover:bg-red-700 text-white transition-colors"
                  >
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </button>
                ) : (
                  <button
                    onClick={handleSendStream}
                    disabled={!inputValue.trim()}
                    className={`p-3 rounded-xl transition-colors ${
                      inputValue.trim()
                        ? 'bg-primary-600 hover:bg-primary-700 text-white'
                        : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    }`}
                  >
                    <Send className="w-5 h-5" />
                  </button>
                )}
              </div>
              <p className="text-xs text-slate-500 text-center mt-2">
                按 Enter 发送，Shift + Enter 换行
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

// Markdown渲染组件
function MarkdownContent({ content }: { content: string }) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const handleCopy = async (code: string, index: number) => {
    await navigator.clipboard.writeText(code)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  let codeBlockIndex = 0

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        // 代码块
        code({ className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !match
          
          if (isInline) {
            return (
              <code className="bg-slate-600 px-1.5 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            )
          }

          const currentIndex = codeBlockIndex++
          const codeString = String(children).replace(/\n$/, '')

          return (
            <div className="relative group my-3">
              <div className="flex items-center justify-between bg-slate-600 px-4 py-2 rounded-t-lg">
                <span className="text-xs text-slate-300">{match[1]}</span>
                <button
                  onClick={() => handleCopy(codeString, currentIndex)}
                  className="text-slate-300 hover:text-white transition-colors"
                >
                  {copiedIndex === currentIndex ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
              <pre className="!mt-0 !rounded-t-none">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            </div>
          )
        },
        // 段落
        p({ children }) {
          return <p className="mb-2 last:mb-0">{children}</p>
        },
        // 列表
        ul({ children }) {
          return <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
        },
        ol({ children }) {
          return <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
        },
        // 链接
        a({ href, children }) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary-400 hover:underline">
              {children}
            </a>
          )
        },
        // 表格
        table({ children }) {
          return (
            <div className="overflow-x-auto my-3">
              <table className="min-w-full border-collapse border border-slate-600">
                {children}
              </table>
            </div>
          )
        },
        th({ children }) {
          return <th className="border border-slate-600 bg-slate-700 px-3 py-2 text-left">{children}</th>
        },
        td({ children }) {
          return <td className="border border-slate-600 px-3 py-2">{children}</td>
        },
        // 引用
        blockquote({ children }) {
          return (
            <blockquote className="border-l-4 border-primary-500 pl-4 my-2 text-slate-300 italic">
              {children}
            </blockquote>
          )
        },
        // 标题
        h1({ children }) {
          return <h1 className="text-xl font-bold mb-2">{children}</h1>
        },
        h2({ children }) {
          return <h2 className="text-lg font-bold mb-2">{children}</h2>
        },
        h3({ children }) {
          return <h3 className="text-base font-bold mb-2">{children}</h3>
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

// 消息气泡组件
function MessageBubble({ message }: { message: StreamMessage }) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isUser 
          ? 'bg-slate-600' 
          : 'bg-gradient-to-br from-primary-500 to-purple-600'
      }`}>
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : message.isStreaming ? (
          <Loader2 className="w-5 h-5 text-white animate-spin" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </div>
      
      {/* 消息内容 */}
      <div className={`max-w-[70%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser 
            ? 'bg-primary-600 text-white rounded-tr-none' 
            : 'bg-slate-700 text-white rounded-tl-none'
        }`}>
          {isUser ? (
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <MarkdownContent content={message.content || (message.isStreaming ? '思考中...' : '')} />
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 bg-white/50 animate-pulse ml-0.5" />
              )}
            </div>
          )}
        </div>
        
        {/* 元信息 */}
        {!message.isStreaming && (
          <div className={`flex items-center gap-2 mt-1 text-xs text-slate-500 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}>
            {message.agent_used && (
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3" />
                {message.agent_used}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {formatDistanceToNow(new Date(message.created_at), {
                addSuffix: true,
                locale: zhCN,
              })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
