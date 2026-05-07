class MarketSummaryEngine:
    def summarize(self, tactical: dict, game: dict) -> str:
        state = tactical.get("state", "NEUTRAL_FLOW").replace("_", " ").lower()
        intent = game.get("intent", {}).get("intent", "RANGE_MANIPULATION").replace("_", " ").lower()
        trapped = game.get("trapped_side", "NONE").lower()
        scenario = game.get("decision", {}).get("best_scenario", "COMPRESSION_WAIT").replace("_", " ").lower()
        pressure = tactical.get("pressure_direction", "FLAT").lower()
        return (
            f"Market {state}, {intent} intent, {trapped} vulnerable, "
            f"{scenario} scenario active, pressure {pressure}."
        )
