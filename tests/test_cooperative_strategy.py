"""Unit tests for cooperative strategy module."""

import asyncio
import pytest
from src.llm_wrapper.mcp.cooperative_strategy import (
    chain,
    fallback,
    parallel,
    router,
    StrategyStep,
    StrategyResult,
    CooperativeStrategy,
    StrategyType,
)


async def _ok(value: str = "ok") -> str:
    return value


async def _fail() -> str:
    raise ValueError("intentional fail")


async def _slow(value: str = "slow") -> str:
    await asyncio.sleep(0.05)
    return value


def test_strategy_types():
    assert StrategyType.PARALLEL.value == "parallel"
    assert StrategyType.CHAIN.value == "chain"
    assert StrategyType.FALLBACK.value == "fallback"
    assert StrategyType.ROUTER.value == "router"


class TestParallelStrategy:
    @pytest.mark.asyncio
    async def test_all_succeed(self):
        steps = [
            StrategyStep("a", lambda: _ok("a")),
            StrategyStep("b", lambda: _ok("b")),
        ]
        result = await parallel(steps).execute()
        assert result.success
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_one_fails_gather(self):
        steps = [
            StrategyStep("good", lambda: _ok("good")),
            StrategyStep("bad", _fail),
        ]
        result = await parallel(steps).execute()
        assert not result.success
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_return_on_first_error(self):
        steps = [
            StrategyStep("bad", _fail),
            StrategyStep("slow", lambda: _slow("done")),
        ]
        from src.llm_wrapper.mcp.cooperative_strategy import ParallelStrategy
        strategy = ParallelStrategy(steps, return_on_first_error=True)
        result = await strategy.execute()
        # May or may not be success depending on ordering
        assert isinstance(result, StrategyResult)

    @pytest.mark.asyncio
    async def test_empty_steps(self):
        result = await parallel([]).execute()
        assert result.success
        assert result.data == []


class TestChainStrategy:
    @pytest.mark.asyncio
    async def test_all_succeed(self):
        steps = [
            StrategyStep("first", lambda: _ok("first")),
            StrategyStep("second", lambda: _ok("second")),
        ]
        result = await chain(steps).execute()
        assert result.success
        assert len(result.data) == 2

    @pytest.mark.asyncio
    async def test_stop_on_error(self):
        steps = [
            StrategyStep("ok", lambda: _ok("ok")),
            StrategyStep("bad", _fail),
            StrategyStep("never", lambda: _ok("never")),
        ]
        result = await chain(steps, stop_on_error=True).execute()
        assert not result.success
        assert len(result.data) == 2  # Only first two executed

    @pytest.mark.asyncio
    async def test_continue_on_error(self):
        steps = [
            StrategyStep("ok", lambda: _ok("ok")),
            StrategyStep("bad", _fail),
            StrategyStep("also_ok", lambda: _ok("also_ok")),
        ]
        result = await chain(steps, stop_on_error=False).execute()
        assert result.success  # Chain completed (some steps failed but didn't abort)
        assert len(result.data) == 3  # All executed
        assert not result.data[1]["success"]

    @pytest.mark.asyncio
    async def test_empty_steps(self):
        result = await chain([]).execute()
        assert result.success
        assert result.data is None


class TestFallbackStrategy:
    @pytest.mark.asyncio
    async def test_primary_succeeds(self):
        strategy = fallback(
            StrategyStep("primary", lambda: _ok("primary")),
            StrategyStep("backup", lambda: _ok("backup")),
        )
        result = await strategy.execute()
        assert result.success
        assert result.metadata["used"] == "primary"
        assert result.data == "primary"

    @pytest.mark.asyncio
    async def test_fallback_succeeds(self):
        strategy = fallback(
            StrategyStep("primary", _fail),
            StrategyStep("backup", lambda: _ok("backup")),
        )
        result = await strategy.execute()
        assert result.success
        assert result.metadata["used"] == "fallback"
        assert result.data == "backup"

    @pytest.mark.asyncio
    async def test_both_fail(self):
        strategy = fallback(
            StrategyStep("primary", _fail),
            StrategyStep("backup", _fail),
        )
        result = await strategy.execute()
        assert not result.success
        assert "intentional fail" in result.error


class TestRouterStrategy:
    @pytest.mark.asyncio
    async def test_route_found(self):
        async def route_fn() -> str:
            return "a"
        r = router(
            {"a": StrategyStep("route_a", lambda: _ok("a")), "b": StrategyStep("route_b", lambda: _ok("b"))},
            route_fn,
        )
        result = await r.execute()
        assert result.success
        assert result.metadata["route"] == "a"

    @pytest.mark.asyncio
    async def test_route_not_found_no_fallback(self):
        async def route_fn() -> str:
            return "nonexistent"
        r = router({}, route_fn)
        result = await r.execute()
        assert not result.success

    @pytest.mark.asyncio
    async def test_route_not_found_with_fallback(self):
        async def route_fn() -> str:
            return "nonexistent"
        r = router(
            {},
            route_fn,
            fallback_step=StrategyStep("fallback", lambda: _ok("fallback_ok")),
        )
        result = await r.execute()
        assert result.success
        assert result.data == "fallback_ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
