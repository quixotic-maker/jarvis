import { HTMLAttributes } from 'react'
import { Loader2 } from 'lucide-react'

export interface LoadingProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'dots' | 'pulse'
  text?: string
  fullScreen?: boolean
}

const Loading = ({
  size = 'md',
  variant = 'spinner',
  text,
  fullScreen = false,
  className = '',
  ...props
}: LoadingProps) => {
  // 尺寸映射
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  }

  // 渲染加载器
  const renderLoader = () => {
    switch (variant) {
      case 'spinner':
        return (
          <Loader2
            className={`animate-spin text-emerald-500 ${sizes[size]}`}
          />
        )

      case 'dots':
        return (
          <div className="flex items-center gap-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`
                  rounded-full bg-emerald-500
                  animate-pulse
                  ${size === 'sm' ? 'w-2 h-2' : ''}
                  ${size === 'md' ? 'w-3 h-3' : ''}
                  ${size === 'lg' ? 'w-4 h-4' : ''}
                  ${size === 'xl' ? 'w-6 h-6' : ''}
                `}
                style={{
                  animationDelay: `${i * 0.15}s`,
                }}
              />
            ))}
          </div>
        )

      case 'pulse':
        return (
          <div
            className={`
              rounded-full
              bg-gradient-to-r from-emerald-500 to-teal-500
              animate-pulse
              ${sizes[size]}
            `}
          />
        )

      default:
        return null
    }
  }

  const content = (
    <div
      className={`
        flex flex-col items-center justify-center gap-3
        ${className}
      `}
      {...props}
    >
      {renderLoader()}
      {text && (
        <p className="text-sm text-slate-400 animate-pulse">{text}</p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm z-50">
        {content}
      </div>
    )
  }

  return content
}

export default Loading
