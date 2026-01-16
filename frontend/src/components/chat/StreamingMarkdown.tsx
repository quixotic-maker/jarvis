import { useState, useEffect, useRef, memo } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'

interface StreamingMarkdownProps {
  content: string
  isStreaming?: boolean
  className?: string
}

/**
 * 流式Markdown渲染组件
 * 
 * 特点：
 * 1. 流式输出时使用防抖渲染，减少重新解析次数
 * 2. 流式完成后立即渲染最终版本
 * 3. 使用memo优化性能
 */
const StreamingMarkdown = memo(({ content, isStreaming = false, className = '' }: StreamingMarkdownProps) => {
  const [renderedContent, setRenderedContent] = useState(content)
  const timeoutRef = useRef<NodeJS.Timeout>()
  const lastContentRef = useRef(content)

  useEffect(() => {
    if (isStreaming) {
      // 流式输出中：使用防抖，每100ms更新一次渲染
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }

      timeoutRef.current = setTimeout(() => {
        setRenderedContent(content)
        lastContentRef.current = content
      }, 100)
    } else {
      // 流式完成：立即渲染最终版本
      if (lastContentRef.current !== content) {
        setRenderedContent(content)
        lastContentRef.current = content
      }
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [content, isStreaming])

  return (
    <div className={`markdown-body ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // 自定义代码块渲染
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''

            if (!inline && language) {
              return (
                <div className="relative group">
                  {/* 语言标签 */}
                  <div className="absolute top-2 right-2 px-2 py-1 text-xs bg-slate-700 text-slate-300 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    {language}
                  </div>
                  
                  {/* 代码块 */}
                  <pre className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                </div>
              )
            }

            // 内联代码
            return (
              <code className="px-1.5 py-0.5 bg-slate-800 text-emerald-400 rounded text-sm" {...props}>
                {children}
              </code>
            )
          },

          // 自定义链接渲染
          a({ node, children, href, ...props }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 hover:decoration-blue-300"
                {...props}
              >
                {children}
              </a>
            )
          },

          // 自定义引用块
          blockquote({ node, children, ...props }) {
            return (
              <blockquote
                className="border-l-4 border-emerald-500 pl-4 py-2 my-4 bg-slate-800/50 rounded-r-lg italic text-slate-300"
                {...props}
              >
                {children}
              </blockquote>
            )
          },

          // 自定义表格
          table({ node, children, ...props }) {
            return (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border border-slate-700 rounded-lg overflow-hidden" {...props}>
                  {children}
                </table>
              </div>
            )
          },

          thead({ node, children, ...props }) {
            return (
              <thead className="bg-slate-800" {...props}>
                {children}
              </thead>
            )
          },

          th({ node, children, ...props }) {
            return (
              <th className="px-4 py-2 text-left text-slate-200 font-semibold border-b border-slate-700" {...props}>
                {children}
              </th>
            )
          },

          td({ node, children, ...props }) {
            return (
              <td className="px-4 py-2 text-slate-300 border-b border-slate-800" {...props}>
                {children}
              </td>
            )
          },

          // 自定义列表
          ul({ node, children, ...props }) {
            return (
              <ul className="list-disc list-inside space-y-2 my-4 text-slate-300" {...props}>
                {children}
              </ul>
            )
          },

          ol({ node, children, ...props }) {
            return (
              <ol className="list-decimal list-inside space-y-2 my-4 text-slate-300" {...props}>
                {children}
              </ol>
            )
          },

          // 自定义标题
          h1({ node, children, ...props }) {
            return (
              <h1 className="text-3xl font-bold text-white mb-4 mt-6 pb-2 border-b border-slate-700" {...props}>
                {children}
              </h1>
            )
          },

          h2({ node, children, ...props }) {
            return (
              <h2 className="text-2xl font-bold text-white mb-3 mt-5" {...props}>
                {children}
              </h2>
            )
          },

          h3({ node, children, ...props }) {
            return (
              <h3 className="text-xl font-semibold text-white mb-2 mt-4" {...props}>
                {children}
              </h3>
            )
          },

          // 自定义段落
          p({ node, children, ...props }) {
            return (
              <p className="text-slate-300 leading-relaxed my-3" {...props}>
                {children}
              </p>
            )
          },

          // 自定义水平线
          hr({ node, ...props }) {
            return <hr className="my-6 border-slate-700" {...props} />
          },
        }}
      >
        {renderedContent}
      </ReactMarkdown>

      {/* 流式输出中的光标动画 */}
      {isStreaming && (
        <span className="inline-block w-2 h-4 ml-1 bg-emerald-500 animate-pulse" />
      )}
    </div>
  )
})

StreamingMarkdown.displayName = 'StreamingMarkdown'

export default StreamingMarkdown
