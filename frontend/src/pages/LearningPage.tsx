import { useState } from 'react'
import { MainLayout } from '../components/layout'
import { Card, Badge, Button, Input } from '../components/ui'
import ResultCard from '../components/ResultCard'
import {
  BookOpen,
  Target,
  CheckCircle2,
  Clock,
  TrendingUp,
  Award,
  FileText,
  Link2,
  Plus,
  Search,
} from 'lucide-react'

// 学习资源类型
interface LearningResource {
  id: string
  title: string
  type: 'video' | 'article' | 'book' | 'course' | 'doc'
  progress: number
  duration: string
  tags: string[]
  url?: string
}

// 学习计划类型
interface LearningPlan {
  id: string
  title: string
  goal: string
  progress: number
  dueDate: string
  tasks: number
  completedTasks: number
}

// 示例数据
const learningPlans: LearningPlan[] = [
  {
    id: '1',
    title: 'React高级进阶',
    goal: '掌握React Hooks和性能优化',
    progress: 65,
    dueDate: '2026-02-15',
    tasks: 10,
    completedTasks: 7,
  },
  {
    id: '2',
    title: 'TypeScript深入学习',
    goal: '熟练使用高级类型和泛型',
    progress: 40,
    dueDate: '2026-02-28',
    tasks: 8,
    completedTasks: 3,
  },
  {
    id: '3',
    title: '系统设计与架构',
    goal: '理解分布式系统设计原则',
    progress: 20,
    dueDate: '2026-03-30',
    tasks: 15,
    completedTasks: 3,
  },
]

const resources: LearningResource[] = [
  {
    id: '1',
    title: 'React性能优化最佳实践',
    type: 'article',
    progress: 100,
    duration: '15分钟',
    tags: ['React', '性能优化'],
    url: 'https://example.com',
  },
  {
    id: '2',
    title: 'TypeScript类型体操',
    type: 'video',
    progress: 45,
    duration: '2小时',
    tags: ['TypeScript', '高级'],
  },
  {
    id: '3',
    title: '设计模式详解',
    type: 'book',
    progress: 30,
    duration: '300页',
    tags: ['设计模式', '架构'],
  },
]

export default function LearningPage() {
  const [searchQuery, setSearchQuery] = useState('')

  // 统计数据
  const stats = {
    totalPlans: learningPlans.length,
    completedTasks: learningPlans.reduce((sum, p) => sum + p.completedTasks, 0),
    totalTasks: learningPlans.reduce((sum, p) => sum + p.tasks, 0),
    resources: resources.length,
    avgProgress: Math.round(
      learningPlans.reduce((sum, p) => sum + p.progress, 0) / learningPlans.length
    ),
  }

  return (
    <MainLayout
      title="学习工作台"
      subtitle={`${stats.totalPlans} 个学习计划 · ${stats.completedTasks}/${stats.totalTasks} 任务完成`}
    >
      <div className="h-full overflow-y-auto">
        <div className="max-w-7xl mx-auto p-6 space-y-6">
          {/* 统计卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <Target className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.totalPlans}</p>
                  <p className="text-sm text-slate-400">学习计划</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                  <CheckCircle2 className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">
                    {stats.completedTasks}/{stats.totalTasks}
                  </p>
                  <p className="text-sm text-slate-400">任务进度</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                  <BookOpen className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.resources}</p>
                  <p className="text-sm text-slate-400">学习资源</p>
                </div>
              </div>
            </Card>

            <Card variant="glass">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20">
                  <TrendingUp className="w-6 h-6 text-orange-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stats.avgProgress}%</p>
                  <p className="text-sm text-slate-400">平均进度</p>
                </div>
              </div>
            </Card>
          </div>

          {/* 学习计划 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">学习计划</h2>
              <Button
                variant="primary"
                size="sm"
                leftIcon={<Plus className="w-4 h-4" />}
              >
                新建计划
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {learningPlans.map((plan) => (
                <Card key={plan.id} variant="glass" hoverable>
                  <div className="space-y-4">
                    {/* 标题和进度 */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-white mb-1">
                          {plan.title}
                        </h3>
                        <p className="text-sm text-slate-400">{plan.goal}</p>
                      </div>
                      <Badge
                        variant={
                          plan.progress >= 80 ? 'success' :
                          plan.progress >= 40 ? 'info' : 'warning'
                        }
                      >
                        {plan.progress}%
                      </Badge>
                    </div>

                    {/* 进度条 */}
                    <div className="space-y-2">
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            plan.progress >= 80 ? 'bg-emerald-500' :
                            plan.progress >= 40 ? 'bg-blue-500' : 'bg-orange-500'
                          }`}
                          style={{ width: `${plan.progress}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500">
                        <span>
                          {plan.completedTasks}/{plan.tasks} 任务完成
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {plan.dueDate}
                        </span>
                      </div>
                    </div>

                    {/* 操作按钮 */}
                    <div className="flex items-center gap-2 pt-2 border-t border-slate-700">
                      <Button variant="outline" size="sm" className="flex-1">
                        查看详情
                      </Button>
                      <Button variant="primary" size="sm" className="flex-1">
                        继续学习
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* 学习资源 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">学习资源</h2>
              <div className="flex items-center gap-2">
                <Input
                  placeholder="搜索资源..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  leftIcon={<Search className="w-4 h-4" />}
                  className="w-64"
                />
                <Button variant="outline" size="sm">
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {resources.map((resource) => (
                <ResultCard
                  key={resource.id}
                  title={resource.title}
                  subtitle={resource.duration}
                  icon={
                    resource.type === 'video' ? FileText :
                    resource.type === 'article' ? FileText :
                    resource.type === 'book' ? BookOpen : FileText
                  }
                  type={resource.type === 'video' ? 'data' : 'file'}
                  metadata={[
                    { label: '类型', value: resource.type },
                    { label: '进度', value: `${resource.progress}%` },
                    { label: '时长', value: resource.duration },
                  ]}
                  actions={[
                    {
                      label: '继续学习',
                      variant: 'primary',
                      onClick: () => console.log('Continue learning'),
                    },
                  ]}
                  showShare
                  showDownload={resource.progress === 100}
                >
                  {/* 进度条 */}
                  <div className="mb-4">
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all"
                        style={{ width: `${resource.progress}%` }}
                      />
                    </div>
                  </div>

                  {/* 标签 */}
                  <div className="flex flex-wrap gap-2">
                    {resource.tags.map((tag, index) => (
                      <Badge key={index} variant="purple" size="sm">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  {/* 链接 */}
                  {resource.url && (
                    <div className="mt-3 flex items-center gap-2 text-sm text-emerald-400">
                      <Link2 className="w-4 h-4" />
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                      >
                        访问资源
                      </a>
                    </div>
                  )}
                </ResultCard>
              ))}
            </div>
          </div>

          {/* 学习成就 */}
          <div>
            <h2 className="text-xl font-bold text-white mb-4">最近成就</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { title: '坚持学习7天', icon: Award, color: 'emerald' },
                { title: '完成10个任务', icon: CheckCircle2, color: 'blue' },
                { title: '学习100小时', icon: Clock, color: 'purple' },
              ].map((achievement, index) => {
                const Icon = achievement.icon
                return (
                  <Card key={index} variant="glass">
                    <div className="flex items-center gap-4">
                      <div className={`p-3 rounded-xl bg-${achievement.color}-500/10 border border-${achievement.color}-500/20`}>
                        <Icon className={`w-6 h-6 text-${achievement.color}-400`} />
                      </div>
                      <div>
                        <p className="font-medium text-white">{achievement.title}</p>
                        <p className="text-xs text-slate-500">刚刚解锁</p>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
