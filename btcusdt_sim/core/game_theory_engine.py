from collections import deque
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

INTENTS = [
    "BAIT_LONGS",
    "BAIT_SHORTS",
    "SWEEP_FOR_LIQUIDITY",
    "ACCEPT_HIGHER",
    "ACCEPT_LOWER",
    "FAKE_BREAKOUT",
    "RANGE_MANIPULATION",
    "MOMENTUM_HUNT",
    "EXHAUSTION_ROTATION",
    "PANIC_EXTRACTION",
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


class MarketIntentEngine:
    def __init__(self) -> None:
        self._intent = "RANGE_MANIPULATION"
        self._confidence = 0.4
        self._duration = 0

    def evaluate(self, tactical: dict, flow: dict, depth: dict, reaction: dict, pain: dict) -> dict:
        pressure = flow.get("pressure", 0.0)
        momentum = flow.get("momentum_pulse", 0.0)
        stress = tactical.get("liquidity_stress", 0.0)
        rej = reaction.get("rejection_strength", 0.0)
        imbalance = depth.get("liquidity_imbalance", 0.0)
        trap_score = max(pain.get("trapped_longs", 0.0), pain.get("trapped_shorts", 0.0))

        scores = {
            "BAIT_LONGS": max(-momentum, 0.0) + max(-pressure, 0.0) + pain.get("trapped_longs", 0.0),
            "BAIT_SHORTS": max(momentum, 0.0) + max(pressure, 0.0) + pain.get("trapped_shorts", 0.0),
            "SWEEP_FOR_LIQUIDITY": stress + abs(imbalance) + max(pain.get("pain_above", 0.0), pain.get("pain_below", 0.0)),
            "ACCEPT_HIGHER": max(momentum, 0.0) + max(pressure, 0.0) + reaction.get("continuation_probability", 0.0),
            "ACCEPT_LOWER": max(-momentum, 0.0) + max(-pressure, 0.0) + reaction.get("continuation_probability", 0.0),
            "FAKE_BREAKOUT": tactical.get("fake_pressure_warning", 0.0) + rej,
            "RANGE_MANIPULATION": (1.0 - abs(momentum)) + tactical.get("tactical_danger", 0.0) * 0.4,
            "MOMENTUM_HUNT": abs(momentum) + abs(pressure) + tactical.get("continuation_strength", 0.0),
            "EXHAUSTION_ROTATION": tactical.get("tactical_danger", 0.0) + tactical.get("liquidity_stress", 0.0) + max(0.0, 0.7 - reaction.get("reaction_speed", 0.0)),
            "PANIC_EXTRACTION": tactical.get("tactical_danger", 0.0) + stress + trap_score,
        }

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        intent, score = ranked[0]
        second = ranked[1][1]
        raw_conf = max(min((score - second + score) / 3.0, 1.0), 0.0)
        if intent == self._intent:
            self._duration += 1
        elif raw_conf > self._confidence + 0.08:
            self._intent = intent
            self._duration = 1
        else:
            intent = self._intent
            self._duration += 1
        self._confidence = self._confidence * 0.7 + raw_conf * 0.3
        return {
            "intent": intent,
            "confidence": self._confidence,
            "persistence": min(self._duration / 14.0, 1.0),
            "tactical_pressure": min((abs(pressure) + stress + abs(momentum)) / 2.0, 1.0),
            "supporting_signals": sorted(scores, key=scores.get, reverse=True)[:3],
        }


class ScenarioEvolutionEngine:
    def __init__(self) -> None:
        self.flow = deque(maxlen=36)

    def update(self, scenario: str, confidence: float) -> dict:
        prev = self.flow[-1]["scenario"] if self.flow else scenario
        self.flow.append({"scenario": scenario, "confidence": confidence})
        persistence = sum(1 for x in reversed(self.flow) if x["scenario"] == scenario) / max(len(self.flow), 1)
        failed = prev != scenario and confidence < 0.5
        return {
            "strengthening": scenario,
            "collapsing": prev if failed else "NONE",
            "transition": f"{prev} -> {scenario}" if prev != scenario else f"{scenario} -> {scenario}",
            "persistence": persistence,
            "failed_scenario": prev if failed else "NONE",
            "flow": [x["scenario"] for x in list(self.flow)[-8:]],
        }


class IntentRealityEngine:
    def evaluate(self, intent: dict, tactical: dict, reaction: dict) -> dict:
        tried = intent.get("intent", "RANGE_MANIPULATION")
        if tried in {"ACCEPT_LOWER", "BAIT_LONGS"} and reaction.get("state") in {"REJECTION", "FAST_ACCEPTANCE"}:
            reality = "FAST_REJECTION"
            verdict = "bear weakness"
        elif tried in {"ACCEPT_HIGHER", "BAIT_SHORTS"} and reaction.get("state") in {"FAILED_BREAK", "REJECTION"}:
            reality = "FAILED_CONTINUATION"
            verdict = "bull weakness"
        else:
            reality = reaction.get("state", "WEAK_RESPONSE")
            verdict = "intent aligned"
        inversion = 1.0 if verdict != "intent aligned" else 0.0
        return {"intent": tried, "reality": reality, "verdict": verdict, "inversion_risk": inversion}


class TrapAnalyzer:
    def evaluate(self, pain: dict, tactical: dict, intent_reality: dict) -> dict:
        long_trap = min(pain.get("trapped_longs", 0.0) + tactical.get("fake_pressure_warning", 0.0) * 0.4, 1.0)
        short_trap = min(pain.get("trapped_shorts", 0.0) + tactical.get("fake_pressure_warning", 0.0) * 0.4, 1.0)
        failed_momentum = min(tactical.get("tactical_danger", 0.0) + intent_reality.get("inversion_risk", 0.0) * 0.5, 1.0)
        severity = min((long_trap + short_trap + failed_momentum) / 3.0, 1.0)
        likely_pain = "LONGS" if long_trap > short_trap else "SHORTS"
        return {
            "long_trap_probability": long_trap,
            "short_trap_probability": short_trap,
            "fake_continuation": tactical.get("fake_pressure_warning", 0.0),
            "failed_momentum": failed_momentum,
            "trapped_crowd_severity": severity,
            "likely_pain_direction": likely_pain,
        }


class PayoffEvolutionEngine:
    def __init__(self) -> None:
        self._last = 0.0

    def update(self, payoff: float, scenario_persistence: float) -> dict:
        delta = payoff - self._last
        self._last = self._last * 0.65 + payoff * 0.35
        return {
            "payoff_growth": max(delta, 0.0),
            "payoff_collapse": max(-delta, 0.0),
            "scenario_decay": max(0.0, 1.0 - scenario_persistence),
            "scenario_reinforcement": scenario_persistence,
            "payoff_momentum": self._last,
        }


class GameTheoryCore:
    def __init__(self) -> None:
        self.pain_engine = CrowdPainEngine()
        self.player_engine = PlayerModelEngine()
        self.payoff_engine = PayoffMatrixEngine()
        self.decision_engine = GameDecisionEngine()
        self.intent_engine = MarketIntentEngine()
        self.scenario_engine = ScenarioEvolutionEngine()
        self.intent_reality_engine = IntentRealityEngine()
        self.trap_analyzer = TrapAnalyzer()
        self.payoff_evolution = PayoffEvolutionEngine()

    def evaluate(self, price: float, tactical: dict, flow: dict, depth: dict, reaction: dict | None = None) -> dict:
        reaction = reaction or {}
        pain = self.pain_engine.evaluate(price, depth, flow, tactical)
        players = self.player_engine.evaluate(flow, depth, tactical, pain)
        matrix = self.payoff_engine.evaluate(tactical, flow, depth, pain, players)
        decision = self.decision_engine.decide(matrix, pain, players)
        intent = self.intent_engine.evaluate(tactical, flow, depth, reaction, pain)
        scenario_flow = self.scenario_engine.update(decision.best_scenario, decision.confidence)
        intent_reality = self.intent_reality_engine.evaluate(intent, tactical, reaction)
        trap = self.trap_analyzer.evaluate(pain, tactical, intent_reality)
        payoff_flow = self.payoff_evolution.update(decision.expected_payoff, scenario_flow["persistence"])
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
            "intent": intent,
            "scenario_flow": scenario_flow,
            "intent_vs_reality": intent_reality,
            "trap": trap,
            "payoff_flow": payoff_flow,
            "tactical_instability": min((trap["trapped_crowd_severity"] + intent_reality["inversion_risk"] + tactical.get("tactical_danger", 0.0)) / 3.0, 1.0),
        }
