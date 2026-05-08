import unittest

from btcusdt_sim.core.micro_tick_setup_engine import MicroTickSetupEngine


class TestMicroTickSetupEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = MicroTickSetupEngine()

    def _base(self):
        tactical = {
            "pressure_direction": "UP",
            "tactical_opportunity": 0.8,
            "tactical_danger": 0.2,
            "liquidity_stress": 0.4,
            "absorption_status": "BUY_ABSORPTION",
            "state": "TREND_CONTINUATION",
        }
        game = {
            "trapped_side": "SHORTS",
            "decision": {"confidence": 0.75, "best_scenario": "MOVE_UP"},
            "intent": {"intent": "BAIT_SHORTS"},
            "intent_reality": {"reality": "WEAK_RESPONSE"},
        }
        return tactical, game

    def test_long_decision_when_all_aligned(self):
        tactical, game = self._base()
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertEqual(r.direction, "LONG")

    def test_short_decision_when_all_aligned(self):
        tactical, game = self._base()
        tactical["pressure_direction"] = "DOWN"
        game["trapped_side"] = "LONGS"
        game["decision"]["best_scenario"] = "MOVE_DOWN"
        game["intent"]["intent"] = "BAIT_LONGS"
        tactical["absorption_status"] = "SELL_ABSORPTION"
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertEqual(r.direction, "SHORT")

    def test_wait_when_spread_too_wide(self):
        tactical, game = self._base()
        r = self.engine.evaluate(100.0, 101.0, tactical, game, ws_fresh=True)
        self.assertEqual(r.direction, "WAIT")

    def test_wait_when_confidence_low(self):
        tactical, game = self._base()
        game["decision"]["confidence"] = 0.4
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertEqual(r.direction, "WAIT")

    def test_wait_when_signal_conflict(self):
        tactical, game = self._base()
        game["decision"]["best_scenario"] = "COMPRESSION_WAIT"
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertEqual(r.direction, "WAIT")

    def test_ev_calculation_correctness(self):
        tactical, game = self._base()
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertGreater(r.ev_estimate, 0.0)

    def test_target_invalidation_price_correctness(self):
        tactical, game = self._base()
        r = self.engine.evaluate(100.0, 100.1, tactical, game, ws_fresh=True)
        self.assertEqual(r.entry_candidate, 100.1)
        self.assertAlmostEqual(r.target_price, 100.2)
        self.assertAlmostEqual(r.target_price_2, 100.3)
        self.assertAlmostEqual(r.invalidation_price, 99.9)


if __name__ == "__main__":
    unittest.main()
