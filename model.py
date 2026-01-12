"""
主模型类 - 修复版
"""

import random
import time
from typing import List, Dict, Any, Optional
from base_types import *
from agents import *

class FloodResponseModel:
    """洪水响应ABM模型"""
    
    def __init__(self, scenario_config: Dict[str, Any]):
        # 设置固定随机种子确保可重复
        random.seed(42)
        
        self.scenario_name = scenario_config.get("name", "baseline")
        self.scenario_mode = scenario_config.get("mode", "baseline")
        self.steps = scenario_config.get("steps", 80)
        
        self.agents: List[BaseAgent] = []
        self.time_step = 0
        self.rainfall_history: List[float] = []
        self.incidents_log: List[Dict] = []
        self.metrics = {
            "total_incidents": 0,
            "resolved_incidents": 0,
            "avg_response_time": 0,
            "task_backlog": [],
            "system_efficiency": 0,
            "bottleneck_events": 0
        }
        
        self._create_agents(scenario_config)
        
        
    def _create_agents(self, config: Dict[str, Any]):
        """根据配置创建智能体"""
        
        # 1. 市防指
        command_center = CommandCenter(1)
        command_center.direct_command_enabled = config.get("direct_command_enabled", True)
        self.agents.append(command_center)
        
        # 2. 水务局
        water_bureau = WaterBureau(2)
        self.agents.append(water_bureau)
        
        # 3. 交管局
        grid_areas = config.get("traffic_police_grids", ["江岸区", "江汉区", "硚口区"])
        for i, area in enumerate(grid_areas):
            traffic_police = TrafficPolice(3 + i, area)
            traffic_police.standardized_procedure = config.get("standardized_procedures", False)
            self.agents.append(traffic_police)
        
        # 4. 抢险队
        rescue_teams_config = config.get("rescue_team_types", [("市级", 0.9), ("国企", 0.8), ("区级", 0.7)])
        for i, (team_type, capability) in enumerate(rescue_teams_config):
            rescue_team = RescueTeam(10 + i, team_type, capability)
            self.agents.append(rescue_team)
        
        # 5. 巡查员
        num_inspectors = config.get("num_inspectors", 6)
        patrol_ranges = ["堤段A", "堤段B", "街道C", "街道D", "社区E", "社区F", "区域G", "区域H"]
        reporting_path = config.get("reporting_path", "mixed")
        for i in range(min(num_inspectors, len(patrol_ranges))):
            inspector = Inspector(20 + i, patrol_ranges[i], reporting_path)
            self.agents.append(inspector)
        
        # 6. 信息平台
        if config.get("info_platform_enabled", True):
            info_platform = InfoPlatform(100, processing_capacity=config.get("platform_capacity", 15))
            info_platform.intelligent_matching = config.get("intelligent_matching", False)
            self.agents.append(info_platform)
        
        print(f"情景 '{self.scenario_name}' 初始化完成，共创建 {len(self.agents)} 个智能体")
        
    def generate_rainfall(self) -> float:
        """生成降雨事件"""
        if self.time_step < 20:
            base = random.uniform(20, 40)
        elif self.time_step < 50:
            base = random.uniform(40, 80)
        else:
            if random.random() < 0.3:
                base = random.uniform(80, 120)
            else:
                base = random.uniform(30, 60)
                
        self.rainfall_history.append(base)
        return base
        
# 在 generate_incidents 方法中，确保所有事件都被记录
    def generate_incidents(self, rainfall: float):
        """生成随机事件"""
        incident_types = list(IncidentType)
        
        incident_prob = min(0.2 + rainfall/200, 0.6)
        
        num_incidents = random.choices([0, 1, 2], 
                                    weights=[1-incident_prob, incident_prob*0.7, 
                                            incident_prob*0.3])[0]
        
        incidents = []
        for _ in range(num_incidents):
            incident_type = random.choice(incident_types)
            location = f"区域{random.randint(1, 20)}"
            water_depth = random.uniform(10, min(rainfall + 20, 120))
            
            incident = {
                "type": "incident_report",
                "incident_type": incident_type.value,
                "location": location,
                "water_depth": water_depth,
                "urgency": min(0.3 + water_depth/100, 0.95),
                "timestamp": self.time_step,
                "scenario": self.scenario_mode  # 添加情景标记
            }
            
            incidents.append(incident)
            self.incidents_log.append(incident)
            self.metrics["total_incidents"] += 1
            
            print(f"[{self.time_step}] 生成事件：{incident_type.value}于{location}")
        
        return incidents
         
    def hierarchical_reporting(self, incident: Dict, inspector: Inspector):
        """层级上报机制 - 修复版"""
        if inspector.reporting_path == "hierarchical":
            delay_steps = random.randint(3, 8)
            
            print(f"[{self.time_step}] {inspector.patrol_range}巡查员发现{incident['incident_type']}，开始层级上报...")
            
            # 模拟上报到指挥部
            for agent in self.agents:
                if isinstance(agent, CommandCenter):
                    # 使用安全转换
                    incident_type = IncidentType.from_string(incident["incident_type"])
                    
                    # 创建任务（考虑上报延迟）
                    task = Task(
                        id=len(self.incidents_log) + 1000,
                        incident_type=incident_type,
                        location=incident["location"],
                        urgency=incident.get("urgency", 0.5),
                        create_time=self.time_step + delay_steps  # 任务创建时间考虑延迟
                    )
                    
                    # 添加到指挥部紧急任务列表
                    agent.emergency_tasks.append(task)
                    print(f"[{self.time_step}] 事件已上报，预计{delay_steps}步后到达市防指")
                    return delay_steps
        
        return 0
        
    def direct_platform_reporting(self, incident: Dict, inspector: Inspector):
        """直接平台上报"""
        if inspector.reporting_path in ["direct", "mixed"]:
            for agent in self.agents:
                if isinstance(agent, InfoPlatform):
                    agent.receive_message(incident)
                    return True
        return False
        
    def hierarchical_dispatch(self):
        """科层结构下的手动任务调度"""
        if self.scenario_mode != "hierarchical":
            return
        
        # 查找指挥部
        command_center = None
        for agent in self.agents:
            if isinstance(agent, CommandCenter):
                command_center = agent
                break
        
        if not command_center:
            return
        
        # 处理已到达的紧急任务（考虑上报延迟）
        current_tasks = []
        for task in command_center.emergency_tasks:
            if task.status == "pending" and self.time_step >= task.create_time:
                current_tasks.append(task)
        
        if not current_tasks:
            return
        
        # 查找可用抢险队
        available_teams = []
        for agent in self.agents:
            if isinstance(agent, RescueTeam) and agent.available:
                available_teams.append(agent)
        
        if not available_teams:
            return
        
        # 分派任务（每次最多2个）
        for task in current_tasks[:2]:
            team = available_teams[0]
            print(f"[{self.time_step}] 市防指通过科层调度{team.team_type}抢险队执行{task.incident_type.value}")
            
            team.receive_message({
                "type": "hierarchical_assignment",
                "task": task,
                "urgency": "medium"
            })
            task.assigned_to = f"{team.type.value}_{team.id}"
            task.start_time = self.time_step
            task.status = "assigned"
            
            # 从指挥部任务列表移除
            command_center.emergency_tasks.remove(task)
            available_teams.pop(0)  # 该队伍不再可用
            
            if not available_teams:
                break
        
    def run_coordination(self, rainfall: float):
        """运行协同机制"""
        # 水务-交管协同
        if rainfall > 60:
            water_bureau = None
            traffic_police_list = []
            
            for agent in self.agents:
                if isinstance(agent, WaterBureau):
                    water_bureau = agent
                elif isinstance(agent, TrafficPolice):
                    traffic_police_list.append(agent)
            
            if water_bureau and traffic_police_list:
                location = f"区域{random.randint(1, 10)}"
                water_depth = random.uniform(40, 80)
                
                result = water_bureau.schedule_drainage(water_depth, location, self.time_step)
                
                if result == 2:
                    area_index = hash(location) % len(traffic_police_list)
                    traffic_police = traffic_police_list[area_index]
                    
                    traffic_police.receive_message({
                        "type": "traffic_coordination",
                        "water_depth": water_depth,
                        "location": location,
                        "timestamp": self.time_step
                    })
        
        # 市防指直接指挥（紧急情况下）
        if rainfall > 80 and self.time_step > 10:
            command_center = None
            rescue_teams = []
            
            for agent in self.agents:
                if isinstance(agent, CommandCenter):
                    command_center = agent
                elif isinstance(agent, RescueTeam) and agent.available:
                    rescue_teams.append(agent)
            
            if command_center and command_center.direct_command_enabled and rescue_teams:
                emergency_task = Task(
                    id=1000 + self.time_step,
                    incident_type=IncidentType.EMBANKMENT_DANGER,
                    location=f"紧急区域{random.randint(1, 5)}",
                    urgency=0.95,
                    create_time=self.time_step
                )
                
                selected_team = rescue_teams[0]
                command_center.direct_dispatch(selected_team, emergency_task, self.time_step)
                
    def collect_metrics(self):
        """收集性能指标"""
        response_times = []
        tasks_completed = 0
        
        for agent in self.agents:
            if isinstance(agent, RescueTeam):
                response_times.extend(agent.response_times)
                tasks_completed += agent.metrics["tasks_completed"]
        
        if response_times:
            self.metrics["avg_response_time"] = sum(response_times) / len(response_times)
        
        self.metrics["resolved_incidents"] = tasks_completed
        
        # 计算系统效率
        if self.metrics["total_incidents"] > 0:
            resolution_rate = tasks_completed / self.metrics["total_incidents"]
            efficiency_score = resolution_rate * (1 / (self.metrics["avg_response_time"] + 1))
            self.metrics["system_efficiency"] = efficiency_score
        
        # 记录任务积压 - 修复版
        backlog = 0
        if self.scenario_mode == "hierarchical":
            # 科层结构：统计指挥部未分派的任务
            for agent in self.agents:
                if isinstance(agent, CommandCenter):
                    backlog = len([t for t in agent.emergency_tasks if t.status == "pending"])
                    break
        else:
            # 其他模式：统计信息平台积压
            for agent in self.agents:
                if isinstance(agent, InfoPlatform):
                    backlog = len(agent.task_queue)
                    break
        
        self.metrics["task_backlog"].append(backlog)
        
        # 检查瓶颈
        if backlog > (20 if self.scenario_mode == "optimized" else 10):
            self.metrics["bottleneck_events"] += 1
            
    def step(self):
        """运行一个时间步"""
        self.time_step += 1
        
        print(f"\n{'='*60}")
        print(f"时间步 {self.time_step} | 情景: {self.scenario_name}")
        print(f"{'='*60}")
        
        # 1. 生成降雨
        rainfall = self.generate_rainfall()
        print(f"[{self.time_step}] 降雨强度: {rainfall:.1f}mm")
        
        # 2. 指挥部发布响应等级
        for agent in self.agents:
            if isinstance(agent, CommandCenter):
                agent.issue_response_level(rainfall, self.time_step)
                break
        
        # 3. 生成事件
        incidents = self.generate_incidents(rainfall)
        
        # 4. 巡查员报告
        for agent in self.agents:
            if isinstance(agent, Inspector):
                report = agent.patrol(self.time_step, rainfall)
                if report:
                    if self.scenario_mode == "hierarchical":
                        delay = self.hierarchical_reporting(report, agent)
                    elif self.scenario_mode in ["baseline", "optimized"]:
                        if self.direct_platform_reporting(report, agent):
                            print(f"[{self.time_step}] {agent.patrol_range}巡查员直接上报信息平台")
        
        # 5. 智能体处理消息
        for agent in self.agents:
            agent.process_inbox(self.time_step)
        
        # 6. 信息平台分派任务
        for agent in self.agents:
            if isinstance(agent, InfoPlatform):
                other_agents = [a for a in self.agents if a != agent]
                agent.dispatch_tasks(other_agents, self.time_step)
        
        # 6.5 科层结构下的手动调度
        if self.scenario_mode == "hierarchical":
            self.hierarchical_dispatch()
        
        # 7. 运行协同机制
        self.run_coordination(rainfall)
        
        # 8. 收集指标
        self.collect_metrics()
        
        # 9. 输出当前状态
        if self.time_step % 20 == 0:
            self.print_status()
        
    def print_status(self):
        """输出当前状态"""
        print(f"\n[状态报告] 时间步 {self.time_step}")
        print(f"累积事件: {self.metrics['total_incidents']}")
        print(f"已解决: {self.metrics['resolved_incidents']}")
        if self.metrics['avg_response_time'] > 0:
            print(f"平均响应时间: {self.metrics['avg_response_time']:.1f}步")
        print(f"系统效率: {self.metrics['system_efficiency']:.3f}")
        
        # 检查信息平台积压
        for agent in self.agents:
            if isinstance(agent, InfoPlatform):
                backlog = len(agent.task_queue)
                print(f"信息平台积压任务: {backlog}")
                break
        
    def run(self):
        """运行完整模拟"""
        print(f"\n{'#'*60}")
        print(f"开始运行情景: {self.scenario_name}")
        print(f"{'#'*60}\n")
        
        start_time = time.time()
        
        for step in range(self.steps):
            self.step()
            
            # 每20步输出详细报告
            if (step + 1) % 20 == 0:
                print(f"\n{'='*60}")
                print(f"阶段报告 (步数 {step + 1})")
                print(f"{'='*60}")
                self.print_detailed_metrics()
        
        end_time = time.time()
        print(f"\n{'#'*60}")
        print(f"情景 '{self.scenario_name}' 模拟完成")
        print(f"总耗时: {end_time - start_time:.2f}秒")
        print(f"{'#'*60}")
        
        return self.metrics
        
    def print_detailed_metrics(self):
        """输出详细指标"""
        print("\n[详细性能指标]")
        print("-" * 40)
        
        agent_types = {}
        for agent in self.agents:
            agent_type = agent.type.value
            if agent_type not in agent_types:
                agent_types[agent_type] = {
                    "count": 0,
                    "tasks_completed": 0,
                    "avg_response": 0
                }
            
            agent_types[agent_type]["count"] += 1
            agent_types[agent_type]["tasks_completed"] += agent.metrics.get("tasks_completed", 0)
            if agent.metrics.get("avg_response_time", 0) > 0:
                agent_types[agent_type]["avg_response"] = agent.metrics['avg_response_time']
        
        for agent_type, stats in agent_types.items():
            print(f"{agent_type}: {stats['count']}个，完成任务: {stats['tasks_completed']}，平均响应: {stats['avg_response']:.1f}步")
        
        print(f"\n系统总体表现:")
        total = self.metrics['total_incidents']
        resolved = self.metrics['resolved_incidents']
        print(f"事件解决率: {resolved}/{total} ({resolved/max(total,1)*100:.1f}%)")
        print(f"瓶颈事件次数: {self.metrics['bottleneck_events']}")
        print("-" * 40)