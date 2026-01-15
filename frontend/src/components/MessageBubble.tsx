import { ReactNode } from 'react'
import { Avatar, Badge, Loading } from './ui'
import { Copy, ThumbsUp, ThumbsDown, RefreshCw } from 'lucide-react'

export interface MessageBubbleProps {
  role: 'user' | 'assistant' | 'system'
  content: ReactNode
  avatar?: string
  name?: string
  timestamp?: string
  isStreaming?: boolean
  agentName?: string
  onCopy?: () => void
  onLike?: () => void
  onDislike?: () => void
  onRetry?: () => void
}

const MessageBubble = ({
  role,
  content,
  avatar,
  name,
  timestamp,
  isStreaming = false,
  agentName,
  onCopy,
  onLike,
  onDislike,
  onRetry,
}: MessageBubbleProps) => {
  const isUser = role === 'user'
  const isSystem = role === 'system'

  // 系统消息样式
  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700">
          <p className="text-sm text-slate-400">{content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} group`}>
      {/* Avatar */}
      <Avatar
        src={avatar}
        name={name || (isUser ? 'User' : 'Jarvis')}
        size="md"
        status={isStreaming ? 'busy' : 'online'}
      />

      {/* 消息内容 */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
        {/* 名称和时间 */}
        <div className={`flex items-center gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <span className="text-sm font-medium text-slate-300">
            {name || (isUser ? '我' : 'Jarvis')}
          </span>
          {agentName && !isUser && (
            <Badge variant="purple" size="sm">
              {agentName}
            </Badge>
          )}
          {timestamp && (
            <span className="text-xs text-slate-500">{timestamp}</span>
          )}
        </div>

        {/* 消息气泡 */}
        <div
          className={`
            px-4 py-3 rounded-2xl
            ${isUser
              ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white rounded-tr-sm'
              : 'bg-slate-800 border border-slate-700 text-slate-100 rounded-tl-sm'
            }
            ${isStreaming ? 'animate-pulse' : ''}
          `}
        >
          <div className="prose prose-invert prose-sm max-w-none">
            {content}
          </div>

          {/* 流式加载指示器 */}
          {isStreaming && (
            <div className="mt-2 flex items-center gap-2">
              <Loading size="sm" variant="dots" />
            </div>
          )}
        </div>

        {/* 操作按钮 - 只在助手消息显示 */}
        {!isUser && !isStreaming && (
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            {onCopy && (
              <button
                onClick={onCopy}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
                title="复制"
              >
                <Copy className="w-4 h-4" />
              </button>
            )}
            {onLike && (
              <button
                onClick={onLike}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-emerald-400 transition-all"
                title="点赞"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
            )}
            {onDislike && (
              <button
                onClick={onDislike}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-red-400 transition-all"
                title="踩"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            )}
            {onRetry && (
              <button
                onClick={onRetry}
                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-blue-400 transition-all"
                title="重新生成"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageBubble
