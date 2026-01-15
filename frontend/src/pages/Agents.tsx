import { useQuery } from '@tanstack/react-query'
import { agentAPI } from '../api/client'
import Layout from '../components/Layout'
import { Bot, Activity, Clock } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function Agents() {
  const { data: agents = [] } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => (await agentAPI.list()).data,
  })

  const { data: logs = [] } = useQuery({
    queryKey: ['agent-logs'],
    queryFn: async () => (await agentAPI.logs()).data,
  })

  return (
    <Layout>
      <div className="p-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Agent管理</h1>
            <p className="text-slate-400">查看系统中所有可用的智能Agent及其活动日志</p>
          </div>

          {/* Agents列表 */}
          <div>
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Bot className="w-5 h-5 text-primary-500" />
              可用Agents
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent) => (
                <div
                  key={agent.name}
                  className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-primary-600 transition-all"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-primary-900/50 rounded-lg">
                      <Bot className="w-6 h-6 text-primary-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                  </div>
                  <p className="text-slate-400 text-sm">{agent.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* 执行日志 */}
          <div>
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary-500" />
              执行日志
            </h2>
            <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-900">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      Agent
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      操作
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      任务ID
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      执行时间
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      状态
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                      时间
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-700/50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <Bot className="w-4 h-4 text-primary-400" />
                          <span className="text-sm font-medium text-white">{log.agent_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-300">
                        {log.action}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                        {log.task_id ? `#${log.task_id}` : '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {log.execution_time}ms
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          log.status === 'success' 
                            ? 'bg-green-900 text-green-300' 
                            : 'bg-red-900 text-red-300'
                        }`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                        {formatDistanceToNow(new Date(log.created_at), { 
                          addSuffix: true,
                          locale: zhCN 
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {logs.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  暂无执行日志
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
