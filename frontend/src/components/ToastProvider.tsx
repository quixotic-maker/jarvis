import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { Toast, ToastType, ToastProps } from '../ui/Toast'

interface ToastContextType {
  toast: (type: ToastType, title: string, message?: string, duration?: number) => void
  success: (title: string, message?: string, duration?: number) => void
  error: (title: string, message?: string, duration?: number) => void
  info: (title: string, message?: string, duration?: number) => void
  warning: (title: string, message?: string, duration?: number) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

interface ToastProviderProps {
  children: ReactNode
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Omit<ToastProps, 'onClose'>[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback(
    (type: ToastType, title: string, message?: string, duration = 5000) => {
      const id = Math.random().toString(36).substring(2, 9)
      setToasts((prev) => [...prev, { id, type, title, message, duration }])
    },
    []
  )

  const success = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast('success', title, message, duration)
    },
    [toast]
  )

  const error = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast('error', title, message, duration)
    },
    [toast]
  )

  const info = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast('info', title, message, duration)
    },
    [toast]
  )

  const warning = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast('warning', title, message, duration)
    },
    [toast]
  )

  return (
    <ToastContext.Provider value={{ toast, success, error, info, warning }}>
      {children}
      
      {/* Toast容器 */}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        <div className="flex flex-col gap-2 pointer-events-auto">
          {toasts.map((toastProps) => (
            <Toast key={toastProps.id} {...toastProps} onClose={removeToast} />
          ))}
        </div>
      </div>
    </ToastContext.Provider>
  )
}
