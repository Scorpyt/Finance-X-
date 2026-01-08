from models import MarketSnapshot, SystemState

class Analyst:
    def __init__(self):
        # In a real scenario, this would initialize the LLM client
        pass

    def explain_situation(self, snapshot: MarketSnapshot) -> str:
        """
        Receives a deterministic snapshot and generates a narrative explanation.
        """
        # 1. Construct the Strict Context
        top_events_desc = "\n".join(
            [f"- {e.original_event.description} (Relevance: {e.current_weight:.2f})" 
             for e in snapshot.active_events]
        )
        
        prompt = f"""
        ACT AS: A Senior Financial Intelligence Analyst.
        TASK: Explain the current market situation.
        
        --- DETERMINISTIC DATA ---
        STATE: {snapshot.state.value} 
        RISK: {snapshot.risk_score}
        DRIVERS:
        {top_events_desc}
        -----------------------
        
        Keep it concise (under 50 words).
        """
        return self._mock_llm_response(prompt, snapshot)

    def explain_event(self, event) -> str:
        """
        Explains a specific single event.
        """
        prompt = f"""
        ACT AS: Financial Analyst.
        TASK: Analyze this specific market event.
        
        EVENT: {event.original_event.description}
        IMPACT: {event.original_event.base_impact}
        CURRENT WEIGHT: {event.current_weight:.2f}
        
        Explain the potential downstream effects of this event.
        """
        return f"ANALYST INSIGHT [Event {event.original_event.description[:10]}...]: This event (Impact {event.original_event.base_impact}) is significant. Historically, similar events lead to sector-specific volatility. (Simulated LLM Output)"

    def _mock_llm_response(self, prompt: str, snapshot: MarketSnapshot) -> str:
        """Simulates an LLM response based on the state."""
        if snapshot.state == SystemState.CRASH:
            return f"ALERT: CRASH STATE DETECTED (Risk {snapshot.risk_score}). Driven by: {[e.original_event.description for e in snapshot.active_events[:2]]}."
        
        if snapshot.state == SystemState.HIGH_VOLATILITY:
            return f"VOLATILITY WARNING: Markets reacting to {len(snapshot.active_events)} active events."
            
        return f"STABLE: Risk low ({snapshot.risk_score}). No significant drivers."
