import { useState } from 'react'
import { MainLayout } from '../components/layout'
import { Badge, Button, Card, Input } from '../components/ui'
import ToolCard from '../components/ToolCard'
import {
  Search,
  Wrench,
  Code,
  Database,
  Globe,
  FileText,
  Image,
  Video,
  Music,
  Terminal,
  Cloud,
  Lock,
  Zap,
} from 'lucide-react'

// MCP工具分类
const categories = [
  { id: 'all', label: '全部', count: 12 },
  { id: 'dev', label: '开发工具', count: 4 },
  { id: 'data', label: '数据处理', count: 3 },
  { id: 'media', label: '媒体处理', count: 3 },
  { id: 'other', label: '其他', count: 2 },
]

// MCP工具数据
const tools = [
  // 开发工具
  {
    id: '1',
    name: 'Code Runner',
    description: '在安全的沙箱环境中执行代码片段，支持多种编程语言',
    icon: Code,
    category: 'dev',
    categoryLabel: '开发工具',
    version: '1.2.0',
    isEnabled: true,
    isRunning: false,
    lastRun: '2小时前',
  },
  {
    id: '2',
    name: 'Git Helper',
    description: 'Git 操作助手，自动化常见的版本控制任务',
    icon: Terminal,
    category: 'dev',
    categoryLabel: '开发工具',
    version: '2.0.1',
    isEnabled: true,
    isRunning: false,
    lastRun: '1天前',
  },
  {
    id: '3',
    name: 'API Tester',
    description: 'RESTful API 测试工具，支持多种认证方式',
    icon: Globe,
    category: 'dev',
    categoryLabel: '开发工具',
    version: '1.5.3',
    isEnabled: true,
    isRunning: false,
    lastRun: '3天前',
  },
  {
    id: '4',
    name: 'Database Query',
    description: '数据库查询工具，支持 SQL、MongoDB 等多种数据库',
    icon: Database,
    category: 'dev',
    categoryLabel: '开发工具',
    version: '3.1.0',
    isEnabled: false,
    isRunning: false,
    lastRun: '从未',
  },

  // 数据处理
  {
    id: '5',
    name: 'CSV Processor',
    description: 'CSV 文件处理，数据清洗、转换、分析',
    icon: FileText,
    category: 'data',
    categoryLabel: '数据处理',
    version: '1.0.5',
    isEnabled: true,
    isRunning: true,
    lastRun: '正在运行',
  },
  {
    id: '6',
    name: 'JSON Formatter',
    description: 'JSON 格式化、验证、转换工具',
    icon: FileText,
    category: 'data',
    categoryLabel: '数据处理',
    version: '2.3.1',
    isEnabled: true,
    isRunning: false,
    lastRun: '1小时前',
  },
  {
    id: '7',
    name: 'Data Analyzer',
    description: '数据分析工具，统计、可视化、趋势分析',
    icon: Database,
    category: 'data',
    categoryLabel: '数据处理',
    version: '1.8.2',
    isEnabled: true,
    isRunning: false,
    lastRun: '5小时前',
  },

  // 媒体处理
  {
    id: '8',
    name: 'Image Converter',
    description: '图片格式转换、压缩、裁剪',
    icon: Image,
    category: 'media',
    categoryLabel: '媒体处理',
    version: '2.1.0',
    isEnabled: true,
    isRunning: false,
    lastRun: '2天前',
  },
  {
    id: '9',
    name: 'Video Transcoder',
    description: '视频转码、剪辑、合并工具',
    icon: Video,
    category: 'media',
    categoryLabel: '媒体处理',
    version: '1.4.0',
    isEnabled: false,
    isRunning: false,
    lastRun: '从未',
  },
  {
    id: '10',
    name: 'Audio Processor',
    description: '音频处理、格式转换、降噪',
    icon: Music,
    category: 'media',
    categoryLabel: '媒体处理',
    version: '1.2.3',
    isEnabled: true,
    isRunning: false,
    lastRun: '1周前',
  },

  // 其他
  {
    id: '11',
    name: 'Cloud Storage',
    description: '云存储集成，支持多个云服务提供商',
    icon: Cloud,
    category: 'other',
    categoryLabel: '其他',
    version: '3.0.0',
    isEnabled: true,
    isRunning: false,
    lastRun: '昨天',
  },
  {
    id: '12',
    name: 'Encryption Tool',
    description: '加密解密工具，支持多种加密算法',
    icon: Lock,
    category: 'other',
    categoryLabel: '其他',
    version: '2.5.1',
    isEnabled: true,
    isRunning: false,
    lastRun: '3天前',
  },
]

export default function MCPToolsPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  // 过滤工具
  const filteredTools = tools.filter((tool) => {
    const matchCategory = selectedCategory === 'all' || tool.category === selectedCategory
    const matchSearch =
      searchQuery === '' ||
      tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  // 统计信息
  const stats = {
    total: tools.length,
    enabled: tools.filter((t) => t.isEnabled).length,
    running: tools.filter((t) => t.isRunning).length,
  }

  const handleExecute = (toolId: string) => {
    console.log('Execute tool:', toolId)
    // TODO: 实际执行逻辑
  }

  const handleConfigure = (toolId: string) => {
    console.log('Configure tool:', toolId)
    // TODO: 打开配置界面
  }

  const handleToggle = (toolId: string, enabled: boolean) => {
    console.log('Toggle tool:', toolId, enabled)
    // TODO: 更新工具启用状态
  }

  return (
    <MainLayout title="MCP 工具" subtitle={`${filteredTools.length} 个工具可用`}>
      <div className="h-full flex flex-col">
        {/* 顶部统计 */}
        <div className="border-b border-slate-800 bg-slate-900/30 px-6 py-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-3 gap-4 mb-6">
              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                    <Wrench className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.total}</p>
                    <p className="text-sm text-slate-400">全部工具</p>
                  </div>
                </div>
              </Card>

              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                    <Zap className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.enabled}</p>
                    <p className="text-sm text-slate-400">已启用</p>
                  </div>
                </div>
              </Card>

              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                    <Zap className="w-6 h-6 text-blue-400 animate-pulse" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.running}</p>
                    <p className="text-sm text-slate-400">正在运行</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* 搜索和筛选 */}
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  placeholder="搜索工具..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  leftIcon={<Search className="w-5 h-5" />}
                />
              </div>

              <div className="flex items-center gap-2">
                {categories.map((cat) => (
                  <Button
                    key={cat.id}
                    variant={selectedCategory === cat.id ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedCategory(cat.id)}
                  >
                    {cat.label}
                    <Badge
                      variant={selectedCategory === cat.id ? 'success' : 'default'}
                      size="sm"
                      className="ml-2"
                    >
                      {cat.count}
                    </Badge>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 工具列表 */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-7xl mx-auto">
            {filteredTools.length === 0 ? (
              <div className="text-center py-20">
                <Wrench className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <p className="text-lg text-slate-400">未找到匹配的工具</p>
                <p className="text-sm text-slate-500 mt-2">试试调整搜索条件</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filteredTools.map((tool) => (
                  <ToolCard
                    key={tool.id}
                    name={tool.name}
                    description={tool.description}
                    icon={tool.icon}
                    category={tool.categoryLabel}
                    isEnabled={tool.isEnabled}
                    isRunning={tool.isRunning}
                    version={tool.version}
                    lastRun={tool.lastRun}
                    onExecute={() => handleExecute(tool.id)}
                    onConfigure={() => handleConfigure(tool.id)}
                    onToggle={(enabled) => handleToggle(tool.id, enabled)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
