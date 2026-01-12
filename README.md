## 项目概述
基于主体的洪水应急响应模拟系统，用于公共危机管理课程设计。包含三种情景对比。

## 项目结构
fresh_flood_response_abm/
├── base_types.py # 基础类型定义
├── agents.py # 智能体实现
├── model.py # 主模型类
├── scenarios.py # 三种情景配置
├── analysis.py # 数据分析模块
├── run_experiments.py # 运行实验脚本
├── quick_demo.py # 快速演示脚本
├── requirements.txt # 依赖包
└── README.md # 说明文档


## 三种情景
1. **基准模式**：武汉2020混合实践（信息平台+直接指挥）
2. **科层结构**：纯树状层级结构（无平台，层级上报）
3. **优化模式**：制度化协同网络（智能匹配+标准化）

## 快速开始
```bash
# 安装依赖（可选）
pip install -r requirements.txt

# 快速演示（推荐先测试）
python quick_demo.py

# 运行完整实验
python run_experiments.py