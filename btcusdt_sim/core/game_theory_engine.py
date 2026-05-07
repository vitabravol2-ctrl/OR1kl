from dataclasses import dataclass
from math import exp


PLAYERS = [
    "LONG_CROWD",
    "SHORT_CROWD",
    "MARKET_MAKER",
    "MOMENTUM_TRADERS",
    "LIQUIDITY_PROVIDERS",
    "OUR_SIMULATOR",
]

SCENARIOS = [
    "MOVE_UP",
    "MOVE_DOWN",
    "FAKE_UP_THEN_DOWN",
    "FAKE_DOWN_THEN_UP",
    "COMPRESSION_WAIT",
    "SWEEP_HIGH",
    "SWEEP_LOW",
    "RANGE_TRAP",
]


@dataclass(slots=True)
class GameDecision:
    best_scenario: str
    second_scenario: str
    confidence: float
    expected_payoff: float
    reason: str


class CrowdPainEngine:
    def evaluate(self, price: float, depth: dict, flow: dict, tactical: dict) -> dict:
        liq_imb = abs(depth.get("liquidity_imbalance", 0.0))
        stress = tactical.get("liquidity_stress", 0.0)
        pressure = abs(flow.get("pressure", 0.0)) + abs(flow.get("momentum_pulse", 0.0))
        stop_above = max(0.05, liq_imb * 0.7 + max(0.0, flow.get("pressure", 0.0)) * 0.3 + 0.1)
        stop_below = max(0.05, liq_imb * 0.7 + max(0.0, -flow.get("pressure", 0.0)) * 0.3 + 0.1)
        distance = max(price * 0.0005, 1e-6)
        reward = 1.0 + stress + pressure
        pain_above = min((stop_above * reward) / distance * 0.01, 1.5)
        pain_below = min((stop_below * reward) / distance * 0.01, 1.5)
        trapped_longs = min(max((-flow.get("momentum_pulse", 0.0) + stress * 0.5), 0.0), 1.0)
        trapped_shorts = min(max((flow.get("momentum_pulse", 0.0) + stress * 0.5), 0.0), 1.0)
        return {
            "pain_above": pain_above,
            "pain_below": pain_below,
            "stop_density_above": stop_above,
            "stop_density_below": stop_below,
            "trapped_longs": trapped_longs,
            "trapped_shorts": trapped_shorts,
            "liquidation_pressure_proxy": min((trapped_longs + trapped_shorts + stress) / 3.0, 1.0),
        }


class PlayerModelEngine:
    def evaluate(self, flow: dict, depth: dict, tactical: dict, pain: dict) -> dict:
        pressure = flow.get("pressure", 0.0)
        momentum = flow.get("momentum_pulse", 0.0)
        liq_imb = depth.get("liquidity_imbalance", 0.0)
        stress = tactical.get("liquidity_stress", 0.0)

        def mk(v: float, action: str, risk: float, payoff: float) -> dict:
            return {
                "pressure": max(min(v, 1.0), -1.0),
                "vulnerability": min(max(abs(v) * 0.7 + risk * 0.3, 0.0), 1.0),
                "likely_action": action,
                "risk_level": min(max(risk, 0.0), 1.0),
                "payoff_expectation": max(min(payoff, 1.0), -1.0),
            }

        return {
            "LONG_CROWD": mk(pressure + momentum * 0.5, "DEFEND_OR_STOP_OUT", pain["trapped_longs"], 0.3 - pain["pain_below"]),
            "SHORT_CROWD": mk(-pressure - momentum * 0.5, "DEFEND_OR_STOP_OUT", pain["trapped_shorts"], 0.3 - pain["pain_above"]),
            "MARKET_MAKER": mk(-liq_imb, "SEEK_LIQUIDITY_IMBALANCE", stress * 0.4, max(pain["pain_above"], pain["pain_below"]) - 0.2),
            "MOMENTUM_TRADERS": mk(momentum, "CHASE_BREAKOUT", min(abs(momentum) + stress * 0.2, 1.0), abs(momentum) - stress * 0.1),
            "LIQUIDITY_PROVIDERS": mk(-stress + liq_imb * 0.3, "WIDEN_OR_PULL_QUOTES", stress, 0.2 + stress * 0.4),
            "OUR_SIMULATOR": mk(tactical.get("continuation_strength", 0.0), "SELECT_BEST_PAYOFF", tactical.get("tactical_danger", 0.0), tactical.get("tactical_opportunity", 0.0) - tactical.get("tactical_danger", 0.0)),
        }


class PayoffMatrixEngine:
    def evaluate(self, tactical: dict, flow: dict, depth: dict, pain: dict, players: dict) -> dict:
        up_bias = max(flow.get("momentum_pulse", 0.0), 0.0) + max(depth.get("liquidity_imbalance", 0.0), 0.0)
        down_bias = max(-flow.get("momentum_pulse", 0.0), 0.0) + max(-depth.get("liquidity_imbalance", 0.0), 0.0)
        mm_edge = players["MARKET_MAKER"]["payoff_expectation"]

        def row(direction_edge: float, fake: float, sweep: float, trap: float) -> dict:
            reward = direction_edge + tactical.get("tactical_opportunity", 0.0) + sweep
            cost = tactical.get("liquidity_stress", 0.0) + fake * 0.6
            risk = tactical.get("tactical_danger", 0.0) + trap * 0.5
            liq_gain = sweep + max(pain["pain_above"], pain["pain_below"]) * 0.5
            crowd_pain = trap + pain["trapped_longs"] + pain["trapped_shorts"]
            mm_adv = mm_edge + sweep * 0.3 - fake * 0.2
            expected = reward - cost - risk + liq_gain * 0.4 + crowd_pain * 0.2 + mm_adv * 0.3
            return {
                "reward": reward,
                "cost": cost,
                "risk": risk,
                "liquidity_gain": liq_gain,
                "crowd_pain": crowd_pain,
                "market_maker_advantage": mm_adv,
                "expected_payoff": expected,
            }

        return {
            "MOVE_UP": row(up_bias, 0.1, pain["pain_above"], pain["trapped_shorts"] * 0.6),
            "MOVE_DOWN": row(down_bias, 0.1, pain["pain_below"], pain["trapped_longs"] * 0.6),
            "FAKE_UP_THEN_DOWN": row(down_bias * 0.8, 0.8, pain["pain_above"] * 0.8, pain["trapped_longs"]),
            "FAKE_DOWN_THEN_UP": row(up_bias * 0.8, 0.8, pain["pain_below"] * 0.8, pain["trapped_shorts"]),
            "COMPRESSION_WAIT": row(0.2, 0.0, 0.1, 0.0),
            "SWEEP_HIGH": row(up_bias * 0.7, 0.2, pain["pain_above"] * 1.2, pain["trapped_shorts"] * 0.5),
            "SWEEP_LOW": row(down_bias * 0.7, 0.2, pain["pain_below"] * 1.2, pain["trapped_longs"] * 0.5),
            "RANGE_TRAP": row(0.3, 0.4, 0.2, max(pain["trapped_longs"], pain["trapped_shorts"])),
        }


class GameDecisionEngine:
    def decide(self, matrix: dict, pain: dict, players: dict) -> GameDecision:
        ranked = sorted(matrix.items(), key=lambda x: x[1]["expected_payoff"], reverse=True)
        best_name, best_data = ranked[0]
        second_name, second_data = ranked[1]
        spread = best_data["expected_payoff"] - second_data["expected_payoff"]
        confidence = 1.0 / (1.0 + exp(-spread * 3.0))
        trapped_side = "LONGS" if pain["trapped_longs"] > pain["trapped_shorts"] else "SHORTS"
        reason = (
            f"{trapped_side.lower()} vulnerable + liquidity {'below' if pain['pain_below'] > pain['pain_above'] else 'above'}"
            f" + mm_edge={players['MARKET_MAKER']['payoff_expectation']:.2f}"
        )
        return GameDecision(best_name, second_name, confidence, best_data["expected_payoff"], reason)


class GameTheoryCore:
    def __init__(self) -> None:
        self.pain_engine = CrowdPainEngine()
        self.player_engine = PlayerModelEngine()
        self.payoff_engine = PayoffMatrixEngine()
        self.decision_engine = GameDecisionEngine()

    def evaluate(self, price: float, tactical: dict, flow: dict, depth: dict) -> dict:
        pain = self.pain_engine.evaluate(price, depth, flow, tactical)
        players = self.player_engine.evaluate(flow, depth, tactical, pain)
        matrix = self.payoff_engine.evaluate(tactical, flow, depth, pain, players)
        decision = self.decision_engine.decide(matrix, pain, players)
        return {
            "pain": pain,
            "players": players,
            "payoff_matrix": matrix,
            "decision": {
                "best_scenario": decision.best_scenario,
                "second_scenario": decision.second_scenario,
                "confidence": decision.confidence,
                "expected_payoff": decision.expected_payoff,
                "reason": decision.reason,
            },
            "trapped_side": "LONGS" if pain["trapped_longs"] > pain["trapped_shorts"] else "SHORTS",
            "market_maker_incentive": players["MARKET_MAKER"]["payoff_expectation"],
        }
