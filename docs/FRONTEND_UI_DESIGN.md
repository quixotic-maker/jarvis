# Jarvis V3 - 完整前端UI设计规范

> **设计理念**: 现代、优雅、高效、智能

---

## 🎨 一、设计系统

### 1.1 配色方案

```css
/* 主题色 - 深色模式 */
:root {
  /* 背景色 */
  --bg-primary: #0f172a;        /* 主背景 */
  --bg-secondary: #1e293b;      /* 次级背景 */
  --bg-tertiary: #334155;       /* 卡片背景 */
  --bg-hover: #475569;          /* 悬停态 */
  
  /* 文字色 */
  --text-primary: #f1f5f9;      /* 主文字 */
  --text-secondary: #cbd5e1;    /* 次级文字 */
  --text-tertiary: #94a3b8;     /* 辅助文字 */
  --text-disabled: #64748b;     /* 禁用文字 */
  
  /* 品牌色 */
  --brand-primary: #10b981;     /* 翠绿 - Jarvis主色 */
  --brand-secondary: #06b6d4;   /* 青色 - 强调色 */
  --brand-accent: #8b5cf6;      /* 紫色 - 点缀色 */
  
  /* 功能色 */
  --success: #10b981;           /* 成功 */
  --warning: #f59e0b;           /* 警告 */
  --error: #ef4444;             /* 错误 */
  --info: #3b82f6;              /* 信息 */
  
  /* 渐变色 */
  --gradient-primary: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
  --gradient-secondary: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
  --gradient-warm: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  
  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
  --shadow-glow: 0 0 20px rgba(16, 185, 129, 0.3);
  
  /* 圆角 */
  --radius-sm: 0.25rem;         /* 4px */
  --radius-md: 0.5rem;          /* 8px */
  --radius-lg: 0.75rem;         /* 12px */
  --radius-xl: 1rem;            /* 16px */
  --radius-2xl: 1.5rem;         /* 24px */
  --radius-full: 9999px;        /* 完全圆角 */
}
```

### 1.2 字体系统

```css
:root {
  /* 中文字体栈 */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", 
               "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
               "Helvetica Neue", Helvetica, Arial, sans-serif;
  
  /* 等宽字体（代码） */
  --font-mono: "SF Mono", "Fira Code", "Consolas", 
               "Liberation Mono", "Courier New", monospace;
  
  /* 字号 */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  
  /* 字重 */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

### 1.3 间距系统

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
}
```

### 1.4 动画系统

```css
/* 缓动函数 */
:root {
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  
  /* 持续时间 */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
}

/* 常用动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(10px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## 🎯 二、核心组件设计

### 2.1 主布局组件

```typescript
// MainLayout.tsx
<div className="flex h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
  {/* 侧边栏 */}
  <Sidebar />
  
  {/* 主内容区 */}
  <main className="flex-1 flex flex-col">
    {/* 顶部导航栏 */}
    <TopNav />
    
    {/* 内容区域 */}
    <div className="flex-1 overflow-hidden flex">
      {/* 主区域 */}
      <div className="flex-1 overflow-y-auto">
        {children}
      </div>
      
      {/* 右侧可视化面板（可折叠） */}
      <VisualizationPanel />
    </div>
  </main>
</div>
```

#### 侧边栏设计

```
┌─────────────────────────┐
│                         │
│  ┌─────────────────┐    │
│  │   🤖 Jarvis     │    │
│  └─────────────────┘    │
│                         │
│  ───────────────────    │
│                         │
│  🏠 首页            ●   │  ←─ 激活态
│  💬 对话                │
│  🧠 知识脑图            │
│  👤 我的画像            │
│  📈 成长轨迹            │
│  🔬 研究工作台          │
│                         │
│  ───────────────────    │
│                         │
│  🤖 Agents              │
│  📋 办公效率    (7)     │
│  💻 技术开发    (3)     │
│  📚 学习成长    (2)     │
│  🌍 生活服务    (9)     │
│  ⭐ 高级AI      (4)     │
│                         │
│  ───────────────────    │
│                         │
│  🔧 MCP工具箱           │
│  ⚙️ 设置                │
│                         │
│  ─────────────── ──     │
│                         │
│  👤 刘同学              │
│  📊 等级 Lv.12          │
│  ⭐ 1,234 经验          │
│                         │
└─────────────────────────┘
```

#### 顶部导航栏设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  🤖 Jarvis                    [新对话+]  [🔍]  [🔔 3]  [⚙️]  [👤 刘同学]  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  💡 提示: 试试说 "嘿Jarvis" 唤醒语音助手                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 对话组件设计

#### 消息气泡组件

```tsx
// MessageBubble.tsx
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  agentUsed?: string;
  timestamp: Date;
}

// 设计规范
const MessageBubble = ({ role, content, isStreaming, agentUsed, timestamp }: MessageBubbleProps) => (
  <div className={`flex gap-4 ${role === 'user' ? 'flex-row-reverse' : ''} 
                   animate-slideUp`}>
    {/* 头像 */}
    <div className={`w-10 h-10 rounded-full flex items-center justify-center
                     ${role === 'user' 
                       ? 'bg-gradient-to-br from-blue-500 to-purple-600' 
                       : 'bg-gradient-to-br from-emerald-500 to-teal-600'}
                     shadow-lg hover:scale-110 transition-transform`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    
    {/* 消息内容 */}
    <div className={`max-w-[70%] ${role === 'user' ? 'text-right' : ''}`}>
      {/* 气泡 */}
      <div className={`inline-block px-5 py-3 rounded-2xl shadow-md
                       ${role === 'user'
                         ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white'
                         : 'bg-slate-800 text-slate-100 border border-slate-700'}
                       backdrop-blur-sm hover:shadow-lg transition-shadow`}>
        {/* Markdown渲染 */}
        <StreamingMarkdown content={content} isStreaming={isStreaming} />
      </div>
      
      {/* 元信息 */}
      <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
        <span>{formatTime(timestamp)}</span>
        {agentUsed && (
          <span className="px-2 py-1 bg-slate-800 rounded-full text-emerald-400
                         flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            {agentUsed}
          </span>
        )}
      </div>
    </div>
  </div>
);
```

#### 输入框组件

```tsx
// InputBox.tsx
<div className="sticky bottom-0 p-6 bg-gradient-to-t from-slate-900 via-slate-900/95 to-transparent
                backdrop-blur-lg border-t border-slate-800">
  {/* 快捷操作栏 */}
  <div className="flex items-center gap-2 mb-3">
    <QuickActionButton icon={Calendar} label="日程" />
    <QuickActionButton icon={Bell} label="提醒" />
    <QuickActionButton icon={Code} label="代码" />
    <QuickActionButton icon={FileText} label="笔记" />
    <QuickActionButton icon={Sparkles} label="更多" />
  </div>
  
  {/* 输入区域 */}
  <div className="relative flex items-end gap-3">
    {/* 左侧工具按钮 */}
    <div className="flex gap-2">
      <button className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700
                       text-slate-400 hover:text-white transition-colors">
        <Paperclip className="w-5 h-5" />
      </button>
      <button className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700
                       text-slate-400 hover:text-white transition-colors"
              onClick={toggleVoice}>
        {isListening ? <MicOff className="w-5 h-5 text-red-400" /> 
                     : <Mic className="w-5 h-5" />}
      </button>
    </div>
    
    {/* 文本输入框 */}
    <div className="flex-1 relative">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入消息... (Shift+Enter 换行)"
        className="w-full px-4 py-3 bg-slate-800 border border-slate-700
                   rounded-xl text-slate-100 placeholder-slate-500
                   focus:outline-none focus:ring-2 focus:ring-emerald-500
                   focus:border-transparent resize-none max-h-32
                   transition-all"
        rows={1}
      />
      
      {/* 字符计数 */}
      {input.length > 0 && (
        <div className="absolute bottom-2 right-2 text-xs text-slate-500">
          {input.length} / 2000
        </div>
      )}
    </div>
    
    {/* 发送按钮 */}
    <button
      onClick={handleSend}
      disabled={!input.trim() || isStreaming}
      className="p-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600
                 text-white shadow-lg hover:shadow-emerald-500/50
                 disabled:opacity-50 disabled:cursor-not-allowed
                 hover:scale-105 active:scale-95 transition-all">
      {isStreaming ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <Send className="w-5 h-5" />
      )}
    </button>
  </div>
  
  {/* 语音识别提示 */}
  {isListening && (
    <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg
                    flex items-center gap-2 animate-pulse">
      <div className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
      <span className="text-sm text-red-400">正在聆听...</span>
    </div>
  )}
</div>
```

### 2.3 卡片组件设计

#### 基础卡片

```tsx
// Card.tsx
interface CardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ElementType;
  actions?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

const Card = ({ title, subtitle, icon: Icon, actions, className, children }: CardProps) => (
  <div className={`bg-slate-800/50 backdrop-blur-sm border border-slate-700
                   rounded-2xl p-6 shadow-xl hover:shadow-2xl
                   hover:border-emerald-500/30 transition-all
                   ${className}`}>
    {/* 卡片头部 */}
    {(title || actions) && (
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className="p-2 bg-emerald-500/10 rounded-lg">
              <Icon className="w-5 h-5 text-emerald-400" />
            </div>
          )}
          <div>
            {title && <h3 className="text-lg font-semibold text-slate-100">{title}</h3>}
            {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
          </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    )}
    
    {/* 卡片内容 */}
    <div className="text-slate-300">
      {children}
    </div>
  </div>
);
```

#### Agent卡片

```tsx
// AgentCard.tsx
<div className="group relative overflow-hidden bg-gradient-to-br from-slate-800 to-slate-900
                border border-slate-700 rounded-2xl p-6 cursor-pointer
                hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20
                transition-all duration-300">
  {/* 背景装饰 */}
  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full
                  blur-3xl group-hover:bg-emerald-500/10 transition-all" />
  
  {/* Agent图标 */}
  <div className="relative w-16 h-16 mb-4 mx-auto">
    <div className="absolute inset-0 bg-gradient-to-br from-emerald-400 to-teal-500
                    rounded-2xl rotate-3 group-hover:rotate-6 transition-transform" />
    <div className="relative w-full h-full bg-slate-900 rounded-2xl
                    flex items-center justify-center">
      <Icon className="w-8 h-8 text-emerald-400" />
    </div>
  </div>
  
  {/* Agent信息 */}
  <h3 className="text-lg font-semibold text-slate-100 text-center mb-1">
    {agent.name}
  </h3>
  <p className="text-sm text-slate-500 text-center mb-4">
    {agent.description}
  </p>
  
  {/* 使用统计 */}
  <div className="flex items-center justify-between text-xs text-slate-600">
    <span>使用 {agent.usageCount} 次</span>
    <span className="flex items-center gap-1">
      <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
      收藏
    </span>
  </div>
  
  {/* 悬浮操作按钮 */}
  <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-slate-900
                  opacity-0 group-hover:opacity-100 transition-opacity">
    <button className="w-full py-2 bg-emerald-500 hover:bg-emerald-600
                     text-white rounded-lg transition-colors">
      开始使用
    </button>
  </div>
</div>
```

### 2.4 可视化组件设计

#### 雷达图组件

```tsx
// RadarChart.tsx
<div className="relative w-full h-64">
  <svg viewBox="0 0 200 200" className="w-full h-full">
    {/* 网格线 */}
    <g className="grid" opacity="0.2">
      {[20, 40, 60, 80, 100].map(r => (
        <polygon
          key={r}
          points={dimensions.map((_, i) => {
            const angle = (Math.PI * 2 * i) / dimensions.length - Math.PI / 2;
            return `${100 + r * Math.cos(angle)},${100 + r * Math.sin(angle)}`;
          }).join(' ')}
          fill="none"
          stroke="currentColor"
          className="text-slate-700"
        />
      ))}
    </g>
    
    {/* 轴线 */}
    {dimensions.map((dim, i) => {
      const angle = (Math.PI * 2 * i) / dimensions.length - Math.PI / 2;
      const x = 100 + 100 * Math.cos(angle);
      const y = 100 + 100 * Math.sin(angle);
      return (
        <g key={dim.name}>
          <line
            x1="100" y1="100"
            x2={x} y2={y}
            stroke="currentColor"
            className="text-slate-700"
            strokeWidth="0.5"
          />
          <text
            x={100 + 120 * Math.cos(angle)}
            y={100 + 120 * Math.sin(angle)}
            className="text-slate-400 text-xs"
            textAnchor="middle">
            {dim.name}
          </text>
        </g>
      );
    })}
    
    {/* 数据区域 */}
    <polygon
      points={data.map((value, i) => {
        const angle = (Math.PI * 2 * i) / data.length - Math.PI / 2;
        const r = value;
        return `${100 + r * Math.cos(angle)},${100 + r * Math.sin(angle)}`;
      }).join(' ')}
      fill="url(#radarGradient)"
      stroke="currentColor"
      className="text-emerald-500"
      strokeWidth="2"
    />
    
    {/* 渐变定义 */}
    <defs>
      <radialGradient id="radarGradient">
        <stop offset="0%" stopColor="rgb(16, 185, 129)" stopOpacity="0.4" />
        <stop offset="100%" stopColor="rgb(16, 185, 129)" stopOpacity="0.1" />
      </radialGradient>
    </defs>
  </svg>
</div>
```

#### 3D知识脑图组件

```tsx
// BrainMap3D.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';

const BrainMap3D = ({ nodes, edges }) => (
  <div className="w-full h-full bg-gradient-to-b from-slate-900 to-slate-800 rounded-2xl overflow-hidden">
    <Canvas camera={{ position: [0, 0, 50], fov: 60 }}>
      {/* 环境光 */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      {/* 相机控制 */}
      <OrbitControls enableDamping dampingFactor={0.05} />
      
      {/* 节点 */}
      {nodes.map(node => (
        <group key={node.id} position={node.position}>
          {/* 球体 */}
          <mesh>
            <sphereGeometry args={[node.size, 32, 32]} />
            <meshStandardMaterial
              color={node.color}
              emissive={node.color}
              emissiveIntensity={0.3}
            />
          </mesh>
          
          {/* 文字标签 */}
          <Text
            position={[0, node.size + 1, 0]}
            fontSize={1}
            color="white"
            anchorX="center"
            anchorY="middle">
            {node.label}
          </Text>
          
          {/* 发光效果 */}
          <mesh scale={[1.1, 1.1, 1.1]}>
            <sphereGeometry args={[node.size, 32, 32]} />
            <meshBasicMaterial
              color={node.color}
              transparent
              opacity={0.1}
            />
          </mesh>
        </group>
      ))}
      
      {/* 连接线 */}
      {edges.map(edge => {
        const start = nodes.find(n => n.id === edge.source).position;
        const end = nodes.find(n => n.id === edge.target).position;
        return (
          <Line
            key={`${edge.source}-${edge.target}`}
            points={[start, end]}
            color="#10b981"
            lineWidth={edge.weight}
            transparent
            opacity={0.4}
          />
        );
      })}
    </Canvas>
    
    {/* 控制面板 */}
    <div className="absolute top-4 right-4 space-y-2">
      <button className="px-3 py-2 bg-slate-800/80 backdrop-blur-sm
                       text-slate-300 rounded-lg hover:bg-slate-700 transition-colors">
        重置视角
      </button>
      <button className="px-3 py-2 bg-slate-800/80 backdrop-blur-sm
                       text-slate-300 rounded-lg hover:bg-slate-700 transition-colors">
        自动旋转
      </button>
    </div>
  </div>
);
```

---

## 🎭 三、交互动效设计

### 3.1 页面过渡

```tsx
// PageTransition.tsx
import { motion, AnimatePresence } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  enter: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const PageTransition = ({ children }) => (
  <AnimatePresence mode="wait">
    <motion.div
      initial="initial"
      animate="enter"
      exit="exit"
      variants={pageVariants}
      transition={{ duration: 0.3, ease: 'easeInOut' }}>
      {children}
    </motion.div>
  </AnimatePresence>
);
```

### 3.2 加载动画

```tsx
// LoadingSpinner.tsx
<div className="flex items-center justify-center">
  <div className="relative w-12 h-12">
    {/* 外圈 */}
    <div className="absolute inset-0 border-4 border-emerald-500/20 rounded-full" />
    
    {/* 旋转圈 */}
    <div className="absolute inset-0 border-4 border-transparent
                    border-t-emerald-500 rounded-full animate-spin" />
    
    {/* 中心点 */}
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
    </div>
  </div>
</div>
```

### 3.3 悬浮效果

```css
/* 卡片悬浮 */
.card-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-hover:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.1),
              0 10px 10px -5px rgba(16, 185, 129, 0.04);
}

/* 按钮悬浮 */
.button-hover {
  transition: all 0.2s ease;
}

.button-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.3);
}

.button-hover:active {
  transform: translateY(0);
}
```

---

## 📱 四、响应式设计

### 4.1 断点系统

```css
/* 移动端优先 */
:root {
  /* sm: 640px */
  --screen-sm: 640px;
  /* md: 768px */
  --screen-md: 768px;
  /* lg: 1024px */
  --screen-lg: 1024px;
  /* xl: 1280px */
  --screen-xl: 1280px;
  /* 2xl: 1536px */
  --screen-2xl: 1536px;
}
```

### 4.2 布局适配

```tsx
// 侧边栏在移动端自动隐藏/抽屉式
<div className="flex h-screen">
  {/* 侧边栏 - 桌面端固定，移动端抽屉 */}
  <aside className="hidden lg:block w-64 border-r border-slate-800">
    <Sidebar />
  </aside>
  
  {/* 移动端菜单按钮 */}
  <button className="lg:hidden fixed top-4 left-4 z-50"
          onClick={() => setMobileMenuOpen(true)}>
    <Menu className="w-6 h-6" />
  </button>
  
  {/* 主内容区 */}
  <main className="flex-1">
    {children}
  </main>
</div>
```

---

## ♿ 五、可访问性设计

### 5.1 键盘导航

```tsx
// 所有交互元素支持键盘操作
<button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
  tabIndex={0}
  aria-label="执行操作">
  操作
</button>
```

### 5.2 ARIA标签

```tsx
// 使用语义化ARIA标签
<nav aria-label="主导航">
  <button aria-expanded={isOpen} aria-controls="menu">
    菜单
  </button>
  <div id="menu" role="menu" aria-hidden={!isOpen}>
    {/* 菜单项 */}
  </div>
</nav>
```

---

## 🎨 六、主题定制

### 6.1 主题切换

```tsx
// ThemeProvider.tsx
const themes = {
  dark: { /* 深色主题变量 */ },
  light: { /* 浅色主题变量 */ },
  emerald: { /* 翠绿主题变量 */ },
  purple: { /* 紫色主题变量 */ }
};

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark');
  
  useEffect(() => {
    Object.entries(themes[theme]).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
  }, [theme]);
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

---

*设计规范版本: V3.0*
*最后更新: 2026-01-15*
