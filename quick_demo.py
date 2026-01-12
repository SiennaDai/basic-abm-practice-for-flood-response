"""
快速演示脚本
"""

import random
from model import FloodResponseModel
from scenarios import get_scenario_config

def quick_demo(scenario="baseline", steps=30):
    """快速演示"""
    print(f"\n{'='*60}")
    print(f"快速演示: {scenario}模式 ({steps}步)")
    print(f"{'='*60}")
    
    random.seed(42)
    
    config = get_scenario_config(scenario)
    config["steps"] = steps
    
    model = FloodResponseModel(config)
    
    # 简略输出
    for i in range(steps):
        model.time_step = i
        rainfall = model.generate_rainfall()
        incidents = model.generate_incidents(rainfall)
        
        if incidents:
            print(f"[步{i}] 降雨:{rainfall:.0f}mm, 事件:{len(incidents)}个")
        
        # 简略处理
        for agent in model.agents:
            if hasattr(agent, 'process_inbox'):
                agent.process_inbox(i)
        
        # 科层结构特殊处理
        if scenario == "hierarchical":
            model.hierarchical_dispatch()
    
    # 收集结果
    model.collect_metrics()
    
    print(f"\n{'='*60}")
    print(f"演示结果 ({scenario}):")
    print(f"事件总数: {model.metrics['total_incidents']}")
    print(f"解决事件: {model.metrics['resolved_incidents']}")
    if model.metrics['total_incidents'] > 0:
        rate = model.metrics['resolved_incidents'] / model.metrics['total_incidents']
        print(f"解决率: {rate:.1%}")
    print(f"{'='*60}")
    
    return model.metrics

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("洪水响应ABM快速演示")
    
    # 运行三种情景
    results = {}
    for scenario in ["baseline", "hierarchical", "optimized"]:
        results[scenario] = quick_demo(scenario, 25)
    
    # 简单对比
    print(f"\n{'#'*60}")
    print("简单对比:")
    print(f"{'情景':<12} {'事件数':<8} {'解决数':<8} {'解决率':<10}")
    print("-"*40)
    
    for scenario in ["baseline", "hierarchical", "optimized"]:
        m = results[scenario]
        total = m['total_incidents']
        resolved = m['resolved_incidents']
        rate = resolved / max(total, 1)
        print(f"{scenario:<12} {total:<8} {resolved:<8} {rate:<10.1%}")
    
    print(f"{'#'*60}")