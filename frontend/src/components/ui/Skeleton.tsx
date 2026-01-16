interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card'
  width?: string
  height?: string
  className?: string
}

export default function Skeleton({ 
  variant = 'rectangular', 
  width, 
  height,
  className = '' 
}: SkeletonProps) {
  const baseClass = 'animate-pulse bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800 bg-[length:200%_100%]'
  
  const variantClass = {
    text: 'rounded h-4 w-full',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'rounded-xl',
  }[variant]

  const style = {
    width: width || (variant === 'circular' ? '40px' : undefined),
    height: height || (variant === 'circular' ? '40px' : '100%'),
  }

  return (
    <div 
      className={`${baseClass} ${variantClass} ${className}`}
      style={style}
    />
  )
}

// 预定义的骨架屏组合

export function CardSkeleton() {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 space-y-4">
      <div className="flex items-center gap-4">
        <Skeleton variant="circular" width="48px" height="48px" />
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
      <Skeleton variant="rectangular" height="100px" />
      <div className="flex gap-2">
        <Skeleton variant="rectangular" width="80px" height="32px" />
        <Skeleton variant="rectangular" width="80px" height="32px" />
      </div>
    </div>
  )
}

export function ListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 bg-gray-800/30 rounded-lg">
          <Skeleton variant="circular" width="40px" height="40px" />
          <div className="flex-1 space-y-2">
            <Skeleton variant="text" width="70%" />
            <Skeleton variant="text" width="50%" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="grid gap-4 p-4 bg-gray-800/50 rounded-lg" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} variant="text" width="80%" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="grid gap-4 p-4 bg-gray-800/30 rounded-lg" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} variant="text" width="90%" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <Skeleton variant="text" width="40%" height="24px" className="mb-6" />
      <div className="flex items-end justify-between gap-2 h-64">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton 
            key={i} 
            variant="rectangular" 
            width="100%" 
            height={`${Math.random() * 60 + 40}%`}
          />
        ))}
      </div>
    </div>
  )
}
