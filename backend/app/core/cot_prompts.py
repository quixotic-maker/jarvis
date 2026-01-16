"""
Chain-of-Thought (CoT) 提示工具
帮助Agent进行结构化思考和推理
"""
from typing import List, Dict, Any
from enum import Enum


class CoTPattern(str, Enum):
    """CoT模式类型"""
    STEP_BY_STEP = "step_by_step"  # 逐步推理
    PROBLEM_SOLVING = "problem_solving"  # 问题解决
    ANALYSIS = "analysis"  # 分析思考
    DECISION_MAKING = "decision_making"  # 决策制定
    CREATIVE = "creative"  # 创意思考


class ChainOfThoughtBuilder:
    """思维链构建器"""
    
    @staticmethod
    def step_by_step(task_description: str) -> str:
        """
        逐步推理模式
        适用于: 计算、推导、分步骤任务
        """
        return f"""请按照以下步骤思考：

任务: {task_description}

让我们一步步来思考:
1. 首先，理解问题的核心是什么
2. 然后，列出解决问题需要的信息
3. 接下来，制定解决方案
4. 最后，验证结果是否合理

请显示你的思考过程，然后给出最终答案。"""
    
    @staticmethod
    def problem_solving(problem: str, constraints: List[str] = None) -> str:
        """
        问题解决模式
        适用于: 复杂问题、需要权衡的决策
        """
        constraints_text = ""
        if constraints:
            constraints_text = "\n\n约束条件:\n" + "\n".join(f"- {c}" for c in constraints)
        
        return f"""问题: {problem}{constraints_text}

请使用以下框架分析:

## 1. 问题分析
- 核心问题是什么？
- 涉及哪些关键因素？

## 2. 可能的解决方案
- 方案A: ...（优缺点）
- 方案B: ...（优缺点）
- 方案C: ...（优缺点）

## 3. 权衡与选择
- 基于约束条件，哪个方案最优？
- 理由是什么？

## 4. 最终建议
给出具体的行动建议。"""
    
    @staticmethod
    def analysis(topic: str, aspects: List[str] = None) -> str:
        """
        分析思考模式
        适用于: 数据分析、情况评估、趋势预测
        """
        aspects_text = ""
        if aspects:
            aspects_text = "\n\n分析维度:\n" + "\n".join(f"- {a}" for a in aspects)
        
        return f"""分析主题: {topic}{aspects_text}

请进行结构化分析:

## 1. 现状描述
当前情况是怎样的？

## 2. 关键发现
- 发现1: ...（支持数据/依据）
- 发现2: ...（支持数据/依据）
- 发现3: ...（支持数据/依据）

## 3. 趋势预测
基于当前情况，未来可能的发展方向？

## 4. 建议与结论
基于分析，给出actionable的建议。"""
    
    @staticmethod
    def decision_making(decision: str, options: List[Dict[str, Any]]) -> str:
        """
        决策制定模式
        适用于: 多选项决策、优先级排序
        """
        options_text = "\n\n可选项:\n"
        for i, opt in enumerate(options, 1):
            options_text += f"{i}. {opt.get('name', f'选项{i}')}\n"
            if 'pros' in opt:
                options_text += f"   优点: {', '.join(opt['pros'])}\n"
            if 'cons' in opt:
                options_text += f"   缺点: {', '.join(opt['cons'])}\n"
        
        return f"""决策: {decision}{options_text}

请使用决策矩阵思考:

## 1. 评估标准
定义评估各选项的关键标准（如成本、时间、质量、风险）

## 2. 选项评分
为每个选项在各标准上打分（1-10分）

## 3. 权重分配
为各评估标准分配权重（总和100%）

## 4. 综合评估
计算加权总分，选出最优方案

## 5. 风险考量
最优方案可能的风险是什么？如何缓解？

## 6. 最终决策
基于以上分析，给出明确的决策建议和理由。"""
    
    @staticmethod
    def creative(challenge: str, constraints: List[str] = None) -> str:
        """
        创意思考模式
        适用于: 头脑风暴、创新方案、设计思维
        """
        constraints_text = ""
        if constraints:
            constraints_text = "\n\n限制条件:\n" + "\n".join(f"- {c}" for c in constraints)
        
        return f"""创意挑战: {challenge}{constraints_text}

使用发散-收敛思维:

## 1. 发散思考（不评判）
尽可能多地产生创意点子:
- 想法1: ...
- 想法2: ...
- 想法3: ...
- 想法4: ...
- 想法5: ...

## 2. 分类整理
将想法按主题/类型分组

## 3. 收敛评估
基于限制条件，筛选最有潜力的3个想法

## 4. 深化设计
选择最佳想法，详细阐述:
- 核心概念
- 实现方式
- 预期效果
- 潜在问题

## 5. 优化方案
如何让这个想法更好？"""
    
    @staticmethod
    def get_cot_prompt(pattern: CoTPattern, **kwargs) -> str:
        """
        根据模式获取CoT提示
        
        Args:
            pattern: CoT模式
            **kwargs: 模式特定参数
        
        Returns:
            CoT提示文本
        """
        if pattern == CoTPattern.STEP_BY_STEP:
            return ChainOfThoughtBuilder.step_by_step(
                kwargs.get('task_description', '完成任务')
            )
        elif pattern == CoTPattern.PROBLEM_SOLVING:
            return ChainOfThoughtBuilder.problem_solving(
                kwargs.get('problem', '解决问题'),
                kwargs.get('constraints')
            )
        elif pattern == CoTPattern.ANALYSIS:
            return ChainOfThoughtBuilder.analysis(
                kwargs.get('topic', '进行分析'),
                kwargs.get('aspects')
            )
        elif pattern == CoTPattern.DECISION_MAKING:
            return ChainOfThoughtBuilder.decision_making(
                kwargs.get('decision', '做出决策'),
                kwargs.get('options', [])
            )
        elif pattern == CoTPattern.CREATIVE:
            return ChainOfThoughtBuilder.creative(
                kwargs.get('challenge', '创新思考'),
                kwargs.get('constraints')
            )
        else:
            raise ValueError(f"不支持的CoT模式: {pattern}")


# CoT提示示例
COT_EXAMPLES = {
    "calculation": {
        "pattern": CoTPattern.STEP_BY_STEP,
        "example": """
问题: 一个商店原价100元的商品打8折，再满200减30，买3件最终多少钱？

思考过程:
步骤1: 计算打折后单价
100 × 0.8 = 80元

步骤2: 计算3件总价
80 × 3 = 240元

步骤3: 检查是否满足满减条件
240 > 200，可以减30

步骤4: 计算最终价格
240 - 30 = 210元

最终答案: 210元
"""
    },
    "scheduling": {
        "pattern": CoTPattern.PROBLEM_SOLVING,
        "example": """
问题: 需要在周五前完成3个任务，但每天只有4小时工作时间

分析:
1. 任务A: 需要6小时（优先级高）
2. 任务B: 需要4小时（优先级中）
3. 任务C: 需要5小时（优先级低）

解决方案:
方案1: 按优先级顺序
- 周一-周二: 任务A（6小时）
- 周三: 任务B（4小时）
- 周四: 任务C（4小时，周五再完成1小时）

方案2: 时间最优
- 重新评估任务C的必要性
- 考虑是否可以延期或简化

最终建议: 采用方案1，同时与利益相关方沟通任务C可能需要延期1小时。
"""
    },
    "data_analysis": {
        "pattern": CoTPattern.ANALYSIS,
        "example": """
分析: 销售数据显示Q4比Q3下降15%

1. 现状:
- Q3销售额: 100万
- Q4销售额: 85万
- 下降幅度: 15%

2. 关键发现:
- 发现1: 新客户获取成本上升30%
- 发现2: 老客户复购率下降20%
- 发现3: 竞争对手推出促销活动

3. 趋势预测:
如果不采取措施，Q1可能继续下滑

4. 建议:
- 短期: 推出客户回馈活动
- 中期: 优化获客渠道
- 长期: 提升产品竞争力
"""
    }
}


def get_example(task_type: str) -> str:
    """获取CoT示例"""
    example_data = COT_EXAMPLES.get(task_type)
    if example_data:
        return example_data['example']
    return ""
