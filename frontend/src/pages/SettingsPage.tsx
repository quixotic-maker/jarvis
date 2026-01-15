import { useState, useEffect } from 'react'
import MainLayout from '../components/layout/MainLayout'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Avatar from '../components/ui/Avatar'
import Badge from '../components/ui/Badge'
import * as settingsApi from '../api/settings'
import type { UserSettings } from '../api/types'
import { 
  User, 
  Settings, 
  Bell, 
  Palette, 
  Shield, 
  Database,
  MessageSquare,
  Globe,
  Zap,
  Moon,
  Sun,
  Monitor,
  Volume2,
  Key,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Briefcase,
  Github,
  Twitter,
  Linkedin,
  Save,
  Camera,
  Edit,
  Trash2,
  Plus,
  Check,
  X,
  Loader2
} from 'lucide-react'

interface SettingsTab {
  id: string
  name: string
  icon: React.ReactNode
  badge?: number
}

interface UserProfile {
  name: string
  email: string
  phone: string
  location: string
  bio: string
  avatar: string
  company: string
  position: string
  website: string
  github: string
  twitter: string
  linkedin: string
}

interface SystemPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US' | 'ja-JP'
  fontSize: 'small' | 'medium' | 'large'
  soundEnabled: boolean
  notificationsEnabled: boolean
  autoSave: boolean
}

interface AgentSettings {
  defaultAgent: string
  responseSpeed: 'fast' | 'balanced' | 'quality'
  creativity: number
  maxTokens: number
  temperature: number
  enableVoice: boolean
  enableMemory: boolean
}

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('profile')
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 用户资料
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: 'Liu Developer',
    email: 'liu@example.com',
    phone: '+86 138 0000 0000',
    location: '深圳，中国',
    bio: '全栈开发工程师，AI爱好者，致力于打造更智能的开发工具',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Liu',
    company: 'Tech Innovation Co.',
    position: '高级工程师',
    website: 'https://liudev.com',
    github: 'liu-dev',
    twitter: '@liu_developer',
    linkedin: 'liu-developer'
  })

  // 系统偏好设置
  const [systemPrefs, setSystemPrefs] = useState<SystemPreferences>({
    theme: 'dark',
    language: 'zh-CN',
    fontSize: 'medium',
    soundEnabled: true,
    notificationsEnabled: true,
    autoSave: true
  })

  // Agent设置
  const [agentSettings, setAgentSettings] = useState<AgentSettings>({
    defaultAgent: 'coordinator',
    responseSpeed: 'balanced',
    creativity: 70,
    maxTokens: 2000,
    temperature: 0.7,
    enableVoice: true,
    enableMemory: true
  })
  
  // 加载设置
  useEffect(() => {
    loadSettings()
  }, [])
  
  const loadSettings = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await settingsApi.getSettings('default_user')
      const settings = response.data.data.settings
      
      // 更新系统设置
      setSystemPrefs({
        theme: settings.system.theme as any,
        language: settings.system.language as any,
        fontSize: settings.system.font_size as any,
        soundEnabled: settings.system.sound_enabled,
        notificationsEnabled: settings.system.notifications_enabled,
        autoSave: settings.system.auto_save,
      })
      
      // 更新Agent设置
      setAgentSettings({
        defaultAgent: settings.agent.default_agent,
        responseSpeed: settings.agent.response_speed as any,
        creativity: settings.agent.creativity,
        maxTokens: settings.agent.max_tokens,
        temperature: settings.agent.temperature,
        enableVoice: settings.agent.enable_voice,
        enableMemory: settings.agent.enable_memory,
      })
    } catch (err: any) {
      setError(err.message || '加载设置失败')
      console.error('加载设置失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 标签页配置
  const tabs: SettingsTab[] = [
    { id: 'profile', name: '个人资料', icon: <User size={20} /> },
    { id: 'preferences', name: '系统偏好', icon: <Settings size={20} /> },
    { id: 'agents', name: 'Agent配置', icon: <MessageSquare size={20} /> },
    { id: 'notifications', name: '通知设置', icon: <Bell size={20} />, badge: 3 },
    { id: 'appearance', name: '外观主题', icon: <Palette size={20} /> },
    { id: 'security', name: '安全隐私', icon: <Shield size={20} /> },
    { id: 'data', name: '数据管理', icon: <Database size={20} /> },
    { id: 'advanced', name: '高级选项', icon: <Zap size={20} /> }
  ]

  // 保存设置
  const handleSave = async () => {
    setIsSaving(true)
    setError(null)
    try {
      await settingsApi.updateSettings({
        user_id: 'default_user',
        settings: {
          system: {
            theme: systemPrefs.theme,
            language: systemPrefs.language,
            font_size: systemPrefs.fontSize,
            sound_enabled: systemPrefs.soundEnabled,
            notifications_enabled: systemPrefs.notificationsEnabled,
            auto_save: systemPrefs.autoSave,
          },
          agent: {
            default_agent: agentSettings.defaultAgent,
            response_speed: agentSettings.responseSpeed,
            creativity: agentSettings.creativity,
            max_tokens: agentSettings.maxTokens,
            temperature: agentSettings.temperature,
            enable_voice: agentSettings.enableVoice,
            enable_memory: agentSettings.enableMemory,
          }
        }
      }, 'default_user')
      
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 2000)
    } catch (err: any) {
      setError(err.message || '保存失败')
      console.error('保存设置失败:', err)
    } finally {
      setIsSaving(false)
    }
  }

  // 渲染个人资料标签
  const renderProfileTab = () => (
    <div className="space-y-6">
      {/* 头像部分 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Camera size={20} className="text-brand-primary" />
          头像设置
        </h3>
        <div className="flex items-center gap-6">
          <div className="relative">
            <Avatar 
              src={userProfile.avatar} 
              alt={userProfile.name}
              size="xl"
            />
            <button className="absolute bottom-0 right-0 bg-brand-primary text-white rounded-full p-2 hover:bg-brand-primary/90 transition-colors">
              <Camera size={16} />
            </button>
          </div>
          <div className="flex-1">
            <p className="text-sm text-text-secondary mb-2">支持 JPG、PNG 格式，建议尺寸 400x400</p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Camera size={16} />
                上传新头像
              </Button>
              <Button variant="outline" size="sm">
                <Trash2 size={16} />
                删除头像
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* 基本信息 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <User size={20} className="text-brand-primary" />
          基本信息
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">姓名</label>
            <Input
              value={userProfile.name}
              onChange={(e) => setUserProfile({ ...userProfile, name: e.target.value })}
              placeholder="请输入姓名"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">邮箱</label>
            <Input
              type="email"
              value={userProfile.email}
              onChange={(e) => setUserProfile({ ...userProfile, email: e.target.value })}
              placeholder="请输入邮箱"
              icon={<Mail size={16} />}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">手机号</label>
            <Input
              value={userProfile.phone}
              onChange={(e) => setUserProfile({ ...userProfile, phone: e.target.value })}
              placeholder="请输入手机号"
              icon={<Phone size={16} />}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">所在地</label>
            <Input
              value={userProfile.location}
              onChange={(e) => setUserProfile({ ...userProfile, location: e.target.value })}
              placeholder="请输入所在地"
              icon={<MapPin size={16} />}
            />
          </div>
          <div className="col-span-2">
            <label className="block text-sm font-medium mb-2">个人简介</label>
            <textarea
              value={userProfile.bio}
              onChange={(e) => setUserProfile({ ...userProfile, bio: e.target.value })}
              placeholder="介绍一下自己..."
              rows={3}
              className="w-full px-4 py-2 bg-bg-tertiary border border-border-primary rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-primary/50 resize-none"
            />
          </div>
        </div>
      </Card>

      {/* 职业信息 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Briefcase size={20} className="text-brand-primary" />
          职业信息
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">公司</label>
            <Input
              value={userProfile.company}
              onChange={(e) => setUserProfile({ ...userProfile, company: e.target.value })}
              placeholder="请输入公司名称"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">职位</label>
            <Input
              value={userProfile.position}
              onChange={(e) => setUserProfile({ ...userProfile, position: e.target.value })}
              placeholder="请输入职位"
            />
          </div>
        </div>
      </Card>

      {/* 社交链接 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Globe size={20} className="text-brand-primary" />
          社交链接
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">个人网站</label>
            <Input
              value={userProfile.website}
              onChange={(e) => setUserProfile({ ...userProfile, website: e.target.value })}
              placeholder="https://example.com"
              icon={<Globe size={16} />}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">GitHub</label>
            <Input
              value={userProfile.github}
              onChange={(e) => setUserProfile({ ...userProfile, github: e.target.value })}
              placeholder="用户名"
              icon={<Github size={16} />}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Twitter</label>
            <Input
              value={userProfile.twitter}
              onChange={(e) => setUserProfile({ ...userProfile, twitter: e.target.value })}
              placeholder="@username"
              icon={<Twitter size={16} />}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">LinkedIn</label>
            <Input
              value={userProfile.linkedin}
              onChange={(e) => setUserProfile({ ...userProfile, linkedin: e.target.value })}
              placeholder="用户名"
              icon={<Linkedin size={16} />}
            />
          </div>
        </div>
      </Card>
    </div>
  )

  // 渲染系统偏好标签
  const renderPreferencesTab = () => (
    <div className="space-y-6">
      {/* 外观设置 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Palette size={20} className="text-brand-primary" />
          外观设置
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3">主题模式</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'light', label: '浅色', icon: <Sun size={20} /> },
                { value: 'dark', label: '深色', icon: <Moon size={20} /> },
                { value: 'auto', label: '自动', icon: <Monitor size={20} /> }
              ].map((theme) => (
                <button
                  key={theme.value}
                  onClick={() => setSystemPrefs({ ...systemPrefs, theme: theme.value as any })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    systemPrefs.theme === theme.value
                      ? 'border-brand-primary bg-brand-primary/10'
                      : 'border-border-primary hover:border-brand-primary/50'
                  }`}
                >
                  <div className="flex flex-col items-center gap-2">
                    {theme.icon}
                    <span className="text-sm font-medium">{theme.label}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3">字体大小</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'small', label: '小' },
                { value: 'medium', label: '中' },
                { value: 'large', label: '大' }
              ].map((size) => (
                <button
                  key={size.value}
                  onClick={() => setSystemPrefs({ ...systemPrefs, fontSize: size.value as any })}
                  className={`py-3 px-4 rounded-lg border-2 transition-all ${
                    systemPrefs.fontSize === size.value
                      ? 'border-brand-primary bg-brand-primary/10'
                      : 'border-border-primary hover:border-brand-primary/50'
                  }`}
                >
                  <span className={`font-medium ${
                    size.value === 'small' ? 'text-sm' :
                    size.value === 'medium' ? 'text-base' :
                    'text-lg'
                  }`}>{size.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* 语言和区域 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Globe size={20} className="text-brand-primary" />
          语言和区域
        </h3>
        <div>
          <label className="block text-sm font-medium mb-3">界面语言</label>
          <select
            value={systemPrefs.language}
            onChange={(e) => setSystemPrefs({ ...systemPrefs, language: e.target.value as any })}
            className="w-full px-4 py-2 bg-bg-tertiary border border-border-primary rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
          >
            <option value="zh-CN">简体中文</option>
            <option value="en-US">English (US)</option>
            <option value="ja-JP">日本語</option>
          </select>
        </div>
      </Card>

      {/* 通知和声音 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Bell size={20} className="text-brand-primary" />
          通知和声音
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell size={20} className="text-text-secondary" />
              <div>
                <p className="font-medium">桌面通知</p>
                <p className="text-sm text-text-secondary">接收系统通知和提醒</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemPrefs.notificationsEnabled}
                onChange={(e) => setSystemPrefs({ ...systemPrefs, notificationsEnabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-bg-tertiary peer-focus:ring-2 peer-focus:ring-brand-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-primary"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Volume2 size={20} className="text-text-secondary" />
              <div>
                <p className="font-medium">声音效果</p>
                <p className="text-sm text-text-secondary">播放系统音效</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemPrefs.soundEnabled}
                onChange={(e) => setSystemPrefs({ ...systemPrefs, soundEnabled: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-bg-tertiary peer-focus:ring-2 peer-focus:ring-brand-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-primary"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Save size={20} className="text-text-secondary" />
              <div>
                <p className="font-medium">自动保存</p>
                <p className="text-sm text-text-secondary">自动保存对话和设置</p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={systemPrefs.autoSave}
                onChange={(e) => setSystemPrefs({ ...systemPrefs, autoSave: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-bg-tertiary peer-focus:ring-2 peer-focus:ring-brand-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-primary"></div>
            </label>
          </div>
        </div>
      </Card>
    </div>
  )

  // 渲染Agent配置标签
  const renderAgentsTab = () => (
    <div className="space-y-6">
      {/* 默认Agent */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageSquare size={20} className="text-brand-primary" />
          默认Agent
        </h3>
        <div>
          <label className="block text-sm font-medium mb-3">启动时使用的Agent</label>
          <select
            value={agentSettings.defaultAgent}
            onChange={(e) => setAgentSettings({ ...agentSettings, defaultAgent: e.target.value })}
            className="w-full px-4 py-2 bg-bg-tertiary border border-border-primary rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-primary/50"
          >
            <option value="coordinator">Coordinator - 主控Agent</option>
            <option value="schedule">ScheduleAgent - 日程管理</option>
            <option value="task">TaskAgent - 任务管理</option>
            <option value="code">CodeAgent - 代码助手</option>
            <option value="learning">LearningAgent - 学习助手</option>
          </select>
        </div>
      </Card>

      {/* 响应设置 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap size={20} className="text-brand-primary" />
          响应设置
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3">响应速度</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'fast', label: '快速', desc: '更快但可能不够准确' },
                { value: 'balanced', label: '均衡', desc: '速度和质量平衡' },
                { value: 'quality', label: '质量', desc: '更准确但稍慢' }
              ].map((speed) => (
                <button
                  key={speed.value}
                  onClick={() => setAgentSettings({ ...agentSettings, responseSpeed: speed.value as any })}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    agentSettings.responseSpeed === speed.value
                      ? 'border-brand-primary bg-brand-primary/10'
                      : 'border-border-primary hover:border-brand-primary/50'
                  }`}
                >
                  <p className="font-medium mb-1">{speed.label}</p>
                  <p className="text-xs text-text-secondary">{speed.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium">创造力</label>
              <span className="text-sm text-brand-primary font-semibold">{agentSettings.creativity}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={agentSettings.creativity}
              onChange={(e) => setAgentSettings({ ...agentSettings, creativity: parseInt(e.target.value) })}
              className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer accent-brand-primary"
            />
            <p className="text-xs text-text-secondary mt-2">较高的创造力会产生更多样化的回答</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium">Temperature</label>
              <span className="text-sm text-brand-primary font-semibold">{agentSettings.temperature}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={agentSettings.temperature}
              onChange={(e) => setAgentSettings({ ...agentSettings, temperature: parseFloat(e.target.value) })}
              className="w-full h-2 bg-bg-tertiary rounded-lg appearance-none cursor-pointer accent-brand-primary"
            />
            <p className="text-xs text-text-secondary mt-2">控制回答的随机性，0=确定性，1=高随机性</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3">最大Token数</label>
            <Input
              type="number"
              value={agentSettings.maxTokens}
              onChange={(e) => setAgentSettings({ ...agentSettings, maxTokens: parseInt(e.target.value) })}
              placeholder="2000"
            />
            <p className="text-xs text-text-secondary mt-2">限制单次回答的最大长度</p>
          </div>
        </div>
      </Card>

      {/* 功能开关 */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Settings size={20} className="text-brand-primary" />
          功能开关
        </h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">语音输入</p>
              <p className="text-sm text-text-secondary">启用语音转文字功能</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={agentSettings.enableVoice}
                onChange={(e) => setAgentSettings({ ...agentSettings, enableVoice: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-bg-tertiary peer-focus:ring-2 peer-focus:ring-brand-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-primary"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">对话记忆</p>
              <p className="text-sm text-text-secondary">Agent记住之前的对话内容</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={agentSettings.enableMemory}
                onChange={(e) => setAgentSettings({ ...agentSettings, enableMemory: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-bg-tertiary peer-focus:ring-2 peer-focus:ring-brand-primary/50 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-primary"></div>
            </label>
          </div>
        </div>
      </Card>
    </div>
  )

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto p-6">
        {/* 页面标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">
            系统设置
          </h1>
          <p className="text-text-secondary">
            个性化配置您的Jarvis助手
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* 左侧导航 */}
          <div className="col-span-3">
            <Card className="p-4 sticky top-6">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all ${
                      activeTab === tab.id
                        ? 'bg-brand-primary/10 text-brand-primary'
                        : 'hover:bg-bg-tertiary text-text-secondary'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {tab.icon}
                      <span className="font-medium">{tab.name}</span>
                    </div>
                    {tab.badge && (
                      <Badge variant="error" size="sm">
                        {tab.badge}
                      </Badge>
                    )}
                  </button>
                ))}
              </nav>
            </Card>
          </div>

          {/* 右侧内容 */}
          <div className="col-span-9">
            {activeTab === 'profile' && renderProfileTab()}
            {activeTab === 'preferences' && renderPreferencesTab()}
            {activeTab === 'agents' && renderAgentsTab()}
            
            {/* 其他标签页占位 */}
            {!['profile', 'preferences', 'agents'].includes(activeTab) && (
              <Card className="p-12">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-brand-primary/10 rounded-full mb-4">
                    <Settings size={32} className="text-brand-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">功能开发中</h3>
                  <p className="text-text-secondary">该功能正在开发中，敬请期待...</p>
                </div>
              </Card>
            )}

            {/* 保存按钮 */}
            {['profile', 'preferences', 'agents'].includes(activeTab) && (
              <div className="mt-6 flex items-center justify-end gap-3">
                <Button variant="outline" onClick={() => window.location.reload()}>
                  <X size={16} />
                  取消
                </Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                      保存中...
                    </>
                  ) : saveSuccess ? (
                    <>
                      <Check size={16} />
                      保存成功
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      保存设置
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}

export default SettingsPage
