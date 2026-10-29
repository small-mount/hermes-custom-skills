# -*- coding: utf-8 -*-
"""能力声明式 Agent 注册表（借鉴 Codingns4DSH 的 driver.ts / cli-adapter.ts）。

核心约束：未声明的能力一律按「不支持」处理（never assume）。
上层只依据声明分支，不写 if agent_id == 'xxx' 硬编码。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class Capability(str, Enum):
    MODELS = "models"
    STREAM = "stream"
    RESUME = "resume"
    INTERRUPT = "interrupt"
    TOOL_EVENTS = "tool-events"
    REASONING = "reasoning"
    USAGE = "usage"
    PERMISSION = "permission"
    QUESTIONS = "questions"
    STEER = "steer"


class Protocol(str, Enum):
    COMMAND = "command"
    STREAM_JSON = "stream-json"
    JSON_RPC = "json-rpc"
    ACP = "acp"
    HTTP_SSE = "http-sse"


@dataclass(frozen=True)
class AgentDescriptor:
    id: str
    name: str
    protocol: Protocol
    capabilities: frozenset
    installed: bool = False
    version: Union[str, None] = None
    command: Union[str, None] = None

    def supports(self, capability: Capability) -> bool:
        """未声明 == 不支持。防「假兼容」的关键约束。"""
        return capability in self.capabilities


class CapabilityError(RuntimeError):
    def __init__(self, agent_id: str, capability: Capability) -> None:
        super().__init__(f"Agent '{agent_id}' 未声明能力 '{capability.value}'")
        self.agent_id = agent_id
        self.capability = capability


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict = {}

    def register(self, descriptor: AgentDescriptor) -> None:
        self._agents[descriptor.id] = descriptor

    def get(self, agent_id: str):
        return self._agents.get(agent_id)

    def list_installed(self) -> list:
        return [a for a in self._agents.values() if a.installed]

    def agents_supporting(self, capability: Capability) -> list:
        return [a for a in self._agents.values() if a.supports(capability)]

    def require(self, agent_id: str, capability: Capability) -> None:
        agent = self.get(agent_id)
        if agent is None:
            raise KeyError(f"未知 Agent: {agent_id}")
        if not agent.supports(capability):
            raise CapabilityError(agent_id, capability)
