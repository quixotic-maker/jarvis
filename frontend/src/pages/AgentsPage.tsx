import { useState } from 'react'
import { MainLayout } from '../components/layout'
import { Input, Badge, Button, Card } from '../components/ui'
import AgentCard from '../components/AgentCard'
import {
  Search,
  Filter,
  Calendar,
  CheckSquare,
  Mail,
  Users,
  FileText,
  Bell,
  Code,
  BarChart3,
  Calculator,
  BookOpen,
  Cloud,
  Newspaper,
  Plane,
  Heart,
  Lightbulb,
  Languages,
  FileSignature,
  UserCircle,
  Database,
  Activity,
} from 'lucide-react'

// Agent分类
const categories = [
  { id: 'all', label: '全部', count: 21 },
  { id: 'office', label: '办公效率', count: 7 },
  { id: 'tech', label: '技术开发', count: 3 },
  { id: 'learning', label: '学习成长', count: 2 },
  { id: 'life', label: '生活服务', count: 9 },
]

// Agent数据
const agents = [
  // 办公效率类
  {
    id: '1',
    name: 'ScheduleAgent',
    description: '智能日程管理，自动提取时间、地点、参与者，冲突检测',
    icon: Calendar,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '2分钟前',
    capabilities: ['日程创建', '冲突检测', '智能提醒'],
  },
  {
    id: '2',
    name: 'TaskAgent',
    description: '待办事项管理，优先级设置，进度跟踪，任务标签管理',
    icon: CheckSquare,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '5分钟前',
    capabilities: ['任务管理', '优先级', '进度跟踪'],
  },
  {
    id: '3',
    name: 'EmailAgent',
    description: '智能邮件助手，自动撰写邮件，调整语气，生成主题',
    icon: Mail,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '10分钟前',
    capabilities: ['邮件撰写', '语气调整', '模板生成'],
  },
  {
    id: '4',
    name: 'MeetingAgent',
    description: '会议管理和协作，会议安排，参会人管理，会议纪要生成',
    icon: Users,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '15分钟前',
    capabilities: ['会议安排', '纪要生成', '行动项跟进'],
  },
  {
    id: '5',
    name: 'FileAgent',
    description: '文件管理和搜索，智能文件搜索，文件整理建议',
    icon: FileText,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '20分钟前',
    capabilities: ['文件搜索', '智能整理', '分类管理'],
  },
  {
    id: '6',
    name: 'NoteAgent',
    description: '笔记管理和知识整理，笔记分类，标签管理，知识库',
    icon: FileSignature,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '25分钟前',
    capabilities: ['笔记管理', '知识整理', '标签分类'],
  },
  {
    id: '7',
    name: 'ReminderAgent',
    description: '智能提醒管理，定时提醒，重复提醒，优先级设置',
    icon: Bell,
    category: 'office',
    categoryLabel: '办公效率',
    status: 'idle' as const,
    lastActive: '30分钟前',
    capabilities: ['定时提醒', '重复提醒', '优先级'],
  },

  // 技术开发类
  {
    id: '8',
    name: 'CodeAgent',
    description: '代码助手，代码生成，代码解释，代码优化，Bug修复',
    icon: Code,
    category: 'tech',
    categoryLabel: '技术开发',
    status: 'thinking' as const,
    lastActive: '刚刚',
    capabilities: ['代码生成', '代码优化', 'Bug修复'],
  },
  {
    id: '9',
    name: 'DataAnalysisAgent',
    description: '数据分析和洞察，数据统计，趋势分析，可视化建议',
    icon: BarChart3,
    category: 'tech',
    categoryLabel: '技术开发',
    status: 'idle' as const,
    lastActive: '1小时前',
    capabilities: ['数据分析', '趋势预测', '可视化'],
  },
  {
    id: '10',
    name: 'CalculationAgent',
    description: '数学计算和数据分析，基本运算，复杂公式，统计分析',
    icon: Calculator,
    category: 'tech',
    categoryLabel: '技术开发',
    status: 'idle' as const,
    lastActive: '2小时前',
    capabilities: ['数学计算', '公式求解', '单位转换'],
  },

  // 学习成长类
  {
    id: '11',
    name: 'LearningAgent',
    description: '学习辅助和知识管理，制定学习计划，概念解释，生成测验',
    icon: BookOpen,
    category: 'learning',
    categoryLabel: '学习成长',
    status: 'idle' as const,
    lastActive: '3小时前',
    capabilities: ['学习计划', '知识解释', '测验生成'],
  },
  {
    id: '12',
    name: 'InfoRetrievalAgent',
    description: '信息检索，智能问答，概念解释，信息搜索',
    icon: Database,
    category: 'learning',
    categoryLabel: '学习成长',
    status: 'idle' as const,
    lastActive: '4小时前',
    capabilities: ['知识问答', '信息检索', '概念解释'],
  },

  // 生活服务类
  {
    id: '13',
    name: 'WeatherAgent',
    description: '天气查询和预报，当前天气，未来预报，穿衣建议',
    icon: Cloud,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '5小时前',
    capabilities: ['天气查询', '天气预报', '穿衣建议'],
  },
  {
    id: '14',
    name: 'NewsAgent',
    description: '新闻获取和摘要，分类新闻，新闻摘要，个性化推荐',
    icon: Newspaper,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '6小时前',
    capabilities: ['新闻获取', '新闻摘要', '个性化推荐'],
  },
  {
    id: '15',
    name: 'TravelAgent',
    description: '旅行规划和建议，行程规划，景点推荐，预算建议',
    icon: Plane,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '昨天',
    capabilities: ['行程规划', '景点推荐', '预算建议'],
  },
  {
    id: '16',
    name: 'HealthAgent',
    description: '健康管理和建议，健康建议，运动计划，饮食计划',
    icon: Heart,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '昨天',
    capabilities: ['健康建议', '运动计划', '饮食计划'],
  },
  {
    id: '17',
    name: 'RecommendationAgent',
    description: '个性化推荐，电影推荐，书籍推荐，音乐推荐',
    icon: Lightbulb,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '2天前',
    capabilities: ['电影推荐', '书籍推荐', '音乐推荐'],
  },
  {
    id: '18',
    name: 'TranslationAgent',
    description: '多语言翻译，多语言互译，自动语言检测，专业术语处理',
    icon: Languages,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '2天前',
    capabilities: ['多语言翻译', '术语处理', '地道翻译'],
  },
  {
    id: '19',
    name: 'SummaryAgent',
    description: '文本摘要和要点提取，智能总结，关键信息提取',
    icon: FileText,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '3天前',
    capabilities: ['文本总结', '要点提取', '摘要生成'],
  },
  {
    id: '20',
    name: 'ContactAgent',
    description: '联系人管理，添加联系人，搜索联系人，关系管理',
    icon: UserCircle,
    category: 'life',
    categoryLabel: '生活服务',
    status: 'idle' as const,
    lastActive: '3天前',
    capabilities: ['联系人管理', '关系管理', '沟通记录'],
  },
  {
    id: '21',
    name: 'Coordinator',
    description: '主控Agent，智能调度，任务分配，多Agent协作',
    icon: Activity,
    category: 'life',
    categoryLabel: '系统核心',
    status: 'success' as const,
    lastActive: '始终在线',
    capabilities: ['智能调度', '任务分配', '协调管理'],
  },
]

export default function AgentsPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  // 过滤Agent
  const filteredAgents = agents.filter((agent) => {
    const matchCategory = selectedCategory === 'all' || agent.category === selectedCategory
    const matchSearch =
      searchQuery === '' ||
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchCategory && matchSearch
  })

  // 统计信息
  const stats = {
    total: agents.length,
    active: agents.filter((a) => a.status === 'thinking').length,
    idle: agents.filter((a) => a.status === 'idle').length,
  }

  return (
    <MainLayout title="Agent 中心" subtitle={`${filteredAgents.length} 个智能助手`}>
      <div className="h-full flex flex-col">
        {/* 顶部统计 */}
        <div className="border-b border-slate-800 bg-slate-900/30 px-6 py-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-3 gap-4 mb-6">
              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                    <Users className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.total}</p>
                    <p className="text-sm text-slate-400">全部Agent</p>
                  </div>
                </div>
              </Card>

              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                    <Activity className="w-6 h-6 text-blue-400 animate-pulse" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.active}</p>
                    <p className="text-sm text-slate-400">正在工作</p>
                  </div>
                </div>
              </Card>

              <Card variant="glass">
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-slate-500/10 border border-slate-500/20">
                    <Users className="w-6 h-6 text-slate-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.idle}</p>
                    <p className="text-sm text-slate-400">待命中</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* 搜索和筛选 */}
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  placeholder="搜索 Agent..."
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

        {/* Agent列表 */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-7xl mx-auto">
            {filteredAgents.length === 0 ? (
              <div className="text-center py-20">
                <Users className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <p className="text-lg text-slate-400">未找到匹配的 Agent</p>
                <p className="text-sm text-slate-500 mt-2">试试调整搜索条件</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {filteredAgents.map((agent) => {
                  const Icon = agent.icon
                  return (
                    <AgentCard
                      key={agent.id}
                      name={agent.name}
                      description={agent.description}
                      icon={undefined}
                      status={agent.status}
                      category={agent.categoryLabel}
                      lastActive={agent.lastActive}
                      onClick={() => console.log('Selected agent:', agent.name)}
                    />
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
