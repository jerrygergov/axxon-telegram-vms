import unittest
from pathlib import Path


class CounterWatchSubscribeFlowTests(unittest.TestCase):
    def test_subscribe_flow_contains_counter_detector_branch(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('source="counter_detector"', src)
        self.assertIn('await COUNTER_WATCH.start_subscription(rec, context.bot, row', src)
        self.assertIn('"detector_rows": selected_rows', src)

    def test_counterwatch_command_redirects_to_subscribe(self):
        src = Path("scripts/axxon_tg_bot.py").read_text(encoding="utf-8")
        self.assertIn('Counter watch now lives inside /subscribe', src)


if __name__ == "__main__":
    unittest.main()
