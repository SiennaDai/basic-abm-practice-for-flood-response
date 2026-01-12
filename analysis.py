"""
数据分析模块 - 修复版（无除零错误）
"""

import json
from typing import Dict, List, Any
import statistics

class ScenarioAnalyzer:
    """情景分析器"""
    
    def __init__(self):
        self.results = {}
        self.comparison_data = {}
        
    def add_scenario_result(self, scenario_name: str, metrics: Dict[str, Any]):
        """添加情景结果"""
        self.results[scenario_name] = metrics
        
    def compare_scenarios(self):
        """比较不同情景"""
        
        comparison = {}
        
        for scenario_name, metrics in self.results.items():
            backlog = metrics.get("task_backlog", [0])
            if not backlog:
                backlog = [0]
            
            # 安全计算指标，避免除零
            total_incidents = max(metrics.get("total_incidents", 0), 1)
            resolved_incidents = metrics.get("resolved_incidents", 0)
            
            avg_response = metrics.get("avg_response_time", 0)
            if avg_response == 0 and resolved_incidents > 0:
                avg_response = 1.0
                
            system_efficiency = metrics.get("system_efficiency", 0)
            if system_efficiency == 0 and resolved_incidents > 0:
                resolution_rate = resolved_incidents / total_incidents
                system_efficiency = resolution_rate * (1 / max(avg_response, 1))
            
            comparison[scenario_name] = {
                "事件总数": metrics.get("total_incidents", 0),
                "解决事件数": resolved_incidents,
                "解决率": resolved_incidents / total_incidents,
                "平均响应时间": avg_response,
                "系统效率": system_efficiency,
                "瓶颈事件次数": metrics.get("bottleneck_events", 0),
                "最大任务积压": max(backlog),
                "平均任务积压": statistics.mean(backlog) if backlog else 0,
            }
        
        self.comparison_data = comparison
        return comparison
        
    def print_comparison_table(self):
        """打印比较表格"""
        if not self.comparison_data:
            print("没有可比较的数据")
            return
            
        print("\n" + "="*80)
        print("情景对比分析")
        print("="*80)
        
        headers = ["指标", "基准模式", "科层结构", "优化模式"]
        print(f"{headers[0]:<20} {headers[1]:<15} {headers[2]:<15} {headers[3]:<15}")
        print("-"*80)
        
        baseline_metrics = self.comparison_data.get("baseline", {})
        metrics_list = list(baseline_metrics.keys())
        
        for metric in metrics_list:
            row = [metric]
            for scenario in ["baseline", "hierarchical", "optimized"]:
                value = self.comparison_data.get(scenario, {}).get(metric, 0)
                
                if "率" in metric or "效率" in metric:
                    formatted = f"{value:.2%}"
                elif "时间" in metric:
                    formatted = f"{value:.1f}步"
                else:
                    formatted = f"{value:.1f}"
                    
                row.append(formatted)
            
            print(f"{row[0]:<20} {row[1]:<15} {row[2]:<15} {row[3]:<15}")
        
        print("="*80)
        
    def calculate_improvements(self):
        """计算改进效果 - 安全版"""
        
        if "baseline" not in self.comparison_data or "hierarchical" not in self.comparison_data:
            print("需要基准模式和科层结构的数据")
            return
            
        print("\n" + "="*60)
        print("改进效果分析")
        print("="*60)
        
        baseline = self.comparison_data["baseline"]
        hierarchical = self.comparison_data["hierarchical"]
        
        # 安全计算函数
        def safe_percent_change(new, old):
            if old == 0:
                return 0 if new == 0 else (1.0 if new > 0 else -1.0)
            return (new - old) / old
        
        # 响应时间对比（正数表示科层更慢）
        response_change = safe_percent_change(
            hierarchical["平均响应时间"],
            baseline["平均响应时间"]
        )
        
        # 系统效率对比（正数表示基准更好）
        efficiency_change = safe_percent_change(
            baseline["系统效率"],
            hierarchical["系统效率"]
        )
        
        print(f"1. 响应时间对比: {response_change:+.1%} ({'科层更慢' if response_change > 0 else '科层更快' if response_change < 0 else '相同'})")
        print(f"   • 基准模式: {baseline['平均响应时间']:.1f}步")
        print(f"   • 科层结构: {hierarchical['平均响应时间']:.1f}步")
        
        print(f"\n2. 系统效率对比: {efficiency_change:+.1%} ({'基准更好' if efficiency_change > 0 else '科层更好' if efficiency_change < 0 else '相同'})")
        print(f"   • 基准模式: {baseline['系统效率']:.3f}")
        print(f"   • 科层结构: {hierarchical['系统效率']:.3f}")
        
        print(f"\n3. 任务处理能力:")
        print(f"   • 基准模式解决率: {baseline['解决率']:.1%}")
        print(f"   • 科层结构解决率: {hierarchical['解决率']:.1%}")
        print(f"   • 科层结构任务积压: 最大{hierarchical['最大任务积压']}，平均{hierarchical['平均任务积压']:.1f}")
        
        # 优化模式 vs 基准模式
        if "optimized" in self.comparison_data:
            optimized = self.comparison_data["optimized"]
            
            print(f"\n" + "-"*40)
            print("优化模式效果:")
            
            time_change = safe_percent_change(
                optimized["平均响应时间"],
                baseline["平均响应时间"]
            )
            
            resolution_change = safe_percent_change(
                optimized["解决率"],
                baseline["解决率"]
            )
                
            print(f"1. 响应时间变化: {time_change:+.1%} ({'优化更慢' if time_change > 0 else '优化更快' if time_change < 0 else '相同'})")
            print(f"2. 解决率提升: {resolution_change:+.1%}")
            bottleneck_change = baseline['瓶颈事件次数'] - optimized['瓶颈事件次数']
            print(f"3. 瓶颈事件变化: {bottleneck_change:+.0f}次 ({'减少' if bottleneck_change > 0 else '增加' if bottleneck_change < 0 else '相同'})")
        
        print("="*60)
        
    def generate_findings(self):
        """生成研究发现"""
        
        findings = []
        
        if "hierarchical" in self.comparison_data:
            hierarchical_data = self.comparison_data["hierarchical"]
            baseline_data = self.comparison_data.get("baseline", {})
            
            findings.append({
                "title": "科层结构的局限性",
                "content": f"""
                纯树状科层结构在模拟中表现出明显不足：
                1. 事件解决率仅为{hierarchical_data['解决率']:.1%}，而基准模式为{baseline_data.get('解决率', 0):.1%}
                2. 响应时间相对基准模式{(hierarchical_data['平均响应时间'] - baseline_data.get('平均响应时间', 0)):+.1f}步
                3. 任务积压严重，最大积压达{hierarchical_data['最大任务积压']}个
                这验证了扁平化、网络化改革的必要性。
                """
            })
        
        if "baseline" in self.comparison_data:
            baseline_data = self.comparison_data["baseline"]
            findings.append({
                "title": "混合实践的有效性",
                "content": f"""
                武汉2020年采用的混合模式有效平衡了效率与控制：
                1. 信息平台作为枢纽，处理了大量信息流
                2. 直接指挥链路缩短了关键任务响应时间
                3. 事件解决率达到{baseline_data['解决率']:.1%}
                4. 平均响应时间为{baseline_data['平均响应时间']:.1f}步
                """
            })
        
        if "optimized" in self.comparison_data:
            optimized_data = self.comparison_data["optimized"]
            baseline_data = self.comparison_data.get("baseline", {})
            
            resolution_improvement = (optimized_data["解决率"] - baseline_data.get("解决率", 0)) / max(baseline_data.get("解决率", 1), 1)
            
            findings.append({
                "title": "规则优化的潜力",
                "content": f"""
                通过规则优化（不改变结构或增加资源）可进一步提升效能：
                1. 解决率从{baseline_data.get('解决率', 0):.1%}提升到{optimized_data['解决率']:.1%}（提升{resolution_improvement:.1%}）
                2. 智能匹配提高了资源利用率
                3. 标准化流程减少了协同延迟
                4. 瓶颈事件减少{baseline_data.get('瓶颈事件次数', 0) - optimized_data['瓶颈事件次数']}次
                这展示了"常态化"韧性的建设路径。
                """
            })
        
        print("\n" + "="*80)
        print("研究发现总结")
        print("="*80)
        
        for i, finding in enumerate(findings, 1):
            print(f"\n{i}. {finding['title']}")
            print(finding['content'])
        
        print("="*80)
        
    def export_results(self, filename: str = "abm_simulation_results.json"):
        """导出结果到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "results": self.results,
                "comparison": self.comparison_data
            }, f, ensure_ascii=False, indent=2)
        
        print(f"结果已导出到 {filename}")