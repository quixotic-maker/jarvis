import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { taskAPI, scheduleAPI, agentAPI } from '../api/client'
import Layout from '../components/Layout'
import InputBox from '../components/InputBox'
import { CheckCircle, Clock, XCircle, Calendar, Activity, TrendingUp } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function Dashboard() {
  const queryClient = useQueryClient()

  // 查询数据
  const { data: tasks = [] } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => (await taskAPI.list()).data,
  })

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => (await scheduleAPI.list()).data,
  })

  const { data: agents = [] } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => (await agentAPI.list()).data,
  })

  const { data: logs = [] } = useQuery({
    queryKey: ['agent-logs'],
    queryFn: async () => (await agentAPI.logs()).data,
  })

  // 创建任务的mutation
  const createTask = useMutation({
    mutationFn: (input: string) => taskAPI.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['agent-logs'] })
    },
  })

  const handleSubmit = async (input: string) => {
    await createTask.mutateAsync(input)
  }

  // 统计数据
  const stats = {
    totalTasks: tasks.length,
    completedTasks: tasks.filter(t => t.status === 'completed').length,
    pendingTasks: tasks.filter(t => t.status === 'pending' || t.status === 'processing').length,
    upcomingSchedules: schedules.filter(s => !s.is_completed).length,
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />
    }
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* 头部 */}
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">欢迎回来！</h1>
            <p className="text-slate-400">通过自然语言与Jarvis交互，让AI助手帮您完成任务</p>
          </div>

          {/* 输入框 */}
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <InputBox onSubmit={handleSubmit} placeholder="告诉Jarvis您想做什么..." />
          </div>

          {/* 统计卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <StatCard
              icon={<Activity className="w-6 h-6" />}
              label="总任务数"
              value={stats.totalTasks}
              color="primary"
            />
            <StatCard
              icon={<CheckCircle className="w-6 h-6" />}
              label="已完成"
              value={stats.completedTasks}
              color="green"
            />
            <StatCard
              icon={<Clock className="w-6 h-6" />}
              label="进行中"
              value={stats.pendingTasks}
              color="yellow"
            />
            <StatCard
              icon={<Calendar className="w-6 h-6" />}
              label="待办日程"
              value={stats.upcomingSchedules}
              color="blue"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 最近任务 */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary-500" />
                最近任务
              </h2>
              <div className="space-y-3">
                {tasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="bg-slate-700 rounded-lg p-4 flex items-start gap-3"
                  >
                    {getStatusIcon(task.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium truncate">{task.user_input}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-slate-400">{task.task_type}</span>
                        <span className="text-xs text-slate-500">
                          {formatDistanceToNow(new Date(task.created_at), { 
                            addSuffix: true,
                            locale: zhCN 
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
                {tasks.length === 0 && (
                  <p className="text-slate-400 text-center py-8">还没有任务</p>
                )}
              </div>
            </div>

            {/* Agent状态 */}
            <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-500" />
                Agent活动
              </h2>
              <div className="space-y-3">
                {logs.slice(0, 5).map((log) => (
                  <div
                    key={log.id}
                    className="bg-slate-700 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-medium">{log.agent_name}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        log.status === 'success' 
                          ? 'bg-green-900 text-green-300' 
                          : 'bg-red-900 text-red-300'
                      }`}>
                        {log.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 truncate">{log.action}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-slate-500">
                        {log.execution_time}ms
                      </span>
                      <span className="text-xs text-slate-600">•</span>
                      <span className="text-xs text-slate-500">
                        {formatDistanceToNow(new Date(log.created_at), { 
                          addSuffix: true,
                          locale: zhCN 
                        })}
                      </span>
                    </div>
                  </div>
                ))}
                {logs.length === 0 && (
                  <p className="text-slate-400 text-center py-8">暂无活动记录</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: number
  color: 'primary' | 'green' | 'yellow' | 'blue'
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  const colorClasses = {
    primary: 'bg-primary-900/50 text-primary-400 border-primary-800',
    green: 'bg-green-900/50 text-green-400 border-green-800',
    yellow: 'bg-yellow-900/50 text-yellow-400 border-yellow-800',
    blue: 'bg-blue-900/50 text-blue-400 border-blue-800',
  }

  return (
    <div className={`rounded-xl p-6 border ${colorClasses[color]}`}>
      <div className="flex items-center gap-3">
        <div className="p-3 bg-slate-800 rounded-lg">
          {icon}
        </div>
        <div>
          <p className="text-slate-400 text-sm">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
        </div>
      </div>
    </div>
  )
}
