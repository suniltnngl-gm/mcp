# src/llm_wrapper/mcp/resilience.py

import asyncio
import random
import time
from typing import Callable, Any, Awaitable, Optional


class CircuitBreaker:
    """
    Implements a Circuit Breaker pattern to prevent cascading failures.
    States:
        - CLOSED: Operations are allowed. If failures exceed threshold, opens circuit.
        - OPEN: Operations are blocked. After a timeout, transitions to HALF_OPEN.
        - HALF_OPEN: A single trial operation is allowed. If successful, closes circuit.
                     If failed, opens circuit again.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        reset_timeout: int = 30,
        service_name: str = "Service",
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = (
            reset_timeout  # Time in seconds to stay OPEN before HALF_OPEN
        )
        self.service_name = service_name

        self._failures = 0
        self._last_failure_time = 0
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = asyncio.Lock()  # To protect state changes in async context

    @property
    def state(self) -> str:
        return self._state

    async def _check_state_transition(self):
        """Manages transitions between OPEN and HALF_OPEN states."""
        if self._state == "OPEN":
            if time.monotonic() - self._last_failure_time > self.reset_timeout:
                print(
                    f"[{self.service_name} Circuit Breaker]: Reset timeout passed. Transitioning to HALF_OPEN."
                )
                self._state = "HALF_OPEN"
        # HALF_OPEN state doesn't transition automatically, it waits for a trial

    async def record_success(self):
        async with self._lock:
            if self._state == "HALF_OPEN":
                print(
                    f"[{self.service_name} Circuit Breaker]: Trial operation successful. Closing circuit."
                )
                self._state = "CLOSED"
            self._failures = 0  # Reset failures on success

    async def record_failure(self):
        async with self._lock:
            self._failures += 1
            self._last_failure_time = time.monotonic()
            if self._state == "HALF_OPEN" or self._failures >= self.failure_threshold:
                if self._state != "OPEN":  # Avoid duplicate open message
                    print(
                        f"[{self.service_name} Circuit Breaker]: Failures ({self._failures}) exceeded threshold ({self.failure_threshold}). Opening circuit."
                    )
                self._state = "OPEN"

    async def __call__(
        self, func: Callable[..., Awaitable[Any]], *args, **kwargs
    ) -> Any:
        """
        Decorator-like usage for circuit breaker.
        Checks circuit state before executing the function.
        """
        async with self._lock:
            await self._check_state_transition()  # Check for state transition first

            if self._state == "OPEN":
                remaining_time = int(
                    self.reset_timeout - (time.monotonic() - self._last_failure_time)
                )
                raise CircuitBreakerOpenError(
                    f"[{self.service_name} Circuit Breaker]: Circuit is OPEN. Operations blocked. "
                    f"Will attempt reset in {max(0, remaining_time)}s."
                )
            # If HALF_OPEN or CLOSED, proceed with the call

        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise e


class CircuitBreakerOpenError(Exception):
    """Custom exception raised when the circuit breaker is open."""

    pass


async def retry_with_backoff(
    func: Callable[..., Awaitable[Any]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    jitter: float = 0.1,
    catch_exceptions: tuple = (
        asyncio.TimeoutError,
        ConnectionError,
        IOError,
    ),  # Added IOError for broader network issues
    on_retry_callback: Optional[Callable[[int, Exception, float], None]] = None,
) -> Any:
    """
    Retries an async function with exponential backoff and jitter.

    Args:
        func: The async function to retry.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds before the first retry.
        max_delay: Maximum delay between retries.
        jitter: Random factor to add to the delay (0.0 to 1.0).
        catch_exceptions: Tuple of exceptions to catch and retry on.
        on_retry_callback: A callback function (retry_num, exception, delay) called before each retry.

    Returns:
        The result of the function if successful.

    Raises:
        The last exception caught if all retries fail.
    """
    delay = initial_delay
    last_exception = None

    for i in range(max_retries + 1):
        try:
            return await func()
        except catch_exceptions as e:
            last_exception = e
            if i < max_retries:
                sleep_time = min(
                    delay * (2**i) + random.uniform(0, delay * jitter), max_delay
                )
                if on_retry_callback:
                    on_retry_callback(i + 1, e, sleep_time)
                print(
                    f"Retry {i + 1}/{max_retries} for {func.__name__}. Waiting {sleep_time:.2f}s due to {e.__class__.__name__}."
                )
                await asyncio.sleep(sleep_time)
            else:
                break  # Max retries reached
        except Exception as e:
            # For other unexpected exceptions, re-raise immediately
            raise e

    if last_exception:
        raise last_exception
    else:
        # Should not happen if loop completes without success and no exception, but defensive
        raise RuntimeError(
            f"Function {func.__name__} failed after {max_retries} retries without catching expected exceptions."
        )


if __name__ == "__main__":

    async def _test_func_success_after_retries(
        attempt: int, fail_until_attempt: int
    ) -> str:
        if attempt < fail_until_attempt:
            print(f"  Test Func: Attempt {attempt} failed.")
            raise ConnectionError("Simulated network issue")
        print(f"  Test Func: Attempt {attempt} successful!")
        return "Success!"

    async def _test_func_always_fail(msg: str) -> str:
        print(f"  Test Func (always fail): {msg} - Failing now.")
        raise ConnectionError("Simulated permanent failure")

    async def _test_func_timeout(delay: float):
        print(f"  Test Func (timeout): Starting long operation ({delay}s).")
        await asyncio.sleep(delay)
        print("  Test Func (timeout): Operation finished.")
        return "Timeout test success"

    async def main():
        print("--- Testing Resilience Module ---")

        # --- Test Circuit Breaker ---
        print("\n--- Circuit Breaker Test (service 'MyService') ---")
        cb = CircuitBreaker(
            failure_threshold=2, reset_timeout=5, service_name="MyService"
        )

        async def protected_call_logic(sim_fail: bool = False, msg: str = "Work"):
            if sim_fail:
                await _test_func_always_fail(msg=msg)  # This will raise
            return f"{msg} done."

        # Should work
        await cb(protected_call_logic, msg="Initial Call")

        # Simulate failures to open circuit
        print("\nSimulating failures to open circuit:")
        for i in range(1, 4):  # Attempt 3 times, 2 failures + 1 to hit threshold
            try:
                await cb(protected_call_logic, sim_fail=True, msg=f"Failure {i}")
            except ConnectionError:
                pass
            except CircuitBreakerOpenError as e:
                print(f"  Caught: {e}")
            print(f"  After failure {i}. Circuit: {cb.state}, Failures: {cb._failures}")

        await cb(protected_call_logic, msg="Call while OPEN (should be blocked)")

        print(f"\nWaiting for reset timeout ({cb.reset_timeout}s) to go HALF_OPEN...")
        await asyncio.sleep(cb.reset_timeout + 1)

        # Test HALF_OPEN - trial success
        print("\nTesting HALF_OPEN: Trial SUCCESS (should close circuit):")
        try:
            await cb(protected_call_logic, msg="Trial 1 (Success)")
            print(f"  Trial success. Circuit: {cb.state}")  # Should be CLOSED
        except Exception as e:
            print(f"  Trial failed: {e}. Circuit: {cb.state}")

        # Test HALF_OPEN - trial failure
        print("\nTesting HALF_OPEN: Trial FAILURE (should open circuit again):")
        cb = CircuitBreaker(
            failure_threshold=2, reset_timeout=5, service_name="MyService"
        )  # Reset CB for this test
        for _ in range(cb.failure_threshold):
            try:
                await cb(protected_call_logic, sim_fail=True, msg="Pre-open failure")
            except ConnectionError:
                pass
        await asyncio.sleep(cb.reset_timeout + 1)  # To HALF_OPEN

        try:
            await cb(
                protected_call_logic, sim_fail=True, msg="Trial 2 (Failure)"
            )  # Fail the trial
        except ConnectionError:
            pass
        except CircuitBreakerOpenError as e:
            print(f"  Caught: {e}")
        print(f"  Trial failed. Circuit: {cb.state}")  # Should be OPEN again

        # --- Test Retry with Backoff ---
        print("\n--- Retry with Backoff Test ---")

        def retry_callback(retry_num, exception, delay):
            print(
                f"  Retry Callback: Attempt {retry_num} due to {exception.__class__.__name__}. Next delay {delay:.2f}s."
            )

        print("\nTesting func that succeeds on 3rd attempt:")
        test_counter = 0

        async def func_succeeds_on_3rd_attempt():
            nonlocal test_counter
            test_counter += 1
            return await _test_func_success_after_retries(test_counter, 3)

        try:
            result = await retry_with_backoff(
                func_succeeds_on_3rd_attempt,
                max_retries=5,
                on_retry_callback=retry_callback,
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Failed after retries: {e}")

        print("\nTesting func that always fails:")
        try:
            # Need to wrap _test_func_always_fail in a lambda to pass without args
            await retry_with_backoff(
                lambda: _test_func_always_fail(msg="always fails func"),
                max_retries=2,
                on_retry_callback=retry_callback,
            )
        except Exception as e:
            print(f"Correctly failed after retries: {e.__class__.__name__}")

        # --- Test Timeout Enforcement (conceptual - actual integration will use asyncio.wait_for) ---
        print("\n--- Timeout Enforcement (Conceptual) ---")
        print(
            "This is primarily handled by asyncio.wait_for around tool calls in MultiClientManager."
        )
        try:
            print("  Attempting a 1s operation with 0.5s timeout...")
            await asyncio.wait_for(_test_func_timeout(1.0), timeout=0.5)
            print("  Unexpected success (timeout should have occurred).")
        except asyncio.TimeoutError:
            print("  Correctly caught asyncio.TimeoutError.")
        except Exception as e:
            print(f"  Unexpected error: {e}")

    asyncio.run(main())
