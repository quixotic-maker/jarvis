import { ReactNode, useState } from 'react'

export interface TooltipProps {
  children: ReactNode
  content: string | ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  delay?: number
}

const Tooltip = ({
  children,
  content,
  position = 'top',
  delay = 200,
}: TooltipProps) => {
  const [isVisible, setIsVisible] = useState(false)
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null)

  const handleMouseEnter = () => {
    const id = setTimeout(() => {
      setIsVisible(true)
    }, delay)
    setTimeoutId(id)
  }

  const handleMouseLeave = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    setIsVisible(false)
  }

  // 位置样式
  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  // 箭头样式
  const arrows = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-slate-800',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-slate-800',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-slate-800',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-slate-800',
  }

  return (
    <div
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}

      {/* Tooltip内容 */}
      {isVisible && (
        <div
          className={`
            absolute z-50 px-3 py-2
            bg-slate-800 text-slate-100
            text-sm rounded-lg
            border border-slate-700
            shadow-lg shadow-slate-900/50
            whitespace-nowrap
            animate-fade-in
            ${positions[position]}
          `}
        >
          {content}

          {/* 箭头 */}
          <div
            className={`
              absolute w-0 h-0
              border-4 border-transparent
              ${arrows[position]}
            `}
          />
        </div>
      )}
    </div>
  )
}

export default Tooltip
