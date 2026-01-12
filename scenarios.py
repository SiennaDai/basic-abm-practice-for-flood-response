"""
三种情景配置
"""

SCENARIO_CONFIGS = {
    "baseline": {
        "name": "基准模式（武汉2020混合实践）",
        "mode": "baseline",
        "steps": 80,
        "info_platform_enabled": True,
        "direct_command_enabled": True,
        "standardized_procedures": False,
        "intelligent_matching": False,
        "reporting_path": "mixed",
        "platform_capacity": 15,
        "num_rescue_teams": 4,
        "num_inspectors": 6,
        "traffic_police_grids": ["江岸区", "江汉区", "硚口区"],
        "rescue_team_types": [("市级", 0.9), ("国企", 0.8), ("区级", 0.7), ("企业", 0.75)],
    },
    "hierarchical": {
        "name": "纯树状科层结构",
        "mode": "hierarchical",
        "steps": 80,
        "info_platform_enabled": False,
        "direct_command_enabled": False,
        "standardized_procedures": False,
        "intelligent_matching": False,
        "reporting_path": "hierarchical",
        "platform_capacity": 0,
        "num_rescue_teams": 4,
        "num_inspectors": 6,
        "traffic_police_grids": ["江岸区", "江汉区", "硚口区"],
        "rescue_team_types": [("市级", 0.9), ("国企", 0.8), ("区级", 0.7), ("企业", 0.75)],
        "hierarchical_delay": (3, 8),  # 层级上报延迟范围
    },
    "optimized": {
        "name": "制度化与智能化的协同网络",
        "mode": "optimized",
        "steps": 80,
        "info_platform_enabled": True,
        "direct_command_enabled": True,
        "standardized_procedures": True,
        "intelligent_matching": True,
        "reporting_path": "direct",
        "platform_capacity": 30,  # 增加容量到30
        "num_rescue_teams": 6,    # 增加到6个抢险队
        "num_inspectors": 8,
        "traffic_police_grids": ["江岸区", "江汉区", "硚口区", "汉阳区"],
        "rescue_team_types": [("市级", 0.9), ("国企", 0.85), ("区级", 0.8), 
                            ("企业", 0.8), ("社会", 0.7), ("机动", 0.75)],
        "standardized_delay": 0,  # 标准化流程无延迟
    }
}

def get_scenario_config(scenario_name: str):
    """获取情景配置"""
    return SCENARIO_CONFIGS.get(scenario_name, SCENARIO_CONFIGS["baseline"])
