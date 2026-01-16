import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MainLayout } from '../components/layout'
import { Card, Badge, Button, Input } from '../components/ui'
import ResultCard from '../components/ResultCard'
import { learningAPI, type LearningPlan, type DailyTask } from '../api/client'
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
  Loader2,
} from 'lucide-react'

export default function LearningPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  // 获取学习计划列表
  const { data: plansData, isLoading } = useQuery({
    queryKey: ['learning', 'plans'],
    queryFn: async () => {
      const response = await learningAPI.plans.list()
      return response.data
    },
  })

  // 获取今日任务
  const { data: todayTasksData } = useQuery({
    queryKey: ['learning', 'tasks', 'today'],
    queryFn: async () => {
      const response = await learningAPI.tasks.today()
      return response.data
    },
  })

  const learningPlans = plansData?.data || []
  const todayTasks = todayTasksData?.data || []

  // 统计数据
  const stats = {
    totalPlans: learningPlans.length,
    completedTasks: learningPlans.reduce((sum: number, p: LearningPlan) => sum + p.completed_tasks_count, 0),
    totalTasks: learningPlans.reduce((sum: number, p: LearningPlan) => sum + p.tasks_count, 0),
    resources: 0, // TODO: 添加资源API后更新
    avgProgress: learningPlans.length > 0
      ? Math.round(learningPlans.reduce((sum: number, p: LearningPlan) => sum + p.progress, 0) / learningPlans.length)
      : 0,
  }

  if (isLoading) {
    return (
      <MainLayout title="学习工作台" subtitle="加载中...">
        <div className="flex items-center justify-center h-full">
          <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
        </div>
      </MainLayout>
    )
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
              {learningPlans.length === 0 ? (
                <div className="col-span-2 text-center py-12 text-slate-400">
                  <Target className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>暂无学习计划，点击"新建计划"开始学习吧！</p>
                </div>
              ) : (
                learningPlans.map((plan: LearningPlan) => (
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
                        <div className="flex items-center justify-between text-xs text-slate-400">
                          <span className="flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            {plan.completed_tasks_count}/{plan.tasks_count} 任务完成
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {new Date(plan.end_date || plan.start_date).toLocaleDateString('zh-CN')}
                          </span>
                        </div>
                      </div>

                      {/* 标签 */}
                      {plan.tags && plan.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {plan.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" size="sm">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}

                      {/* 操作按钮 */}
                      <div className="flex gap-2">
                        <Button variant="secondary" size="sm" className="flex-1">
                          查看详情
                        </Button>
                        <Button variant="secondary" size="sm" className="flex-1">
                          继续学习
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* 学习资源 - 暂未实现 */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">学习资源</h2>
              <Button variant="outline" size="sm" disabled>
                <Plus className="w-4 h-4 mr-2" />
                添加资源
              </Button>
            </div>
            
            <Card variant="glass">
              <div className="text-center py-12 text-slate-400">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>学习资源功能即将推出...</p>
              </div>
            </Card>
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
