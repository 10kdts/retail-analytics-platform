import unittest

from src.retail_data.reliability import RetryPolicy, retry


class RetryTests(unittest.TestCase):
    def test_operation_is_retried_until_success(self) -> None:
        calls = []
        delays = []

        def flaky_operation() -> str:
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("indisponível")
            return "ok"

        result = retry(
            flaky_operation,
            RetryPolicy(max_attempts=3, initial_delay_seconds=0.5),
            retryable=lambda error: isinstance(error, ConnectionError),
            sleep=delays.append,
        )
        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [0.5, 1.0])

    def test_non_retryable_error_fails_immediately(self) -> None:
        calls = []

        def invalid_data() -> None:
            calls.append(1)
            raise ValueError("dado inválido")

        with self.assertRaises(ValueError):
            retry(
                invalid_data,
                RetryPolicy(max_attempts=3),
                retryable=lambda error: isinstance(error, ConnectionError),
                sleep=lambda _: None,
            )
        self.assertEqual(len(calls), 1)
