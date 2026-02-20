import unittest
from typing import Any

from eddlogger import EddLogger, LogOptions
from eddlogger.drivers import BaseDriver, ConsoleDriver


class MockDriver(BaseDriver):
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self.closed = False

    def send(self, record: dict[str, Any]) -> str:
        self.records.append(record)
        return "mock-id"

    def close(self) -> None:
        self.closed = True


class LoggerTests(unittest.TestCase):
    def test_new_logger(self) -> None:
        logger = EddLogger("test-service")
        self.assertEqual(logger.service, "test-service")

    def test_log_with_mock_driver(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)

        record_id = logger.log(
            LogOptions(trace_id="test-trace-001", action="TEST_ACTION", context="TestContext")
        )

        self.assertEqual(record_id, "mock-id")
        self.assertEqual(len(mock_driver.records), 1)
        record = mock_driver.records[0]
        self.assertEqual(record["traceId"], "test-trace-001")
        self.assertEqual(record["action"], "TEST_ACTION")
        self.assertEqual(record["context"], "TestContext")

    def test_log_with_request_response(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)

        record_id = logger.log(
            LogOptions(
                trace_id="test-trace-002",
                action="API_CALL",
                method="POST",
                path="/api/test",
                request_body={"key": "value"},
                status_code=200,
                response_body={"result": "success"},
                duration_ms=123.45,
            )
        )

        self.assertEqual(record_id, "mock-id")
        record = mock_driver.records[0]
        self.assertEqual(record["request"]["method"], "POST")
        self.assertEqual(record["request"]["path"], "/api/test")
        self.assertEqual(record["response"]["statusCode"], 200)
        self.assertEqual(record["durationMs"], 123.45)

    def test_log_with_tags(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)

        tags = ["tag1", "tag2", "tag3"]
        logger.log(LogOptions(trace_id="test-trace-003", action="TAGGED_ACTION", tags=tags))

        record = mock_driver.records[0]
        self.assertIsInstance(record["tags"], list)
        self.assertEqual(len(record["tags"]), len(tags))

    def test_log_default_level(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)

        logger.log(LogOptions(trace_id="test-trace-004", action="DEFAULT_LEVEL"))
        record = mock_driver.records[0]
        self.assertEqual(record["level"], "INFO")

    def test_log_custom_level(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)

        logger.log(LogOptions(trace_id="test-trace-005", action="ERROR_ACTION", level="ERROR"))
        record = mock_driver.records[0]
        self.assertEqual(record["level"], "ERROR")

    def test_console_driver(self) -> None:
        driver = ConsoleDriver()
        record = {"traceId": "console-test", "action": "CONSOLE_TEST"}
        record_id = driver.send(record)
        self.assertEqual(record_id, "console-log")

    def test_close_logger(self) -> None:
        logger = EddLogger("test-service")
        mock_driver = MockDriver()
        logger.set_driver(mock_driver)
        logger.close()
        self.assertTrue(mock_driver.closed)


if __name__ == "__main__":
    unittest.main()
