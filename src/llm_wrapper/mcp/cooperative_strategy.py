"""Cooperative strategies for orchestrating LLMs and MCP tools.

Defines composable patterns: parallel execution, chaining, fallback, and routing.
"""

import asyncio
import inspect
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar, Union

from mcp.types import CallToolResult


class StrategyType(Enum):
    PARALLEL = "parallel"
    CHAIN = "chain"
    FALLBACK = "fallback"
    ROUTER = "router"


@dataclass
class StrategyStep:
    """A single step in a cooperative strategy."""

    name: str
    action: Callable[[], Any]
    description: str = ""


@dataclass
class StrategyResult:
    """Result of executing a cooperative strategy."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


T = TypeVar("T")


class CooperativeStrategy:
    """Base class for cooperative strategies."""

    type: StrategyType

    async def execute(self) -> StrategyResult:
        raise NotImplementedError


class ParallelStrategy(CooperativeStrategy):
    """Execute multiple steps concurrently and collect results."""

    type = StrategyType.PARALLEL

    def __init__(
        self,
        steps: List[StrategyStep],
        gather: bool = True,
        return_on_first_error: bool = False,
    ):
        self.steps = steps
        self.gather = gather
        self.return_on_first_error = return_on_first_error

    async def execute(self) -> StrategyResult:
        if not self.steps:
            return StrategyResult(success=True, data=[])

        tasks = [asyncio.create_task(step.action()) for step in self.steps]

        if self.return_on_first_error:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            results = []
            errors = []
            for fut in done:
                try:
                    results.append(fut.result())
                except Exception as e:
                    errors.append(str(e))
            for fut in pending:
                fut.cancel()
            if errors and not results:
                return StrategyResult(success=False, error="; ".join(errors))
            return StrategyResult(
                success=True,
                data=results,
                metadata={"completed": len(results), "cancelled": len(pending)},
            )
        else:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            data = []
            errors = []
            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    errors.append(f"{self.steps[i].name}: {res}")
                else:
                    data.append(res)
            return StrategyResult(
                success=len(errors) == 0,
                data=data,
                error="; ".join(errors) if errors else None,
                metadata={"total": len(self.steps), "succeeded": len(data), "failed": len(errors)},
            )


class ChainStrategy(CooperativeStrategy):
    """Execute steps sequentially, passing previous output as context."""

    type = StrategyType.CHAIN

    def __init__(
        self,
        steps: List[StrategyStep],
        stop_on_error: bool = True,
    ):
        self.steps = steps
        self.stop_on_error = stop_on_error

    async def execute(self) -> StrategyResult:
        if not self.steps:
            return StrategyResult(success=True, data=None)

        chain_context: Dict[str, Any] = {}
        results = []

        for step in self.steps:
            try:
                result = await step.action()
                chain_context[step.name] = result
                results.append({"step": step.name, "result": result, "success": True})
            except Exception as e:
                error_msg = f"Chain failed at step '{step.name}': {e}"
                results.append({"step": step.name, "error": str(e), "success": False})
                if self.stop_on_error:
                    return StrategyResult(
                        success=False,
                        data=results,
                        error=error_msg,
                        metadata={"failed_at": step.name},
                    )

        return StrategyResult(
            success=True,
            data=results,
            metadata={"steps": len(results)},
        )


class FallbackStrategy(CooperativeStrategy):
    """Try primary action; on failure, fall back to secondary."""

    type = StrategyType.FALLBACK

    def __init__(
        self,
        primary: StrategyStep,
        fallback: StrategyStep,
        fallback_on: Optional[Sequence[type]] = None,
    ):
        self.primary = primary
        self.fallback = fallback
        self.fallback_on = fallback_on or (Exception,)

    async def execute(self) -> StrategyResult:
        try:
            result = await self.primary.action()
            return StrategyResult(
                success=True,
                data=result,
                metadata={"used": "primary", "primary_name": self.primary.name},
            )
        except Exception as e:
            if not any(isinstance(e, exc_type) for exc_type in self.fallback_on):
                raise
            try:
                fallback_result = await self.fallback.action()
                return StrategyResult(
                    success=True,
                    data=fallback_result,
                    metadata={
                        "used": "fallback",
                        "primary_error": str(e),
                        "fallback_name": self.fallback.name,
                    },
                )
            except Exception as fbe:
                return StrategyResult(
                    success=False,
                    error=f"Primary: {e}; Fallback: {fbe}",
                )


class RouterStrategy(CooperativeStrategy):
    """Route to a specific model/tool based on routing function."""

    type = StrategyType.ROUTER

    def __init__(
        self,
        routes: Dict[str, StrategyStep],
        router_fn: Callable[[], str],
        fallback_step: Optional[StrategyStep] = None,
    ):
        self.routes = routes
        self.router_fn = router_fn
        self.fallback_step = fallback_step

    async def execute(self) -> StrategyResult:
        try:
            route_key = await self.router_fn() if inspect.iscoroutinefunction(self.router_fn) else self.router_fn()
        except Exception as e:
            route_key = None

        step = self.routes.get(route_key) or self.fallback_step
        if not step:
            return StrategyResult(
                success=False,
                error=f"No route for '{route_key}' and no fallback provided",
            )

        try:
            result = await step.action()
            return StrategyResult(
                success=True,
                data=result,
                metadata={"route": route_key, "step_name": step.name},
            )
        except Exception as e:
            return StrategyResult(
                success=False,
                error=str(e),
                metadata={"route": route_key, "step_name": step.name},
            )


# --- Convenience builders ---

def parallel(
    steps: List[StrategyStep],
    return_on_first_error: bool = False,
) -> CooperativeStrategy:
    return ParallelStrategy(steps, return_on_first_error=return_on_first_error)


def chain(
    steps: List[StrategyStep],
    stop_on_error: bool = True,
) -> CooperativeStrategy:
    return ChainStrategy(steps, stop_on_error=stop_on_error)


def fallback(
    primary: StrategyStep,
    fallback_step: StrategyStep,
) -> CooperativeStrategy:
    return FallbackStrategy(primary, fallback_step)


def router(
    routes: Dict[str, StrategyStep],
    router_fn: Callable[[], str],
    fallback_step: Optional[StrategyStep] = None,
) -> CooperativeStrategy:
    return RouterStrategy(routes, router_fn, fallback_step)
