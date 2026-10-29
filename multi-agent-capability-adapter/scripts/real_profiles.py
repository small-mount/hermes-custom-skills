# -*- coding: utf-8 -*-
"""大山的三个真实 Hermes 外接 Agent 的能力目录 + 任务选择器。

✅ 只做「声明 + 查询 + 推荐」，绝不修改任何 profile 的配置或运行。
能力值来源：Codingns4DSH 经验证能力表 + 2026-09-27 本地实测（codex 往返成功）。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capabilities import (  # noqa: E402
    Capability as C, Protocol, AgentDescriptor, AgentRegistry,
)


def real_profiles_registry() -> AgentRegistry:
    reg = AgentRegistry()
    reg.register(AgentDescriptor(
        id="codex", name="Codex (app-server)", protocol=Protocol.JSON_RPC,
        capabilities=frozenset({
            C.MODELS, C.STREAM, C.RESUME, C.INTERRUPT, C.TOOL_EVENTS,
            C.REASONING, C.USAGE, C.PERMISSION, C.QUESTIONS, C.STEER,
        }),
        installed=True, version="app-server", command="hermes -p codex chat",
    ))
    reg.register(AgentDescriptor(
        id="claude", name="Claude Code (ACP)", protocol=Protocol.STREAM_JSON,
        capabilities=frozenset({
            C.MODELS, C.STREAM, C.RESUME, C.INTERRUPT, C.TOOL_EVENTS,
            C.REASONING, C.USAGE,
        }),
        installed=True, version="acp", command="hermes -p claude chat",
    ))
    reg.register(AgentDescriptor(
        id="opencode", name="OpenCode (ACP)", protocol=Protocol.HTTP_SSE,
        capabilities=frozenset({
            C.MODELS, C.STREAM, C.RESUME, C.INTERRUPT, C.TOOL_EVENTS,
            C.REASONING, C.USAGE, C.PERMISSION, C.QUESTIONS,
        }),
        installed=True, version="acp", command="hermes -p opencode chat",
    ))
    return reg


TASK_REQUIREMENTS = {
    "长任务需中途插话": {C.STEER},
    "需要人工权限确认的敏感操作": {C.PERMISSION},
    "会向你提问澄清的交互式任务": {C.QUESTIONS},
    "需要恢复中断的长会话": {C.RESUME},
    "看推理过程的思考型任务": {C.REASONING},
    "普通编码任务": {C.STREAM, C.TOOL_EVENTS},
}


def recommend(reg: AgentRegistry, needed: set) -> list:
    hits = [a for a in reg._agents.values() if needed.issubset(a.capabilities)]
    return sorted(hits, key=lambda a: len(a.capabilities), reverse=True)


def print_matrix(reg: AgentRegistry) -> None:
    ids = ["codex", "claude", "opencode"]
    print(f"{'能力':<14}" + "".join(f"{i:<11}" for i in ids))
    print("-" * 50)
    for cap in list(C):
        row = f"{cap.value:<14}"
        for i in ids:
            row += f"{'  ✓' if reg.get(i).supports(cap) else '  ✗':<11}"
        print(row)


def main() -> None:
    reg = real_profiles_registry()
    args = sys.argv[1:]
    if not args or args[0] == "matrix":
        print("=== 三个外接 Agent 能力对照 ===\n")
        print_matrix(reg)
        print("\n=== 按任务推荐 ===\n")
        for task, needed in TASK_REQUIREMENTS.items():
            hits = recommend(reg, needed)
            names = ", ".join(a.id for a in hits) if hits else "（无）"
            need_s = "+".join(c.value for c in needed)
            print(f"  {task:<24} 需[{need_s:<18}] → {names}")
        return
    if args[0] == "pick" and len(args) > 1:
        try:
            needed = {C(x) for x in args[1:]}
        except ValueError as e:
            print(f"未知能力: {e}. 可用: {[c.value for c in C]}")
            return
        hits = recommend(reg, needed)
        if hits:
            print("推荐（能力最全在前）:")
            for a in hits:
                print(f"  {a.id:<10} {a.command}")
        else:
            print("没有 agent 同时满足这些能力。")
        return
    print("用法: python real_profiles.py [matrix | pick <cap> <cap> ...]")


if __name__ == "__main__":
    main()
