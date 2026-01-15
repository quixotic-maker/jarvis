import { useState } from 'react'
import { MainLayout } from '../components/layout'
import { Card, Badge, Button, Input } from '../components/ui'
import {
  Search,
  Plus,
  Brain,
  Network,
  Zap,
  BookOpen,
  Link2,
  Filter,
  Download,
  Share2,
  Maximize2,
} from 'lucide-react'

// 知识节点类型
interface KnowledgeNode {
  id: string
  label: string
  type: 'concept' | 'skill' | 'project' | 'resource' | 'person'
  description: string
  connections: number
  lastUpdated: string
}

// 模拟知识节点数据
const knowledgeNodes: KnowledgeNode[] = [
  {
    id: '1',
    label: 'React',
    type: 'skill',
    description: '前端框架，用于构建用户界面',
    connections: 12,
    lastUpdated: '2天前',
  },
  {
    id: '2',
    label: 'TypeScript',
    type: 'skill',
    description: 'JavaScript的超集，提供静态类型检查',
    connections: 15,
    lastUpdated: '1周前',
  },
  {
    id: '3',
    label: 'Jarvis项目',
    type: 'project',
    description: '智能助手项目，第二大脑系统',
    connections: 25,
    lastUpdated: '刚刚',
  },
  {
    id: '4',
    label: 'AI知识',
    type: 'concept',
    description: '人工智能相关概念和理论',
    connections: 18,
    lastUpdated: '3天前',
  },
  {
    id: '5',
    label: 'Python编程',
    type: 'skill',
    description: 'Python语言及其生态系统',
    connections: 20,
    lastUpdated: '5天前',
  },
  {
    id: '6',
    label: '机器学习',
    type: 'concept',
    description: '机器学习算法和应用',
    connections: 22,
    lastUpdated: '1周前',
  },
]

// 节点类型配置
const nodeTypeConfig = {
  concept: { color: 'blue', icon: Brain, label: '概念' },
  skill: { color: 'emerald', icon: Zap, label: '技能' },
  project: { color: 'purple', icon: Network, label: '项目' },
  resource: { color: 'orange', icon: BookOpen, label: '资源' },
  person: { color: 'pink', icon: Network, label: '人物' },
}

export default function BrainPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<string>('all')
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null)

  // 过滤节点
  const filteredNodes = knowledgeNodes.filter((node) => {
    const matchSearch =
      searchQuery === '' ||
      node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      node.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchType = selectedType === 'all' || node.type === selectedType
    return matchSearch && matchType
  })

  // 统计信息
  const stats = {
    total: knowledgeNodes.length,
    concepts: knowledgeNodes.filter((n) => n.type === 'concept').length,
    skills: knowledgeNodes.filter((n) => n.type === 'skill').length,
    projects: knowledgeNodes.filter((n) => n.type === 'project').length,
    connections: knowledgeNodes.reduce((sum, n) => sum + n.connections, 0),
  }

  return (
    <MainLayout
      title="知识大脑"
      subtitle={`${stats.total} 个知识节点，${stats.connections} 个连接`}
    >
      <div className="h-full flex">
        {/* 左侧：知识图谱可视化区域 */}
        <div className="flex-1 flex flex-col bg-slate-950/50">
          {/* 顶部工具栏 */}
          <div className="border-b border-slate-800 bg-slate-900/30 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button variant="primary" size="sm" leftIcon={<Plus className="w-4 h-4" />}>
                  添加节点
                </Button>
                <Button variant="outline" size="sm" leftIcon={<Filter className="w-4 h-4" />}>
                  筛选
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm">
                  <Download className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <Share2 className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="sm">
                  <Maximize2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* 3D可视化区域 */}
          <div className="flex-1 relative">
            {/* 占位：3D图谱容器 */}
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
              {/* 网格背景 */}
              <div className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage: `
                    linear-gradient(to right, rgb(148 163 184 / 0.1) 1px, transparent 1px),
                    linear-gradient(to bottom, rgb(148 163 184 / 0.1) 1px, transparent 1px)
                  `,
                  backgroundSize: '50px 50px',
                }}
              />

              {/* 中心节点示意 */}
              <div className="relative">
                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center animate-pulse shadow-2xl shadow-emerald-500/50">
                  <Brain className="w-16 h-16 text-white" />
                </div>

                {/* 外围节点示意 */}
                {[...Array(6)].map((_, i) => {
                  const angle = (i * 60 * Math.PI) / 180
                  const radius = 150
                  const x = Math.cos(angle) * radius
                  const y = Math.sin(angle) * radius
                  
                  return (
                    <div
                      key={i}
                      className="absolute w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-lg shadow-blue-500/30 cursor-pointer hover:scale-110 transition-transform"
                      style={{
                        left: `calc(50% + ${x}px - 2rem)`,
                        top: `calc(50% + ${y}px - 2rem)`,
                      }}
                    >
                      <Network className="w-8 h-8 text-white" />
                    </div>
                  )
                })}

                {/* 连接线 */}
                <svg className="absolute inset-0 w-full h-full" style={{ left: '-50%', top: '-50%', width: '200%', height: '200%' }}>
                  {[...Array(6)].map((_, i) => {
                    const angle = (i * 60 * Math.PI) / 180
                    const radius = 150
                    const x = Math.cos(angle) * radius
                    const y = Math.sin(angle) * radius
                    
                    return (
                      <line
                        key={i}
                        x1="50%"
                        y1="50%"
                        x2={`calc(50% + ${x}px)`}
                        y2={`calc(50% + ${y}px)`}
                        stroke="url(#gradient)"
                        strokeWidth="2"
                        className="opacity-50"
                      />
                    )
                  })}
                  <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#10b981" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              {/* 提示文字 */}
              <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-center">
                <p className="text-slate-400 text-sm mb-2">3D知识图谱可视化</p>
                <p className="text-slate-600 text-xs">
                  这里将展示交互式3D知识图谱（需要集成Three.js或Force Graph 3D）
                </p>
              </div>
            </div>
          </div>

          {/* 底部信息栏 */}
          <div className="border-t border-slate-800 bg-slate-900/50 px-6 py-4">
            <div className="flex items-center justify-between text-sm text-slate-400">
              <div className="flex items-center gap-6">
                <span>节点: {filteredNodes.length}</span>
                <span>连接: {stats.connections}</span>
                <span>深度: 3层</span>
              </div>
              <div className="flex items-center gap-2">
                <span>视图:</span>
                <Button variant="ghost" size="sm">2D</Button>
                <Button variant="primary" size="sm">3D</Button>
                <Button variant="ghost" size="sm">列表</Button>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：节点信息和操作面板 */}
        <div className="w-96 border-l border-slate-800 bg-slate-900/30 flex flex-col">
          {/* 搜索 */}
          <div className="p-4 border-b border-slate-800">
            <Input
              placeholder="搜索知识节点..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              leftIcon={<Search className="w-5 h-5" />}
            />
          </div>

          {/* 统计卡片 */}
          <div className="p-4 border-b border-slate-800 space-y-3">
            <Card variant="glass">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold text-white">{stats.total}</p>
                  <p className="text-sm text-slate-400">知识节点</p>
                </div>
                <Brain className="w-8 h-8 text-emerald-400" />
              </div>
            </Card>

            <div className="grid grid-cols-2 gap-3">
              <Card variant="glass">
                <div className="text-center">
                  <p className="text-xl font-bold text-blue-400">{stats.concepts}</p>
                  <p className="text-xs text-slate-500">概念</p>
                </div>
              </Card>
              <Card variant="glass">
                <div className="text-center">
                  <p className="text-xl font-bold text-emerald-400">{stats.skills}</p>
                  <p className="text-xs text-slate-500">技能</p>
                </div>
              </Card>
            </div>
          </div>

          {/* 类型筛选 */}
          <div className="p-4 border-b border-slate-800">
            <p className="text-sm font-medium text-slate-400 mb-3">节点类型</p>
            <div className="flex flex-wrap gap-2">
              <Badge
                variant={selectedType === 'all' ? 'success' : 'default'}
                className="cursor-pointer"
                onClick={() => setSelectedType('all')}
              >
                全部
              </Badge>
              {Object.entries(nodeTypeConfig).map(([type, config]) => (
                <Badge
                  key={type}
                  variant={selectedType === type ? 'info' : 'default'}
                  className="cursor-pointer"
                  onClick={() => setSelectedType(type)}
                >
                  {config.label}
                </Badge>
              ))}
            </div>
          </div>

          {/* 节点列表 */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            <p className="text-sm font-medium text-slate-400 mb-3">
              知识节点 ({filteredNodes.length})
            </p>
            {filteredNodes.map((node) => {
              const config = nodeTypeConfig[node.type]
              const Icon = config.icon
              
              return (
                <Card
                  key={node.id}
                  variant={selectedNode?.id === node.id ? 'glow' : 'glass'}
                  hoverable
                  className="cursor-pointer"
                  onClick={() => setSelectedNode(node)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg bg-${config.color}-500/10 border border-${config.color}-500/20`}>
                      <Icon className={`w-5 h-5 text-${config.color}-400`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-white truncate">
                          {node.label}
                        </h4>
                        <Badge variant="default" size="sm">
                          {config.label}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-2">
                        {node.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Link2 className="w-3 h-3" />
                          {node.connections}
                        </span>
                        <span>{node.lastUpdated}</span>
                      </div>
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>

          {/* 选中节点详情 */}
          {selectedNode && (
            <div className="border-t border-slate-800 p-4">
              <h3 className="font-semibold text-white mb-3">节点详情</h3>
              <div className="space-y-3">
                <Button variant="primary" size="sm" className="w-full">
                  编辑节点
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  查看关系
                </Button>
                <Button variant="ghost" size="sm" className="w-full text-red-400 hover:text-red-300">
                  删除节点
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  )
}
