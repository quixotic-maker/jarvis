import { useQuery } from '@tanstack/react-query'
import { taskAPI } from '../api/client'
import Layout from '../components/Layout'
import { CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function Tasks() {
  const { data: tasks = [], isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => (await taskAPI.list()).data,
  })

  const getStatusBadge = (status: string) => {
    const badges = {
      completed: { icon: CheckCircle, text: '已完成', class: 'bg-green-900 text-green-300' },
      failed: { icon: XCircle, text: '失败', class: 'bg-red-900 text-red-300' },
      processing: { icon: Clock, text: '处理中', class: 'bg-yellow-900 text-yellow-300' },
      pending: { icon: AlertCircle, text: '待处理', class: 'bg-blue-900 text-blue-300' },
    }
    const badge = badges[status as keyof typeof badges] || badges.pending
    const Icon = badge.icon
    
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${badge.class}`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    )
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-slate-400">加载中...</div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-8">任务列表</h1>

          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-900">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    用户输入
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Agent
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    创建时间
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-slate-700/50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      #{task.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-white max-w-md">
                      {task.user_input}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded">
                        {task.task_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {task.assigned_agent || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {getStatusBadge(task.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                      {formatDistanceToNow(new Date(task.created_at), { 
                        addSuffix: true,
                        locale: zhCN 
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {tasks.length === 0 && (
              <div className="text-center py-12 text-slate-400">
                还没有任务记录
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
