import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatAPI, ChatMessage as APIChatMessage, ChatSession } from '../api/client'
import { MainLayout } from '../components/layout'
import { Button, Input, Loading, Badge, Card } from '../components/ui'
import MessageBubble from '../components/MessageBubble'
import VoiceInput from '../components/VoiceInput'
import AgentCard from '../components/AgentCard'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import {
  Plus,
  MessageSquare,
  Trash2,
  Bot,
  Sparkles,
  Calendar,
  Mail,
  Cloud,
  Code,
  FileText,
  Newspaper,
} from 'lucide-react'
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

// 快捷操作配置
const quickActions = [
  { icon: Calendar, label: '查看日程', prompt: '今天有什么安排？', color: 'blue' },
  { icon: Mail, label: '写邮件', prompt: '帮我写一封邮件', color: 'green' },
  { icon: Cloud, label: '查天气', prompt: '今天天气怎么样？', color: 'cyan' },
  { icon: Code, label: '写代码', prompt: '帮我写一段代码', color: 'purple' },
  { icon: FileText, label: '总结文本', prompt: '帮我总结这段内容', color: 'orange' },
  { icon: Newspaper, label: '看新闻', prompt: '今天有什么新闻？', color: 'pink' },
]

// Agent卡片数据（示例）
const featuredAgents = [
  {
    id: '1',
    name: 'ScheduleAgent',
    description: '智能日程管理，帮你安排时间',
    category: '办公效率',
    status: 'idle' as const,
    lastActive: '2分钟前',
  },
  {
    id: '2',
    name: 'CodeAgent',
    description: '代码生成与优化助手',
    category: '技术开发',
    status: 'idle' as const,
    lastActive: '10分钟前',
  },
  {
    id: '3',
    name: 'WeatherAgent',
    description: '天气查询与预报',
    category: '生活服务',
    status: 'idle' as const,
    lastActive: '1小时前',
  },
]

export default function ChatV3() {
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // 状态
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [inputValue, setInputValue] = useState('')
  const [localMessages, setLocalMessages] = useState<StreamMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [showVoiceInput, setShowVoiceInput] = useState(false)
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])

  // 获取会话列表
  const { data: sessions = [] } = useQuery({
    queryKey: ['sessions'],
    queryFn: async () => (await chatAPI.getSessions()).data,
  })

  // 获取当前会话的消息
  const { data: messages = [], isLoading: messagesLoading } = useQuery({
    queryKey: ['messages', currentSessionId],
    queryFn: async () => {
      if (!currentSessionId) return []
      return (await chatAPI.getMessages(currentSessionId)).data
    },
    enabled: !!currentSessionId,
  })

  // 创建新会话
  const createSessionMutation = useMutation({
    mutationFn: () => chatAPI.createSession(),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      setCurrentSessionId(response.data.id)
      setLocalMessages([])
    },
  })

  // 删除会话
  const deleteSessionMutation = useMutation({
    mutationFn: (sessionId: string) => chatAPI.deleteSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      if (currentSessionId && sessions.length > 1) {
        const currentIndex = sessions.findIndex((s: ChatSession) => s.id === currentSessionId)
        const nextSession = sessions[currentIndex + 1] || sessions[currentIndex - 1]
        if (nextSession && nextSession.id !== currentSessionId) {
          setCurrentSessionId(nextSession.id)
        } else {
          setCurrentSessionId(null)
        }
      } else {
        setCurrentSessionId(null)
      }
      setLocalMessages([])
    },
  })

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, localMessages])

  // 初始化：自动创建或选择会话
  useEffect(() => {
    if (!currentSessionId && sessions.length > 0) {
      setCurrentSessionId(sessions[0].id)
    } else if (!currentSessionId && sessions.length === 0 && !createSessionMutation.isPending) {
      createSessionMutation.mutate()
    }
  }, [sessions, currentSessionId, createSessionMutation])

  // 发送消息
  const handleSend = async (message?: string) => {
    const content = message || inputValue.trim()
    if (!content || !currentSessionId) return

    setInputValue('')
    const userMessage: StreamMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    setLocalMessages((prev) => [...prev, userMessage])

    try {
      abortControllerRef.current = new AbortController()
      setIsStreaming(true)

      const assistantMessageId = `temp-assistant-${Date.now()}`
      const assistantMessage: StreamMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        isStreaming: true,
        created_at: new Date().toISOString(),
      }

      setLocalMessages((prev) => [...prev, assistantMessage])

      const response = await fetch(`http://localhost:8000/api/chat/${currentSessionId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content,
          selected_agents: selectedAgents.length > 0 ? selectedAgents : undefined
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) throw new Error('发送失败')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const text = decoder.decode(value, { stream: true })
          const lines = text.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))

                if (data.type === 'agent_thinking') {
                  setActiveAgent(data.agent)
                  setLocalMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, agent_used: data.agent }
                        : msg
                    )
                  )
                } else if (data.type === 'content') {
                  setLocalMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: msg.content + data.content }
                        : msg
                    )
                  )
                } else if (data.type === 'done') {
                  setLocalMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, isStreaming: false }
                        : msg
                    )
                  )
                  setActiveAgent(null)
                }
              } catch (e) {
                console.error('解析SSE数据失败:', e)
              }
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('发送消息失败:', error)
        setLocalMessages((prev) =>
          prev.map((msg) =>
            msg.isStreaming
              ? { ...msg, content: '发送失败，请重试', isStreaming: false }
              : msg
          )
        )
      }
    } finally {
      setIsStreaming(false)
      setActiveAgent(null)
      queryClient.invalidateQueries({ queryKey: ['messages', currentSessionId] })
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    }
  }

  // 快捷操作 - 只填充输入框，不自动发送
  const handleQuickAction = (prompt: string) => {
    setInputValue(prompt)
    // 不自动发送，由用户决定是否发送
  }

  // Agent选择/取消选择
  const handleAgentSelect = (agentId: string) => {
    setSelectedAgents((prev) => {
      if (prev.includes(agentId)) {
        // 再次点击取消选择
        return prev.filter((id) => id !== agentId)
      } else {
        // 添加到选择列表
        return [...prev, agentId]
      }
    })
  }

  // 新建对话
  const handleNewChat = () => {
    createSessionMutation.mutate()
  }

  // 合并显示的消息
  const allMessages = [...messages, ...localMessages]

  return (
    <MainLayout
      title="智能对话"
      subtitle={currentSessionId ? `会话 ${currentSessionId.slice(0, 8)}...` : ''}
      showVoice
      onVoiceClick={() => setShowVoiceInput(!showVoiceInput)}
    >
      <div className="flex h-full">
        {/* 左侧：对话历史 */}
        <div className="w-80 border-r border-slate-800 flex flex-col bg-slate-900/30">
          <div className="p-4">
            <Button
              variant="primary"
              className="w-full"
              onClick={handleNewChat}
              leftIcon={<Plus className="w-5 h-5" />}
              isLoading={createSessionMutation.isPending}
            >
              新对话
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto px-3 pb-4">
            <p className="px-3 py-2 text-xs text-slate-500 font-medium uppercase">
              对话历史
            </p>
            {sessions.length === 0 ? (
              <div className="px-3 py-12 text-center">
                <MessageSquare className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                <p className="text-sm text-slate-500">暂无对话记录</p>
              </div>
            ) : (
              <div className="space-y-1">
                {sessions.map((session: ChatSession) => (
                  <div
                    key={session.id}
                    className={`
                      group relative flex items-center gap-3 px-3 py-3 rounded-xl
                      cursor-pointer transition-all
                      ${
                        currentSessionId === session.id
                          ? 'bg-emerald-500/10 border border-emerald-500/20 text-white'
                          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                      }
                    `}
                    onClick={() => {
                      setCurrentSessionId(session.id)
                      setLocalMessages([])
                    }}
                  >
                    <MessageSquare className="w-4 h-4 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {session.title || '新对话'}
                      </p>
                      <p className="text-xs text-slate-500">
                        {formatDistanceToNow(new Date(session.last_activity), {
                          addSuffix: true,
                          locale: zhCN,
                        })}
                      </p>
                    </div>

                    {/* 删除按钮 */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSessionMutation.mutate(session.id)
                      }}
                      className="
                        opacity-0 group-hover:opacity-100
                        p-1.5 rounded-lg
                        hover:bg-red-500/20 text-slate-500 hover:text-red-400
                        transition-all
                      "
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 中间：消息区域 */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* 消息列表 */}
          <div className="flex-1 overflow-y-auto px-6 py-6">
            {messagesLoading ? (
              <div className="flex items-center justify-center h-full">
                <Loading size="lg" text="加载中..." />
              </div>
            ) : allMessages.length === 0 ? (
              <div className="max-w-4xl mx-auto">
                {/* 欢迎界面 */}
                <div className="text-center mb-12 py-12">
                  <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                    <Bot className="w-12 h-12 text-white" />
                  </div>
                  <h1 className="text-4xl font-bold text-white mb-3">
                    你好，我是 <span className="text-gradient">Jarvis</span>
                  </h1>
                  <p className="text-lg text-slate-400">
                    你的第二大脑、智能助手和成长伙伴
                  </p>
                </div>

                {/* 快捷操作 */}
                <div className="mb-12">
                  <h2 className="text-sm font-medium text-slate-400 mb-4 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    快速开始
                  </h2>
                  <div className="grid grid-cols-2 gap-3">
                    {quickActions.map((action, index) => {
                      const Icon = action.icon
                      return (
                        <Card
                          key={index}
                          variant="glass"
                          hoverable
                          className="cursor-pointer"
                          onClick={() => handleQuickAction(action.prompt)}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`p-3 rounded-xl bg-${action.color}-500/10 border border-${action.color}-500/20`}>
                              <Icon className={`w-5 h-5 text-${action.color}-400`} />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium text-white text-sm">
                                {action.label}
                              </p>
                              <p className="text-xs text-slate-500">
                                {action.prompt}
                              </p>
                            </div>
                          </div>
                        </Card>
                      )
                    })}
                  </div>
                </div>

                {/* 推荐Agent */}
                <div>
                  <h2 className="text-sm font-medium text-slate-400 mb-4">
                    推荐Agent {selectedAgents.length > 0 && `(已选 ${selectedAgents.length})`}
                  </h2>
                  <div className="grid gap-3">
                    {featuredAgents.map((agent) => {
                      const isSelected = selectedAgents.includes(agent.id)
                      return (
                        <div
                          key={agent.id}
                          className={`relative transition-all ${
                            isSelected
                              ? 'ring-2 ring-emerald-500 rounded-xl'
                              : ''
                          }`}
                        >
                          <AgentCard
                            {...agent}
                            onClick={() => handleAgentSelect(agent.id)}
                          />
                          {isSelected && (
                            <div className="absolute top-2 right-2">
                              <div className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                已选
                              </div>
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto space-y-6">
                {allMessages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    role={msg.role}
                    content={
                      msg.role === 'assistant' ? (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeHighlight]}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        msg.content
                      )
                    }
                    name={msg.role === 'user' ? '我' : 'Jarvis'}
                    timestamp={formatDistanceToNow(new Date(msg.created_at), {
                      addSuffix: true,
                      locale: zhCN,
                    })}
                    isStreaming={msg.isStreaming}
                    agentName={msg.agent_used}
                    onCopy={() => navigator.clipboard.writeText(msg.content)}
                  />
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* 输入区域 */}
          <div className="border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl p-6">
            <div className="max-w-4xl mx-auto">
              {showVoiceInput ? (
                <VoiceInput
                  onSend={handleSend}
                  placeholder="说点什么..."
                  disabled={isStreaming || !currentSessionId}
                />
              ) : (
                <div className="flex items-end gap-3">
                  <div className="flex-1">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          handleSend()
                        }
                      }}
                      placeholder="输入消息... (Shift+Enter 换行)"
                      disabled={isStreaming || !currentSessionId}
                    />
                  </div>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => handleSend()}
                    isLoading={isStreaming}
                    disabled={!inputValue.trim() || !currentSessionId}
                  >
                    发送
                  </Button>
                </div>
              )}

              {/* 状态提示 */}
              {activeAgent && (
                <div className="mt-3 flex items-center gap-2 text-sm text-slate-400">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                  <span>{activeAgent} 正在思考...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
