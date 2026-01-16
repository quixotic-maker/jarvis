import { useEffect, useState } from 'react'

/**
 * 检测页面是否可见的Hook
 * 用于在页面不可见时暂停不必要的操作，提升性能
 * @returns 页面是否可见
 */
export function usePageVisibility(): boolean {
  const [isVisible, setIsVisible] = useState<boolean>(!document.hidden)

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden)
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  return isVisible
}

/**
 * 在页面可见时执行回调的Hook
 * @param callback 页面可见时执行的回调函数
 * @param deps 依赖项数组
 */
export function useOnPageVisible(callback: () => void, deps: any[] = []) {
  const isVisible = usePageVisibility()

  useEffect(() => {
    if (isVisible) {
      callback()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isVisible, ...deps])
}
