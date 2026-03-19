# Phase 5 开发报告

## 阶段目标
完成最小前端联调：卫星列表、预测请求、Cesium 可视化、TLE 时效提示。

## 本阶段完成内容
1. 新增前端 API 客户端：`web/src/api/client.ts`
   - 获取 tracked 列表。
   - 请求指定时间预测结果。
2. 重构主页面：`web/src/App.tsx`
   - 卫星选择、时间选择、预测触发。
   - 结果面板展示经纬高与 UTC 时间。
   - TLE 超 3 天时提示精度风险。
3. 实现 Cesium 视图：`web/src/viewer/CesiumViewer.tsx`
   - 初始化 Viewer。
   - 根据预测结果渲染卫星点位并相机飞行。
4. 样式与布局升级：`web/src/styles.css`
   - 左侧控制面板 + 右侧 3D 视图。
   - 移动端自适应布局。
5. Vite 配置补充：`web/vite.config.ts` 设置 `CESIUM_BASE_URL`。

## 安装的依赖
本阶段未执行依赖安装命令（仅使用已声明依赖）：
- react
- react-dom
- cesium
- vite

## 当前可用功能
1. 前端可读取后端 tracked 列表并触发预测。
2. 可在 Cesium 中显示当前预测点位。
3. 可显示 TLE 老化告警（超过 3 天）。