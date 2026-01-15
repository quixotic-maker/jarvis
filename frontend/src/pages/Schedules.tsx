import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { scheduleAPI } from '../api/client'
import Layout from '../components/Layout'
import { Calendar, MapPin, Clock, CheckCircle } from 'lucide-react'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'

export default function Schedules() {
  const queryClient = useQueryClient()
  
  const { data: schedules = [], isLoading } = useQuery({
    queryKey: ['schedules'],
    queryFn: async () => (await scheduleAPI.list()).data,
  })

  const completeSchedule = useMutation({
    mutationFn: (id: number) => scheduleAPI.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
    },
  })

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
          <h1 className="text-3xl font-bold text-white mb-8">日程管理</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schedules.map((schedule) => (
              <div
                key={schedule.id}
                className={`bg-slate-800 rounded-xl p-6 border ${
                  schedule.is_completed 
                    ? 'border-green-800 bg-green-900/20' 
                    : 'border-slate-700'
                } transition-all hover:shadow-lg`}
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex-1">
                    {schedule.title}
                  </h3>
                  {schedule.is_completed && (
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 ml-2" />
                  )}
                </div>

                {schedule.description && (
                  <p className="text-slate-300 text-sm mb-4">{schedule.description}</p>
                )}

                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {format(new Date(schedule.start_time), 'yyyy年MM月dd日', { locale: zhCN })}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-slate-400">
                    <Clock className="w-4 h-4" />
                    <span>
                      {format(new Date(schedule.start_time), 'HH:mm')}
                      {schedule.end_time && ` - ${format(new Date(schedule.end_time), 'HH:mm')}`}
                    </span>
                  </div>

                  {schedule.location && (
                    <div className="flex items-center gap-2 text-sm text-slate-400">
                      <MapPin className="w-4 h-4" />
                      <span>{schedule.location}</span>
                    </div>
                  )}
                </div>

                {!schedule.is_completed && (
                  <button
                    onClick={() => completeSchedule.mutate(schedule.id)}
                    className="mt-4 w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    标记为已完成
                  </button>
                )}
              </div>
            ))}
          </div>

          {schedules.length === 0 && (
            <div className="text-center py-12 text-slate-400">
              还没有日程安排
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
