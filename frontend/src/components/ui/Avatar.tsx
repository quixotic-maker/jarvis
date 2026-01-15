import { ImgHTMLAttributes } from 'react'

export interface AvatarProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'size'> {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  status?: 'online' | 'offline' | 'busy' | 'away'
  name?: string
  fallback?: string
}

const Avatar = ({
  src,
  alt,
  size = 'md',
  status,
  name,
  fallback,
  className = '',
  ...props
}: AvatarProps) => {
  // 尺寸样式
  const sizes = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-2xl',
  }

  // 状态颜色
  const statusColors = {
    online: 'bg-emerald-500',
    offline: 'bg-slate-500',
    busy: 'bg-red-500',
    away: 'bg-yellow-500',
  }

  // 状态指示器尺寸
  const statusSizes = {
    xs: 'w-1.5 h-1.5',
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
    xl: 'w-4 h-4',
  }

  // 生成首字母头像
  const getInitials = () => {
    if (fallback) return fallback
    if (name) {
      const names = name.split(' ')
      if (names.length >= 2) {
        return `${names[0][0]}${names[1][0]}`.toUpperCase()
      }
      return name.slice(0, 2).toUpperCase()
    }
    return '?'
  }

  return (
    <div className="relative inline-block">
      <div
        className={`
          rounded-full overflow-hidden
          bg-gradient-to-br from-emerald-500/20 to-teal-500/20
          border-2 border-emerald-500/30
          flex items-center justify-center
          font-semibold text-emerald-400
          ${sizes[size]}
          ${className}
        `}
      >
        {src ? (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="w-full h-full object-cover"
            {...props}
          />
        ) : (
          <span>{getInitials()}</span>
        )}
      </div>

      {/* 状态指示器 */}
      {status && (
        <span
          className={`
            absolute bottom-0 right-0
            rounded-full border-2 border-slate-900
            ${statusColors[status]}
            ${statusSizes[size]}
          `}
        />
      )}
    </div>
  )
}

export default Avatar
