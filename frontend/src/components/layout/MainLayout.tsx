import { useState, ReactNode } from 'react'
import Sidebar from './Sidebar'
import TopNav from './TopNav'

export interface MainLayoutProps {
  children: ReactNode
  title?: string
  subtitle?: string
  showVoice?: boolean
  onVoiceClick?: () => void
}

const MainLayout = ({
  children,
  title,
  subtitle,
  showVoice = true,
  onVoiceClick,
}: MainLayoutProps) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* 侧边栏 */}
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部导航 */}
        <TopNav
          title={title}
          subtitle={subtitle}
          showVoice={showVoice}
          onVoiceClick={onVoiceClick}
        />

        {/* 内容区域 */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout
