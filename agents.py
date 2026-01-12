"""
智能体实现
"""

from base_types import *
import random
import time

class CommandCenter(BaseAgent):
    """市防汛抗旱指挥部"""
    def __init__(self, agent_id: int):
        super().__init__(agent_id, AgentType.COMMAND_CENTER)
        self.command_authority = 0.9
        self.info_capacity = 5
        self.response_level = None
        self.direct_command_enabled = True
        self.emergency_tasks: List[Task] = []
        
    def issue_response_level(self, rainfall_intensity: float, current_step: int) -> str:
        """发布响应等级"""
        if rainfall_intensity > 80:
            level = "Ⅰ级"
        elif rainfall_intensity > 60:
            level = "Ⅱ级"
        elif rainfall_intensity > 40:
            level = "Ⅲ级"
        else:
            level = "Ⅳ级"
            
        self.response_level = level
        print(f"[{current_step}] 市防指发布{level}应急响应")
        return level
        
    def direct_dispatch(self, rescue_team, task: Task, current_step: int):
        """直接调度抢险队"""
        if self.direct_command_enabled:
            print(f"[{current_step}] 市防指直接调度{rescue_team.type.value}_{rescue_team.id}执行{task.incident_type.value}")
            rescue_team.receive_message({
                "type": "direct_command",
                "task": task,
                "urgency": "high"
            })
            task.assigned_to = f"{rescue_team.type.value}_{rescue_team.id}"
            task.start_time = current_step
            task.status = "assigned"
            
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        processed = 0
        for msg in self.inbox[:self.info_capacity]:
            if msg.get("type") in ["emergency_report", "hierarchical_report", "incident_report"]:
                # 安全获取事件类型
                incident_type_str = msg.get("incident_type", "道路积水")
                incident_type = IncidentType.from_string(incident_type_str)
                
                task = Task(
                    id=len(self.emergency_tasks) + 1,
                    incident_type=incident_type,
                    location=msg.get("location", "未知区域"),
                    urgency=msg.get("urgency", 0.8),
                    create_time=current_step
                )
                self.emergency_tasks.append(task)
                print(f"[{current_step}] 市防指收到报告：{task.incident_type.value}于{task.location}")
            processed += 1
            
        self.inbox = self.inbox[processed:]

class WaterBureau(BaseAgent):
    """水务局"""
    def __init__(self, agent_id: int):
        super().__init__(agent_id, AgentType.WATER_BUREAU)
        self.pump_capacity = 10000
        self.mobile_pumps = 10
        self.available_pumps = 10
        self.drainage_tasks: List[Task] = []
        
    def schedule_drainage(self, water_depth: float, location: str, current_step: int) -> int:
        """调度排水资源"""
        if water_depth > 30 and self.available_pumps > 0:
            pumps_needed = min(3, self.available_pumps)
            self.available_pumps -= pumps_needed
            print(f"[{current_step}] 水务局向{location}派出{pumps_needed}台移动泵车")
            
            # 创建排水任务
            task = Task(
                id=len(self.drainage_tasks) + 1,
                incident_type=IncidentType.ROAD_FLOODING,
                location=location,
                urgency=0.7,
                create_time=current_step
            )
            self.drainage_tasks.append(task)
            
            # 请求交通协同
            if water_depth > 50:
                return 2  # 需要交通管制
            return 1  # 仅排水
            
        return 0  # 无需排水
        
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        for msg in self.inbox:
            if msg.get("type") == "drainage_request":
                water_depth = msg.get("water_depth", 0)
                location = msg.get("location", "未知")
                self.schedule_drainage(water_depth, location, current_step)
        self.inbox = []

class TrafficPolice(BaseAgent):
    """交管局"""
    def __init__(self, agent_id: int, grid_area: str):
        super().__init__(agent_id, AgentType.TRAFFIC_POLICE)
        self.grid_area = grid_area
        self.traffic_control_active = False
        self.control_threshold = 50
        self.standardized_procedure = False
        self.response_delay = 0
        
    def implement_control(self, water_depth: float, location: str, current_step: int) -> bool:
        """实施交通管制"""
        should_control = water_depth > self.control_threshold
        
        if self.standardized_procedure:
            delay = 0
        else:
            delay = random.randint(1, 3)
            
        if should_control and not self.traffic_control_active:
            self.traffic_control_active = True
            self.response_delay = delay
            if delay > 0:
                print(f"[{current_step}] 交管局{self.grid_area}将在{delay}步后对{location}实施交通管制")
                self.busy_until = current_step + delay
            else:
                print(f"[{current_step}] 交管局{self.grid_area}立即对{location}实施交通管制")
            return True
            
        return False
        
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        if current_step >= self.busy_until and self.traffic_control_active:
            print(f"[{current_step}] 交管局{self.grid_area}完成交通管制设置")
            self.traffic_control_active = False
            self.update_metrics(task_completed=True)
            
        for msg in self.inbox:
            if msg.get("type") == "traffic_coordination":
                water_depth = msg.get("water_depth", 0)
                location = msg.get("location", "未知")
                self.implement_control(water_depth, location, current_step)
                
        self.inbox = []

class RescueTeam(BaseAgent):
    """抢险大队"""
    def __init__(self, agent_id: int, team_type: str, capability: float = 1.0):
        super().__init__(agent_id, AgentType.RESCUE_TEAM)
        self.team_type = team_type
        self.capability = capability
        self.assembly_speed = 0.8
        self.current_location = (random.uniform(0, 100), random.uniform(0, 100))
        self.equipment_type = "综合"
        self.available = True
        self.sanitary_check = False
        
    def execute_mission(self, task: Task, current_step: int, scenario_mode: str = "baseline"):
        """执行抢险任务"""
        self.available = False
        
        # 防疫检查延迟
        sanitary_delay = 0
        if scenario_mode == "baseline" and random.random() < 0.5:
            sanitary_delay = random.randint(1, 2)
            self.sanitary_check = True
            
        # 集结时间
        assembly_time = int(6 * (1 - self.assembly_speed))
        
        # 任务执行时间
        execution_time = int(10 * (1 - task.urgency) * (1.5 - self.capability))
        
        total_time = assembly_time + execution_time + sanitary_delay
        
        self.busy_until = current_step + total_time
        
        if sanitary_delay > 0:
            print(f"[{current_step}] {self.team_type}抢险队执行防疫检查，延迟{sanitary_delay}步")
            
        print(f"[{current_step}] {self.team_type}抢险队开始执行{task.incident_type.value}任务，预计{total_time}步完成")
        
        task.start_time = current_step
        task.status = "in_progress"
        self.tasks.append(task)
        
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        if current_step >= self.busy_until and self.tasks:
            task = self.tasks[0]
            task.completion_time = current_step
            task.status = "completed"
            response_time = current_step - task.create_time
            print(f"[{current_step}] {self.team_type}抢险队完成任务，响应时间：{response_time}步")
            self.update_metrics(task_completed=True, response_time=response_time)
            self.available = True
            self.tasks = []
            
        for msg in self.inbox:
            if msg.get("type") in ["direct_command", "task_assignment", "hierarchical_assignment"]:
                task = msg.get("task")
                if task and self.available:
                    scenario_mode = msg.get("scenario_mode", "baseline")
                    self.execute_mission(task, current_step, scenario_mode)
                    
        self.inbox = []

class Inspector(BaseAgent):
    """巡查员"""
    def __init__(self, agent_id: int, patrol_range: str, reporting_path: str = "hierarchical"):
        super().__init__(agent_id, AgentType.INSPECTOR)
        self.patrol_range = patrol_range
        self.reporting_path = reporting_path
        self.discovery_probability = 0.8
        
    def patrol(self, current_step: int, rainfall_intensity: float) -> Optional[Dict]:
        """巡查并发现事件"""
        discovery_rate = min(0.3 + rainfall_intensity/150, 0.9)
        
        if random.random() < discovery_rate * self.discovery_probability:
            incident_type = random.choice(list(IncidentType))
            location = f"{self.patrol_range}_{random.randint(1, 10)}"
            water_depth = random.uniform(20, rainfall_intensity)
            
            report = {
                "type": "incident_report",
                "incident_type": incident_type.value,  # 使用 .value 确保是字符串
                "location": location,
                "water_depth": water_depth,
                "urgency": min(0.3 + water_depth/100, 0.95),
                "timestamp": current_step
            }
            
            print(f"[{current_step}] 巡查员{self.patrol_range}发现{incident_type.value}于{location}，水深{water_depth:.1f}cm")
            return report
            
        return None
        
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        pass

class InfoPlatform(BaseAgent):
    """综合信息平台"""
    def __init__(self, agent_id: int, processing_capacity: int = 20):
        super().__init__(agent_id, AgentType.INFO_PLATFORM)
        self.processing_capacity = processing_capacity
        self.intelligent_matching = False
        self.task_queue: List[Task] = []
        
    def integrate_info(self, report: Dict, current_step: int):
        """整合信息"""
        if len(self.task_queue) < self.processing_capacity * 2:
            # 安全转换事件类型
            incident_type_str = report.get("incident_type", "道路积水")
            incident_type = IncidentType.from_string(incident_type_str)
            
            task = Task(
                id=len(self.task_queue) + 1,
                incident_type=incident_type,
                location=report["location"],
                urgency=report.get("urgency", 0.5),
                create_time=current_step
            )
            self.task_queue.append(task)
        else:
            print(f"[{current_step}] 信息平台容量饱和，任务被丢弃")
            
    def dispatch_tasks(self, agents: List[BaseAgent], current_step: int):
        """分派任务"""
        if not self.task_queue:
            return
            
        if self.intelligent_matching:
            tasks_to_dispatch = self._intelligent_dispatch(agents, current_step)
        else:
            tasks_to_dispatch = self._basic_dispatch(agents, current_step)
            
        for task, target_agent in tasks_to_dispatch:
            self.send_message(target_agent, {
                "type": "task_assignment",
                "task": task,
                "timestamp": current_step
            })
            task.assigned_to = f"{target_agent.type.value}_{target_agent.id}"
            task.start_time = current_step
            task.status = "assigned"
            print(f"[{current_step}] 信息平台向{target_agent.type.value}_{target_agent.id}分派{task.incident_type.value}任务")
            
    def _basic_dispatch(self, agents: List[BaseAgent], current_step: int) -> List[Tuple[Task, BaseAgent]]:
        """基本分派"""
        dispatched = []
        for task in self.task_queue[:self.processing_capacity]:
            for agent in agents:
                if self._is_suitable_agent(agent, task):
                    dispatched.append((task, agent))
                    break
                    
        self.task_queue = self.task_queue[len(dispatched):]
        return dispatched
        
    def _intelligent_dispatch(self, agents: List[BaseAgent], current_step: int) -> List[Tuple[Task, BaseAgent]]:
        """智能分派"""
        dispatched = []
        tasks_to_remove = []
        
        for task in self.task_queue[:self.processing_capacity]:
            suitable_agents = []
            
            for agent in agents:
                if self._is_suitable_agent(agent, task):
                    priority_score = self._calculate_priority(agent, task)
                    suitable_agents.append((priority_score, agent))
                    
            if suitable_agents:
                suitable_agents.sort(key=lambda x: x[0], reverse=True)
                best_agent = suitable_agents[0][1]
                dispatched.append((task, best_agent))
                tasks_to_remove.append(task)
                
        for task in tasks_to_remove:
            if task in self.task_queue:
                self.task_queue.remove(task)
                
        return dispatched
        
    def _is_suitable_agent(self, agent: BaseAgent, task: Task) -> bool:
        """判断智能体是否适合任务"""
        if agent.type == AgentType.WATER_BUREAU and task.incident_type == IncidentType.ROAD_FLOODING:
            return True
        elif agent.type == AgentType.RESCUE_TEAM and task.incident_type in [IncidentType.EMBANKMENT_DANGER, IncidentType.PEOPLE_TRAPPED]:
            return True
        elif agent.type == AgentType.TRAFFIC_POLICE and task.incident_type == IncidentType.TRAFFIC_JAM:
            return True
        return False
        
    def _calculate_priority(self, agent: BaseAgent, task: Task) -> float:
        """计算优先级分数"""
        score = 0.0
        
        if hasattr(agent, 'capability'):
            score += agent.capability * 0.4
            
        score += task.urgency * 0.3
        
        if hasattr(agent, 'available') and agent.available:
            score += 0.3
            
        return score
        
    def process_inbox(self, current_step: int):
        """处理收件箱"""
        processed = 0
        for msg in self.inbox[:self.processing_capacity]:
            if msg.get("type") == "incident_report":
                self.integrate_info(msg, current_step)
            processed += 1
            
        self.inbox = self.inbox[processed:]