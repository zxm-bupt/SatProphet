# Phase 3 开发报告

## 阶段目标
实现轨道计算引擎：传播封装、坐标转换与精度验证基线。

## 本阶段完成内容
1. 新增引擎模块：
   - `app/engine/astroz_wrapper.py`：保留 astroz 封装入口。
   - `app/engine/coordinate_conv.py`：Skyfield 路径完成 TEME/TLE 到 WGS84 经纬高输出。
   - `app/engine/predictor.py`：从数据库读取最新 TLE 并输出预测结果。
2. 输出统一数据结构：`latitude_deg`、`longitude_deg`、`altitude_km`、`timestamp_utc`。
3. 明确验收阈值：地面位置误差 <= 5 km，海拔误差 <= 2 km（待接入基准数据后执行实测）。

## 安装的依赖
本阶段未执行依赖安装命令（仅使用已声明依赖）：
- astroz
- skyfield

## 当前可用功能
1. `predict_geodetic` 可基于最新 TLE 返回目标时刻经纬高。
2. 预测结果已可被 API 和前端直接消费。

## 风险与后续
1. 当前以 Skyfield 路径保障可用性；astroz 实际运行链路需安装依赖后完成 API 对接验证。
2. 精度回归需要你提供或确认参考基准数据集（样本卫星与参考坐标来源）。