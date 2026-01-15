import { ButtonHTMLAttributes, forwardRef } from 'react'
import { Loader2 } from 'lucide-react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    // 变体样式
    const variants = {
      primary: `
        bg-gradient-to-r from-emerald-500 to-teal-600
        text-white shadow-lg hover:shadow-emerald-500/50
        hover:scale-105 active:scale-95
      `,
      secondary: `
        bg-gradient-to-r from-purple-500 to-pink-600
        text-white shadow-lg hover:shadow-purple-500/50
        hover:scale-105 active:scale-95
      `,
      outline: `
        border-2 border-emerald-500 text-emerald-400
        hover:bg-emerald-500/10 hover:border-emerald-400
      `,
      ghost: `
        text-slate-300 hover:bg-slate-800 hover:text-white
      `,
      danger: `
        bg-gradient-to-r from-red-500 to-red-600
        text-white shadow-lg hover:shadow-red-500/50
        hover:scale-105 active:scale-95
      `,
    }

    // 尺寸样式
    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    }

    const baseStyles = `
      inline-flex items-center justify-center gap-2
      rounded-xl font-medium
      transition-all duration-200 ease-out
      focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-slate-900
      disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
    `

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`
          ${baseStyles}
          ${variants[variant]}
          ${sizes[size]}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          leftIcon && <span className="flex-shrink-0">{leftIcon}</span>
        )}
        {children}
        {rightIcon && !isLoading && (
          <span className="flex-shrink-0">{rightIcon}</span>
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
