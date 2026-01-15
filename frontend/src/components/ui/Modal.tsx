import { ReactNode, useEffect } from 'react'
import { X } from 'lucide-react'
import Button from './Button'

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  closeOnEsc?: boolean
}

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEsc = true,
}: ModalProps) => {
  // ESC键关闭
  useEffect(() => {
    if (!isOpen || !closeOnEsc) return

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [isOpen, closeOnEsc, onClose])

  // 防止背景滚动
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  // 尺寸映射
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full m-4',
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      onClick={(e) => {
        if (closeOnOverlayClick && e.target === e.currentTarget) {
          onClose()
        }
      }}
    >
      {/* 遮罩层 */}
      <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm" />

      {/* 模态框内容 */}
      <div
        className={`
          relative w-full ${sizes[size]}
          bg-slate-800 rounded-2xl
          border border-slate-700
          shadow-2xl shadow-emerald-500/10
          animate-slide-up
          max-h-[90vh] flex flex-col
        `}
      >
        {/* 头部 */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b border-slate-700">
            {title && (
              <h2 className="text-xl font-bold text-white">{title}</h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="
                  p-2 rounded-lg
                  text-slate-400 hover:text-white
                  hover:bg-slate-700
                  transition-all duration-200
                "
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        {/* 内容区域 - 可滚动 */}
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>

        {/* 底部 */}
        {footer && (
          <div className="flex items-center justify-end gap-3 p-6 border-t border-slate-700">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}

export default Modal
