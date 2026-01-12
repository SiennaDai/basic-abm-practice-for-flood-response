"""
运行实验脚本 - 修复版
"""

import time
import random
from model import FloodResponseModel
from scenarios import get_scenario_config
from analysis import ScenarioAnalyzer

def run_single_scenario(scenario_name: str, steps: int = None):
    """运行单个情景"""
    print(f"\n{'#'*80}")
    print(f"准备运行: {scenario_name}")
    print(f"{'#'*80}")
    
    config = get_scenario_config(scenario_name)
    if steps:
        config["steps"] = steps
    
    # 设置固定随机种子，确保可比性
    random.seed(42)
    
    model = FloodResponseModel(config)
    metrics = model.run()
    
    return metrics

def main():
    """主函数"""
    print("洪水响应ABM模拟实验 - 完整修复版")
    print("="*80)
    print("运行三种情景对比实验")
    print("="*80)
    
    analyzer = ScenarioAnalyzer()
    
    # 运行三种情景
    scenarios = ["baseline", "hierarchical", "optimized"]
    
    for scenario in scenarios:
        try:
            print(f"\n{'='*80}")
            print(f"开始实验: {scenario}")
            print(f"{'='*80}")
            
            start_time = time.time()
            metrics = run_single_scenario(scenario, steps=60)  # 60步加速
            end_time = time.time()
            
            analyzer.add_scenario_result(scenario, metrics)
            
            print(f"\n情景 '{scenario}' 完成，耗时: {end_time - start_time:.1f}秒")
            
            time.sleep(1)  # 暂停
            
        except Exception as e:
            print(f"运行情景 {scenario} 时出错: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 分析结果
    print(f"\n{'#'*80}")
    print("所有情景运行完成，开始分析...")
    print(f"{'#'*80}")
    
    analyzer.compare_scenarios()
    analyzer.print_comparison_table()
    analyzer.calculate_improvements()
    analyzer.generate_findings()
    
    # 导出结果
    analyzer.export_results("abm_simulation_results_final.json")
    
    print("\n" + "="*80)
    print("实验完成！")
    print("结果已保存到 abm_simulation_results_final.json")
    print("="*80)

if __name__ == "__main__":
    # 设置编码
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    main()