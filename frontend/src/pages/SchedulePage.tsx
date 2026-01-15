import { useState, useEffect } from 'react'
import { MainLayout } from '../components/layout'
import { Card, Badge, Button, Modal } from '../components/ui'
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  Clock,
  MapPin,
  Users,
  Loader2,
  Video,
} from 'lucide-react'
import * as scheduleApi from '../api/schedule'
import type { Schedule } from '../api/types'

// 日程事件类型（转换用）
interface ScheduleEvent {
  id: number
  title: string
  startTime: string
  endTime: string
  type: 'meeting' | 'task' | 'reminder' | 'event'
  location?: string
  attendees?: string[]
  priority?: 'high' | 'medium' | 'low'
  color: string
  description?: string
  isCompleted: boolean
}

// 将API数据转换为UI数据
const convertToEvent = (schedule: Schedule): ScheduleEvent => {
  const startDate = new Date(schedule.start_time)
  const endDate = schedule.end_time ? new Date(schedule.end_time) : null
  
  const colorMap: Record<string, string> = {
    meeting: 'emerald',
    task: 'purple',
    reminder: 'orange',
    event: 'blue',
  }
  
  return {
    id: schedule.id,
    title: schedule.title,
    startTime: startDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    endTime: endDate?.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) || '',
    type: schedule.event_type as any,
    location: schedule.location || undefined,
    attendees: schedule.attendees || [],
    priority: schedule.priority as any,
    color: colorMap[schedule.event_type] || 'blue',
    description: schedule.description || undefined,
    isCompleted: schedule.is_completed,
  }
}

// 生成日历日期
const generateCalendarDays = (year: number, month: number) => {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  const startDay = firstDay.getDay()

  const days: (number | null)[] = []
  
  // 添加上个月的日期（填充）
  for (let i = 0; i < startDay; i++) {
    days.push(null)
  }
  
  // 添加本月的日期
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i)
  }
  
  return days
}

export default function SchedulePage() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month')
  const [showAddModal, setShowAddModal] = useState(false)
  
  // API状态
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()
  const today = new Date()

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ]

  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const calendarDays = generateCalendarDays(year, month)
  
  // 加载日程数据
  useEffect(() => {
    loadSchedules()
  }, [currentDate])
  
  const loadSchedules = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await scheduleApi.getSchedules({
        page: 1,
        page_size: 100,
        user_id: 'default_user',
      })
      setSchedules(response.data)
    } catch (err: any) {
      setError(err.message || '加载日程失败')
      console.error('加载日程失败:', err)
    } finally {
      setLoading(false)
    }
  }
  
  // 转换为事件格式
  const events = schedules.map(convertToEvent)

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const handleToday = () => {
    setCurrentDate(new Date())
    setSelectedDate(new Date())
  }

  const isToday = (day: number | null) => {
    if (!day) return false
    return (
      day === today.getDate() &&
      month === today.getMonth() &&
      year === today.getFullYear()
    )
  }

  const isSelected = (day: number | null) => {
    if (!day) return false
    return (
      day === selectedDate.getDate() &&
      month === selectedDate.getMonth() &&
      year === selectedDate.getFullYear()
    )
  }

  // 获取当天的日程
  const todayEvents = events.filter((event) => {
    const schedule = schedules.find(s => s.id === event.id)
    if (!schedule) return false
    
    const eventDate = new Date(schedule.start_time)
    return (
      eventDate.getDate() === selectedDate.getDate() &&
      eventDate.getMonth() === selectedDate.getMonth() &&
      eventDate.getFullYear() === selectedDate.getFullYear()
    )
  })
  
  // 获取某天的日程数量
  const getDayEventCount = (day: number) => {
    return schedules.filter(schedule => {
      const eventDate = new Date(schedule.start_time)
      return (
        eventDate.getDate() === day &&
        eventDate.getMonth() === month &&
        eventDate.getFullYear() === year
      )
    }).length
  }

  return (
    <MainLayout
      title="日程管理"
      subtitle={`${year}年${month + 1}月 · ${events.length} 个日程`}
    >
      <div className="h-full flex">
        {/* 左侧：日历视图 */}
        <div className="flex-1 flex flex-col bg-slate-950/50">
          {/* 顶部工具栏 */}
          <div className="border-b border-slate-800 bg-slate-900/30 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleToday}
                >
                  今天
                </Button>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handlePrevMonth}
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </Button>
                  
                  <h2 className="text-xl font-bold text-white min-w-[120px] text-center">
                    {year}年 {monthNames[month]}
                  </h2>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNextMonth}
                  >
                    <ChevronRight className="w-5 h-5" />
                  </Button>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-1">
                  <Button
                    variant={viewMode === 'month' ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('month')}
                  >
                    月
                  </Button>
                  <Button
                    variant={viewMode === 'week' ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('week')}
                  >
                    周
                  </Button>
                  <Button
                    variant={viewMode === 'day' ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('day')}
                  >
                    日
                  </Button>
                </div>

                <Button
                  variant="primary"
                  size="sm"
                  leftIcon={<Plus className="w-4 h-4" />}
                  onClick={() => setShowAddModal(true)}
                >
                  添加日程
                </Button>
              </div>
            </div>
          </div>

          {/* 日历主体 */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="max-w-6xl mx-auto">
              {/* 星期标题 */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {weekDays.map((day) => (
                  <div
                    key={day}
                    className="text-center text-sm font-medium text-slate-400 py-2"
                  >
                    周{day}
                  </div>
                ))}
              </div>

              {/* 日期网格 */}
              <div className="grid grid-cols-7 gap-2">
                {calendarDays.map((day, index) => (
                  <div
                    key={index}
                    className={`
                      aspect-square p-2 rounded-xl border transition-all cursor-pointer
                      ${day === null
                        ? 'bg-slate-900/30 border-slate-800/50 cursor-default'
                        : isToday(day)
                        ? 'bg-emerald-500/20 border-emerald-500/50 ring-2 ring-emerald-500/30'
                        : isSelected(day)
                        ? 'bg-blue-500/20 border-blue-500/50'
                        : 'bg-slate-900/50 border-slate-800 hover:bg-slate-800/50 hover:border-slate-700'
                      }
                    `}
                    onClick={() => {
                      if (day) {
                        setSelectedDate(new Date(year, month, day))
                      }
                    }}
                  >
                    {day && (
                      <>
                        <div className={`
                          text-sm font-medium mb-1
                          ${isToday(day)
                            ? 'text-emerald-400'
                            : isSelected(day)
                            ? 'text-blue-400'
                            : 'text-white'
                          }
                        `}>
                          {day}
                        </div>
                        
                        {/* 日程指示点 */}
                        {getDayEventCount(day) > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {[...Array(Math.min(3, getDayEventCount(day)))].map((_, i) => (
                              <div
                                key={i}
                                className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                              />
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：日程列表 */}
        <div className="w-96 border-l border-slate-800 bg-slate-900/30 flex flex-col">
          {/* 日期信息 */}
          <div className="p-6 border-b border-slate-800">
            <h3 className="text-2xl font-bold text-white mb-1">
              {selectedDate.getDate()}日
            </h3>
            <p className="text-sm text-slate-400">
              {year}年{selectedDate.getMonth() + 1}月 · 
              周{weekDays[selectedDate.getDay()]}
            </p>
          </div>

          {/* 日程列表 */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-slate-400">
                今日日程 ({todayEvents.length})
              </h4>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <Loader2 className="w-8 h-8 text-emerald-500 mx-auto mb-3 animate-spin" />
                <p className="text-sm text-slate-500">加载中...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-sm text-red-400 mb-4">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadSchedules}
                >
                  重试
                </Button>
              </div>
            ) : todayEvents.length === 0 ? (
              <div className="text-center py-12">
                <CalendarIcon className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                <p className="text-sm text-slate-500">今天还没有日程</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={() => setShowAddModal(true)}
                >
                  添加日程
                </Button>
              </div>
            ) : (
              todayEvents.map((event) => (
                <Card
                  key={event.id}
                  variant="glass"
                  hoverable
                  className={`border-l-4 border-${event.color}-500`}
                >
                  <div className="space-y-3">
                    {/* 标题和优先级 */}
                    <div className="flex items-start justify-between gap-2">
                      <h5 className="font-semibold text-white flex-1">
                        {event.title}
                      </h5>
                      {event.priority === 'high' && (
                        <Badge variant="error" size="sm">
                          重要
                        </Badge>
                      )}
                    </div>

                    {/* 时间 */}
                    <div className="flex items-center gap-2 text-sm text-slate-400">
                      <Clock className="w-4 h-4" />
                      <span>{event.startTime} - {event.endTime}</span>
                    </div>

                    {/* 地点 */}
                    {event.location && (
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <MapPin className="w-4 h-4" />
                        <span>{event.location}</span>
                      </div>
                    )}

                    {/* 参与者 */}
                    {event.attendees && event.attendees.length > 0 && (
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <Users className="w-4 h-4" />
                        <span>{event.attendees.join(', ')}</span>
                      </div>
                    )}

                    {/* 类型标签 */}
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          event.type === 'meeting' ? 'info' :
                          event.type === 'task' ? 'purple' :
                          event.type === 'reminder' ? 'warning' : 'default'
                        }
                        size="sm"
                      >
                        {event.type === 'meeting' ? '会议' :
                         event.type === 'task' ? '任务' :
                         event.type === 'reminder' ? '提醒' : '事件'}
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 添加日程弹窗 */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="添加日程"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-slate-400">
            这里将是添加日程的表单...
          </p>
          {/* TODO: 添加日程表单 */}
        </div>
      </Modal>
    </MainLayout>
  )
}
