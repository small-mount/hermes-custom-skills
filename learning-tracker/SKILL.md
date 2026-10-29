---
name: learning-tracker
description: "拆解学习目标与督促打卡。单词背了就忘？每天帮你盯进度，到点就催你学 This skill should be used when the user asks about 拆解学习目标与督促打卡. Keywords: 背单词, 督促学习."
---

# 拆解学习目标与督促打卡

> 单词背了就忘？每天帮你盯进度，到点就催你学

## 前置依赖

```bash
pip install pandas openpyxl
```

## 核心能力

### 能力1：学习资料检索

根据用户学习目标，用 `web_search` 检索适合的学习资料。

### 能力2：每日推送定时任务

用 `automation_update` 创建每日推送定时任务。

### 能力3：学习记录与周报

运行脚本记录每日学习情况，生成周报。

## 命令列表

| 命令 | 说明 | 用法 |
|------|------|------|
| `init` | 初始化学习记录 | `python3 scripts/learning_tracker_tool.py init --goal GOAL --daily-target TARGET --output PATH` |
| `log` | 记录每日学习 | `python3 scripts/learning_tracker_tool.py log --file PATH --date DATE --completed ITEMS` |
| `report` | 生成周报 | `python3 scripts/learning_tracker_tool.py report --file PATH --output REPORT_PATH` |

## 使用流程

### 步骤 1：了解学习目标

询问用户：① 学什么（如背单词、学Python）② 当前水平 ③ 期望目标 ④ 每天可用时间

### 步骤 2：搜索学习资料

根据用户目标执行搜索：
```
web_search("[学习目标] 学习资料推荐")
web_search("[学习目标] 每日学习计划")
web_search("[学习目标] 入门到进阶路径")
```
提取有用的资料链接、推荐书目、在线课程等。

### 步骤 3：创建定时任务

用 `automation_update` 创建每日学习推送任务：
```
automation_update: rrule=FREQ=DAILY;BYHOUR=8;BYMINUTE=0
prompt="根据学习计划推送今日学习任务"
```

### 步骤 4：初始化学习记录

运行脚本初始化学习记录：
```bash
python3 scripts/learning_tracker_tool.py init --goal "学习目标" --daily-target "每日目标量" --output "/path/to/learning_log.xlsx"
```

### 步骤 5：每日推送与记录

每日定时任务触发时：
1. 读取学习记录文件，确认今日任务
2. 推送今日学习内容和资料
3. 到晚上再运行记录命令：
```bash
python3 scripts/learning_tracker_tool.py log --file learning_log.xlsx --date today --completed "完成内容"
```

### 步骤 6：生成周报

每周运行：
```bash
python3 scripts/learning_tracker_tool.py report --file learning_log.xlsx --output weekly_report.md
```
用 `write_to_file` 保存周报。

## 输出格式

输出格式：文字推送 + 日程确认 + 学习记录

## 验收标准

- ✅ 创建了日程
- ✅ 每日推送
- ✅ 记录学习情况
- ✅ 生成周报

## 场景化适配

根据学习水平调整难度

## 依赖 Skills

- **study-buddy**

## 注意事项

- 所有数据必须来自真实搜索结果或用户提供的文件，**严禁编造数据**
- 数据缺失时标注"数据不可用"而非猜测
- 输出必须保存为文件（`write_to_file`），不能只在对话中输出
- 建议结合人工判断使用，AI 分析仅供参考
