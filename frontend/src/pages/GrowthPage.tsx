import { useState } from 'react'
import { MainLayout } from '../components/layout'
import { Card, Badge, Button } from '../components/ui'
import {
  TrendingUp,
  Award,
  Target,
  Calendar,
  Zap,
  Heart,
  Brain,
  Code,
  BookOpen,
  Users,
} from 'lucide-react'

// 成长事件类型
interface GrowthEvent {
  id: string
  date: string
  type: 'achievement' | 'milestone' | 'learning' | 'project'
  title: string
  description: string
  impact: 'high' | 'medium' | 'low'
  category: string
}

// 能力维度
interface SkillDimension {
  name: string
  value: number
  maxValue: number
  color: string
}

// 示例数据
const growthEvents: GrowthEvent[] = [
  {
    id: '1',
    date: '2026-01-15',
    type: 'achievement',
    title: '完成Jarvis V3 UI重构',
    description: '重新设计并实现了完整的UI组件体系',
    impact: 'high',
    category: '技术',
  },
  {
    id: '2',
    date: '2026-01-10',
    type: 'learning',
    title: '掌握React性能优化',
    description: '学习了useMemo、useCallback等优化技巧',
    impact: 'medium',
    category: '学习',
  },
  {
    id: '3',
    date: '2026-01-05',
    type: 'milestone',
    title: '项目上线1周年',
    description: 'Jarvis项目成功运行一周年',
    impact: 'high',
    category: '里程碑',
  },
  {
    id: '4',
    date: '2025-12-28',
    type: 'project',
    title: '实现21个智能Agent',
    description: '构建了完整的Agent生态系统',
    impact: 'high',
    category: '技术',
  },
  {
    id: '5',
    date: '2025-12-20',
    type: 'learning',
    title: 'TypeScript进阶学习',
    description: '深入学习了高级类型和泛型编程',
    impact: 'medium',
    category: '学习',
  },
]

const skillDimensions: SkillDimension[] = [
  { name: '前端开发', value: 85, maxValue: 100, color: 'emerald' },
  { name: '后端开发', value: 70, maxValue: 100, color: 'blue' },
  { name: '系统设计', value: 65, maxValue: 100, color: 'purple' },
  { name: 'AI/ML', value: 60, maxValue: 100, color: 'orange' },
  { name: '项目管理', value: 75, maxValue: 100, color: 'pink' },
  { name: '沟通协作', value: 80, maxValue: 100, color: 'cyan' },
]

const eventTypeConfig = {
  achievement: { icon: Award, label: '成就', color: 'emerald' },
  milestone: { icon: Target, label: '里程碑', color: 'purple' },
  learning: { icon: BookOpen, label: '学习', color: 'blue' },
  project: { icon: Code, label: '项目', color: 'orange' },
}

export default function GrowthPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month')

  // 统计数据
  const stats = {
    totalEvents: growthEvents.length,
    achievements: growthEvents.filter((e) => e.type === 'achievement').length,
    learning: growthEvents.filter((e) => e.type === 'learning').length,
    avgSkill: Math.round(
      skillDimensions.reduce((sum, s) => sum + s.value, 0) / skillDimensions.length
    ),
  }

  // 雷达图坐标计算
  const radarPoints = skillDimensions.map((skill, index) => {
    const angle = (index * 2 * Math.PI) / skillDimensions.length - Math.PI / 2
    const radius = 120
    const value = (skill.value / skill.maxValue) * radius
    const x = 200 + Math.cos(angle) * value
    const y = 200 + Math.sin(angle) * value
    return { x, y, angle, label: skill.name, value: skill.value }
  })

  const radarPath = radarPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`).join(' ') + ' Z'

  return (
    <MainLayout
      title="成长轨迹"
      subtitle={`${stats.totalEvents} 个成长记录 · 平均能力 ${stats.avgSkill}分`}
    >
      <div className="h-full overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6 space-y-6">
          {/* 统计卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <TrendingUp className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.totalEvents}</p>
                  <p className="text-sm text-slate-400">成长事件</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                  <Award className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.achievements}</p>
                  <p className="text-sm text-slate-400">解锁成就</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                  <BookOpen className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.learning}</p>
                  <p className="text-sm text-slate-400">学习记录</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20">
                  <Zap className="w-6 h-6 text-orange-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.avgSkill}</p>
                  <p className="text-sm text-slate-400">平均能力值</p>
                </div>
              </div>
            </Card>
          </div>

          {/* 能力雷达图 */}
          <Card variant="glass">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-6">能力雷达图</h2>
              
              <div className="flex items-center justify-center">
                <svg width="500" height="500" viewBox="0 0 400 400">
                  {/* 背景网格 */}
                  {[0.2, 0.4, 0.6, 0.8, 1].map((ratio, i) => {
                    const gridPoints = skillDimensions.map((_, index) => {
                      const angle = (index * 2 * Math.PI) / skillDimensions.length - Math.PI / 2
                      const radius = 120 * ratio
                      return {
                        x: 200 + Math.cos(angle) * radius,
                        y: 200 + Math.sin(angle) * radius,
                      }
                    })
                    const gridPath = gridPoints.map((p, j) => `${j === 0 ? 'M' : 'L'} ${p.x},${p.y}`).join(' ') + ' Z'
                    
                    return (
                      <path
                        key={i}
                        d={gridPath}
                        fill="none"
                        stroke="rgb(71 85 105)"
                        strokeWidth="1"
                        opacity={0.3}
                      />
                    )
                  })}

                  {/* 从中心到各顶点的线 */}
                  {radarPoints.map((point, i) => (
                    <line
                      key={i}
                      x1="200"
                      y1="200"
                      x2={200 + Math.cos(point.angle) * 120}
                      y2={200 + Math.sin(point.angle) * 120}
                      stroke="rgb(71 85 105)"
                      strokeWidth="1"
                      opacity={0.3}
                    />
                  ))}

                  {/* 能力数据区域 */}
                  <path
                    d={radarPath}
                    fill="url(#radarGradient)"
                    stroke="rgb(16 185 129)"
                    strokeWidth="2"
                    opacity={0.8}
                  />

                  {/* 数据点 */}
                  {radarPoints.map((point, i) => (
                    <g key={i}>
                      <circle
                        cx={point.x}
                        cy={point.y}
                        r="4"
                        fill="rgb(16 185 129)"
                        stroke="white"
                        strokeWidth="2"
                      />
                      
                      {/* 标签 */}
                      <text
                        x={200 + Math.cos(point.angle) * 150}
                        y={200 + Math.sin(point.angle) * 150}
                        textAnchor="middle"
                        dominantBaseline="middle"
                        className="text-xs fill-slate-300 font-medium"
                      >
                        {point.label}
                      </text>
                      
                      {/* 数值 */}
                      <text
                        x={200 + Math.cos(point.angle) * 150}
                        y={200 + Math.sin(point.angle) * 150 + 15}
                        textAnchor="middle"
                        className="text-xs fill-emerald-400"
                      >
                        {point.value}
                      </text>
                    </g>
                  ))}

                  {/* 渐变定义 */}
                  <defs>
                    <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="rgb(16 185 129)" stopOpacity="0.4" />
                      <stop offset="100%" stopColor="rgb(6 182 212)" stopOpacity="0.2" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              {/* 能力列表 */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
                {skillDimensions.map((skill, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">{skill.name}</span>
                      <span className="text-emerald-400 font-medium">{skill.value}</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all"
                        style={{ width: `${(skill.value / skill.maxValue) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {/* 成长时间线 */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">成长时间线</h2>
              <div className="flex items-center gap-2 bg-slate-800 rounded-lg p-1">
                <Button
                  variant={selectedPeriod === 'week' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedPeriod('week')}
                >
                  本周
                </Button>
                <Button
                  variant={selectedPeriod === 'month' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedPeriod('month')}
                >
                  本月
                </Button>
                <Button
                  variant={selectedPeriod === 'year' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedPeriod('year')}
                >
                  今年
                </Button>
              </div>
            </div>

            <div className="relative">
              {/* 时间线竖线 */}
              <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-emerald-500 via-blue-500 to-purple-500" />

              {/* 事件列表 */}
              <div className="space-y-6">
                {growthEvents.map((event, index) => {
                  const config = eventTypeConfig[event.type]
                  const Icon = config.icon
                  
                  return (
                    <div key={event.id} className="relative pl-20">
                      {/* 时间线节点 */}
                      <div className={`absolute left-6 w-5 h-5 rounded-full bg-${config.color}-500 border-4 border-slate-950 z-10`} />

                      {/* 日期 */}
                      <div className="absolute left-0 top-0 w-12 text-xs text-slate-500 text-right pr-8">
                        {event.date.slice(5)}
                      </div>

                      {/* 事件卡片 */}
                      <Card variant="glass" hoverable>
                        <div className="flex items-start gap-4">
                          <div className={`p-3 rounded-xl bg-${config.color}-500/10 border border-${config.color}-500/20`}>
                            <Icon className={`w-6 h-6 text-${config.color}-400`} />
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <h3 className="font-semibold text-white">{event.title}</h3>
                              <Badge
                                variant={
                                  event.impact === 'high' ? 'success' :
                                  event.impact === 'medium' ? 'info' : 'default'
                                }
                                size="sm"
                              >
                                {event.impact === 'high' ? '高影响' :
                                 event.impact === 'medium' ? '中影响' : '低影响'}
                              </Badge>
                            </div>
                            
                            <p className="text-sm text-slate-400 mb-3">
                              {event.description}
                            </p>
                            
                            <div className="flex items-center gap-2">
                              <Badge variant="purple" size="sm">
                                {config.label}
                              </Badge>
                              <Badge variant="default" size="sm">
                                {event.category}
                              </Badge>
                              <span className="text-xs text-slate-500 flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {event.date}
                              </span>
                            </div>
                          </div>
                        </div>
                      </Card>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
