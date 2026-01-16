import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误到日志服务
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })
    
    // TODO: 发送错误到监控服务
    // sendToErrorTracking(error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback
      }

      // 默认错误UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 shadow-2xl">
            {/* 错误图标 */}
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-10 h-10 text-red-500" />
              </div>
            </div>

            {/* 错误标题 */}
            <h1 className="text-3xl font-bold text-white text-center mb-4">
              糟糕，出错了！
            </h1>

            {/* 错误描述 */}
            <p className="text-gray-400 text-center mb-8">
              应用程序遇到了一个意外错误。我们已经记录了这个问题，将尽快修复。
            </p>

            {/* 错误详情（开发模式） */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-4 mb-6 max-h-60 overflow-auto">
                <p className="text-red-400 font-mono text-sm mb-2">
                  <strong>错误信息：</strong> {this.state.error.toString()}
                </p>
                {this.state.errorInfo && (
                  <pre className="text-gray-500 font-mono text-xs overflow-x-auto">
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-4 justify-center">
              <button
                onClick={this.handleReset}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 shadow-lg shadow-blue-500/20"
              >
                <RefreshCw className="w-5 h-5" />
                重试
              </button>
              <button
                onClick={this.handleGoHome}
                className="flex items-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200"
              >
                <Home className="w-5 h-5" />
                返回首页
              </button>
            </div>

            {/* 联系支持 */}
            <div className="mt-8 text-center">
              <p className="text-gray-500 text-sm">
                如果问题持续存在，请{' '}
                <a
                  href="mailto:support@jarvis.com"
                  className="text-blue-400 hover:text-blue-300 underline"
                >
                  联系技术支持
                </a>
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
