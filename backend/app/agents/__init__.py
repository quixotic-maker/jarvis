"""Agent模块"""
from app.agents.coordinator_agent import CoordinatorAgent
from app.agents.schedule_agent import ScheduleAgent
from app.agents.info_agent import InfoRetrievalAgent
from app.agents.email_agent import EmailAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.news_agent import NewsAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.file_agent import FileAgent
from app.agents.calculation_agent import CalculationAgent
from app.agents.translation_agent import TranslationAgent
from app.agents.summary_agent import SummaryAgent
from app.agents.task_agent import TaskAgent
from app.agents.note_agent import NoteAgent
from app.agents.code_agent import CodeAgent
from app.agents.meeting_agent import MeetingAgent
from app.agents.learning_agent import LearningAgent
from app.agents.travel_agent import TravelAgent
from app.agents.health_agent import HealthAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.data_analysis_agent import DataAnalysisAgent
from app.agents.contact_agent import ContactAgent

# 高级Agent
from app.agents.knowledge_graph_agent import KnowledgeGraphAgent
from app.agents.rag_agent import RAGAgent
from app.agents.agentic_rag_agent import AgenticRAGAgent
from app.agents.mcp_agent import MCPAgent

# Agent注册表
AGENT_REGISTRY = {
    "Coordinator": CoordinatorAgent,
    "ScheduleAgent": ScheduleAgent,
    "InfoRetrievalAgent": InfoRetrievalAgent,
    "EmailAgent": EmailAgent,
    "WeatherAgent": WeatherAgent,
    "NewsAgent": NewsAgent,
    "ReminderAgent": ReminderAgent,
    "FileAgent": FileAgent,
    "CalculationAgent": CalculationAgent,
    "TranslationAgent": TranslationAgent,
    "SummaryAgent": SummaryAgent,
    "TaskAgent": TaskAgent,
    "NoteAgent": NoteAgent,
    "CodeAgent": CodeAgent,
    "MeetingAgent": MeetingAgent,
    "LearningAgent": LearningAgent,
    "TravelAgent": TravelAgent,
    "HealthAgent": HealthAgent,
    "RecommendationAgent": RecommendationAgent,
    "DataAnalysisAgent": DataAnalysisAgent,
    "ContactAgent": ContactAgent,
    # 高级Agent
    "KnowledgeGraphAgent": KnowledgeGraphAgent,
    "RAGAgent": RAGAgent,
    "AgenticRAGAgent": AgenticRAGAgent,
    "MCPAgent": MCPAgent,
}


def get_agent(agent_name: str):
    """获取Agent实例"""
    agent_class = AGENT_REGISTRY.get(agent_name)
    if agent_class:
        return agent_class()
    return None
