import { forwardRef, HTMLAttributes } from 'react'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
  icon?: React.ReactNode
  actions?: React.ReactNode
  variant?: 'default' | 'glass' | 'glow'
  hoverable?: boolean
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      title,
      subtitle,
      icon,
      actions,
      variant = 'default',
      hoverable = false,
      className = '',
      ...props
    },
    ref
  ) => {
    // 变体样式
    const variants = {
      default: 'bg-slate-800/50 border border-slate-700',
      glass: 'glass',
      glow: 'bg-slate-800/50 border border-emerald-500/30 glow',
    }

    const baseStyles = `
      backdrop-blur-sm rounded-2xl p-6 shadow-xl
      transition-all duration-300
      ${hoverable ? 'card-hover cursor-pointer hover:border-emerald-500/30' : ''}
    `

    return (
      <div
        ref={ref}
        className={`
          ${baseStyles}
          ${variants[variant]}
          ${className}
        `}
        {...props}
      >
        {/* 卡片头部 */}
        {(title || actions) && (
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {icon && (
                <div className="p-2 bg-emerald-500/10 rounded-lg flex-shrink-0">
                  {icon}
                </div>
              )}
              <div className="min-w-0 flex-1">
                {title && (
                  <h3 className="text-lg font-semibold text-slate-100 truncate">
                    {title}
                  </h3>
                )}
                {subtitle && (
                  <p className="text-sm text-slate-500 truncate">{subtitle}</p>
                )}
              </div>
            </div>
            {actions && (
              <div className="flex items-center gap-2 flex-shrink-0">
                {actions}
              </div>
            )}
          </div>
        )}

        {/* 卡片内容 */}
        <div className="text-slate-300">{children}</div>
      </div>
    )
  }
)

Card.displayName = 'Card'

export default Card
