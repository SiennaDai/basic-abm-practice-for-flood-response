"""
基础类型定义
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any

class AgentType(Enum):
    """智能体类型枚举"""
    COMMAND_CENTER = "市防指"
    WATER_BUREAU = "水务局"
    TRAFFIC_POLICE = "交管局"
    RESCUE_TEAM = "抢险队"
    INSPECTOR = "巡查员"
    INFO_PLATFORM = "信息平台"

class IncidentType(Enum):
    """事件类型枚举"""
    ROAD_FLOODING = "道路积水"
    EMBANKMENT_DANGER = "堤防险情"
    COMMUNITY_FLOODING = "社区渍水"
    PEOPLE_TRAPPED = "人员被困"
    TRAFFIC_JAM = "交通拥堵"
    
    @classmethod
    def from_string(cls, type_str: str):
        """从字符串安全转换为枚举"""
        type_mapping = {
            "道路积水": cls.ROAD_FLOODING,
            "堤防险情": cls.EMBANKMENT_DANGER,
            "社区渍水": cls.COMMUNITY_FLOODING,
            "人员被困": cls.PEOPLE_TRAPPED,
            "交通拥堵": cls.TRAFFIC_JAM,
            "积水": cls.ROAD_FLOODING,  # 简写
            "险情": cls.EMBANKMENT_DANGER,  # 简写
            "渍水": cls.COMMUNITY_FLOODING,  # 简写
            "被困": cls.PEOPLE_TRAPPED,  # 简写
        }
        
        if type_str in type_mapping:
            return type_mapping[type_str]
        
        # 尝试直接转换
        try:
            return cls(type_str)
        except ValueError:
            return cls.ROAD_FLOODING  # 默认类型

@dataclass
class Task:
    """任务类"""
    id: int
    incident_type: IncidentType
    location: str
    urgency: float  # 0-1，紧急程度
    create_time: int
    assigned_to: Optional[str] = None
    start_time: Optional[int] = None
    completion_time: Optional[int] = None
    status: str = "pending"  # pending, assigned, in_progress, completed

class BaseAgent:
    """智能体基类"""
    def __init__(self, agent_id: int, agent_type: AgentType):
        self.id = agent_id
        self.type = agent_type
        self.inbox: List[Dict] = []  # 收件箱
        self.outbox: List[Dict] = []  # 发件箱
        self.tasks: List[Task] = []  # 当前任务
        self.response_times: List[int] = []  # 响应时间记录
        self.busy_until: int = 0  # 忙碌到哪个时间步
        self.metrics = {
            "tasks_completed": 0,
            "avg_response_time": 0,
            "utilization": 0
        }
        
    def send_message(self, to_agent, message: Dict):
        """发送消息"""
        message["from"] = f"{self.type.value}_{self.id}"
        message["timestamp"] = self._current_time if hasattr(self, '_current_time') else 0
        self.outbox.append(message)
        to_agent.receive_message(message)
        
    def receive_message(self, message: Dict):
        """接收消息"""
        self.inbox.append(message)
        
    def process_inbox(self, current_step: int):
        """处理收件箱（由子类实现）"""
        raise NotImplementedError
        
    def update_metrics(self, task_completed=False, response_time=None):
        """更新指标"""
        if task_completed:
            self.metrics["tasks_completed"] += 1
        if response_time is not None:
            self.response_times.append(response_time)
            if self.response_times:
                self.metrics["avg_response_time"] = sum(self.response_times) / len(self.response_times)

    def __str__(self):
        return f"{self.type.value}_{self.id}"
