---
name: multi-agent-capability-adapter
description: "Use when comparing/selecting Hermes external CLI agents."
version: 1.0.0
author: 小山 (for 大山)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [multi-agent, capability-declaration, agent-selector, codex, claude, opencode, adapter, normalization]
    related_skills: [codex-agent-integration, hermes-agent]
---

# 多外接 Agent 能力目录 + 任务选择器

把多个「能力各异的外部 CLI Agent」用一套**能力声明**统一管理,并按任务自动推荐该用哪个。设计借鉴自 DeepSeek Harness 插件 `Codingns4DSH`(github.com/jingyi0605/Codingns4DSH),验证于 2026-09-27。

## 何时加载

- 大山问「这三个/几个 agent 有什么区别 / 该用哪个」
- 新增第 N 个外接 agent,要登记它能干什么
- 想按任务(需插话?需权限确认?)选 agent
- 有人提议「把某框架的多-agent 归一化做法搬过来」——先读本 skill 的边界判断,别做重复劳动

## 铁律:能力是真实属性,绝不伪造 ✓(最重要)

能力声明的**唯一价值**是「未声明 = 不支持,调用前先挡住」。**为了让表好看而把不支持的能力标成 ✓ = 假兼容**,调用时静默失败,比老实标 ✗ 更糟。这是 Codingns4DSH 整套设计要防的头号坑。

- 能力是底层 CLI/协议**实际具备**的属性,不是开关。
- 判定能力来源优先级:①真实往返实测 > ②同款 CLI 的已验证能力表 > ③协议推断(最弱,需标注待校准)。
- 缺的就标缺 → 选择器会把需要该能力的任务自动导向支持它的 agent。这正是它的意义。

## 大山的三个真实外接 Agent(2026-09-27 实测 + 能力表)

| 能力 | codex | claude | opencode |
|---|:---:|:---:|:---:|
| models/stream/resume/interrupt/tool-events/reasoning/usage | ✓ | ✓ | ✓ |
| permission(权限确认) | ✓ | ✗ | ✓ |
| questions(结构化提问) | ✓ | ✗ | ✓ |
| steer(回合中插话) | ✓ | ✗ | ✗ |

- **codex**(profile `codex`,内核 codex app-server,`hermes -p codex chat`):能力最全,唯一支持 steer。
- **claude**(profile `claude`,内核 Claude Code ACP):基础齐全,但**协议层面**无 permission/questions/steer——非配置可开,别硬补(见铁律)。
- **opencode**(profile `opencode`,内核 OpenCode ACP):有 permission+questions,无 steer。

实测坑:claude/opencode 往返可能因中转站瞬时故障(Cloudflare 502 / ACP 超时)超时 exit 124——**这是运行时问题,不是能力缺陷**,别据此判定能力。codex 往返稳定。

## 能不能让 claude 和 codex 一样全(大山问过)

不能。claude 缺的 permission/questions/steer 是 **Claude Code ACP 协议层面本身不暴露**的能力,不是 Hermes 端改个开关能开。硬把表标成 ✓ 只会调用时静默失败(违反铁律)。真需这些能力 → 用 codex。若将来 Claude Code 升级支持了某项,实测验证后再改声明。

## 用法

工作副本在 `workspace/projects/agent-adapter-prototype/`;本 skill 的 `scripts/` 是可移植模板。

```bash
python scripts/real_profiles.py matrix                    # 能力对照 + 任务推荐
python scripts/real_profiles.py pick steer                # 找支持插话的 → codex
python scripts/real_profiles.py pick permission questions  # → codex, opencode
```

## 新增第 4 个 agent

在 `real_profiles.py` 的 `real_profiles_registry()` 里加一条 `AgentDescriptor`:
- `id`/`name`/`protocol`/`command` 照填;
- `capabilities` 只填**实测或已验证**支持的(遵守铁律);
- 需要的话在 `TASK_REQUIREMENTS` 加「任务→所需能力」映射。
编排/选择逻辑零改动。

## 边界:什么时候「不要做」

- **不要重写 Hermes 现有 profile 的接入层**去走自建归一化。standalone profile 的 delta/snapshot 归一化、事件流,**Hermes 内核在 ACP/app-server 层已经做了**,再叠一层是冗余 + 破坏兼容风险。Codingns4DSH 需要三层是因为它要把 8 个 CLI 塞进**一个** DSH 界面;独立 profile 场景不需要。
- 本目录只做「声明 + 查询 + 推荐」,**绝不改任何 profile 的配置或运行**——纯增量、可逆、零风险。

## 三层归一化模式(仅当真要「多 agent 塞进一个界面」时才需要)

完整可运行原型在 `workspace/projects/agent-adapter-prototype/`(`capabilities.py` / `stream_normalizer.py` / `events.py` / `message_projector.py`,22 单测通过):

```
Driver(产原始事件) → 统一事件模型
  → StreamNormalizer(抹平 delta/snapshot,去重)
  → MessageProjector(工具只读历史 + usage 结算 + 终态映射 + 幂等)
  → 上层渲染(只按 kind,零 if-by-agent)
```

要点:①快照型 CLI 每次重发全文,normalizer 只发新增避免重复堆积;②工具事件是**只读历史**,绝不转成待执行工具调用;③usage 在 finish 结算。

## 用户偏好(大山)

- 全程中文;结论先行;不夸赞不复述内部过程。
- 新建/修改 skill 前先说明获同意,不先改后报。
- 交付 = 端到端实测过的可用物;卡住直说卡在哪,不粉饰;绝不编造结果。
