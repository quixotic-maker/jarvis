import { forwardRef, TextareaHTMLAttributes } from 'react'

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  helperText?: string
  maxLength?: number
  showCount?: boolean
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      label,
      error,
      helperText,
      maxLength,
      showCount = false,
      className = '',
      id,
      value,
      ...props
    },
    ref
  ) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`
    const currentLength = value?.toString().length || 0

    return (
      <div className="w-full">
        {/* 标签 */}
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-slate-300 mb-2"
          >
            {label}
          </label>
        )}

        {/* 文本框 */}
        <div className="relative">
          <textarea
            ref={ref}
            id={textareaId}
            maxLength={maxLength}
            value={value}
            className={`
              w-full px-4 py-3
              bg-slate-800 border rounded-xl
              ${error ? 'border-red-500 focus:ring-red-500' : 'border-slate-700 focus:ring-emerald-500'}
              text-slate-100 placeholder-slate-500
              focus:outline-none focus:ring-2 focus:border-transparent
              transition-all duration-200 resize-none
              disabled:opacity-50 disabled:cursor-not-allowed
              ${className}
            `}
            {...props}
          />

          {/* 字符计数 */}
          {showCount && maxLength && (
            <div className="absolute bottom-2 right-2 text-xs text-slate-500 pointer-events-none">
              {currentLength} / {maxLength}
            </div>
          )}
        </div>

        {/* 错误信息或帮助文本 */}
        {(error || helperText) && (
          <p
            className={`mt-1.5 text-sm ${
              error ? 'text-red-400' : 'text-slate-500'
            }`}
          >
            {error || helperText}
          </p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export default Textarea
