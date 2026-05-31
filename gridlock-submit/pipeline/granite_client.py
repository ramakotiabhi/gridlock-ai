"""
GridLock AI — IBM Granite Reasoning Client
==========================================
Handles all IBM Granite inference calls for incident analysis.
Uses HuggingFace Inference API (free tier for IBM Granite models).

Model: ibm-granite/granite-3.1-8b-instruct
Endpoint: HuggingFace Serverless Inference
"""

import os
import json
from typing import Optional

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠ Run: pip install huggingface_hub")


GRANITE_MODEL = "ibm-granite/granite-3.1-8b-instruct"

SYSTEM_PROMPT = """You are GridLock AI, an expert FIA steward decision-support assistant for Formula 1.

Your role is to ASSIST human stewards — never to replace them.

When analysing incidents:
1. Cite specific FIA regulation articles by number
2. Reference comparable historical incidents with outcomes
3. State a severity score from 1–10 based on sporting impact
4. Provide a recommended penalty range with justification
5. State your confidence level (0–100%)
6. Always note: "Human stewards retain final authority"

Be concise, technical, evidence-based. Reason over the telemetry data provided — never invent numbers."""


class GraniteClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HF_TOKEN", "")
        self.client = None
        if self.api_key and HF_AVAILABLE:
            self.client = InferenceClient(
                provider="hf-inference",
                api_key=self.api_key
            )

    def analyse_incident(
        self,
        incident_data: dict,
        retrieved_regulations: list[str],
        max_tokens: int = 800
    ) -> dict:
        """
        Core incident analysis call to IBM Granite.
        
        Args:
            incident_data: Dict with keys: name, telemetry, articles, description
            retrieved_regulations: Top-k passages from IBM Docling RAG
            max_tokens: Response length limit
            
        Returns:
            Dict with: analysis, confidence, model, regulations_cited
        """
        regulation_context = "\n\n".join(
            [f"[Regulation {i+1}]: {reg}" for i, reg in enumerate(retrieved_regulations[:5])]
        )

        telemetry_formatted = "\n".join(
            [f"- {k}: {v}" for k, v in incident_data.get("telemetry", {}).items()]
        )

        user_prompt = f"""
INCIDENT: {incident_data.get('name', 'Unknown')}
RACE: {incident_data.get('race', '')}
ARTICLES CITED: {', '.join(incident_data.get('articles', []))}

TELEMETRY EVIDENCE:
{telemetry_formatted}

INCIDENT DESCRIPTION:
{incident_data.get('description', '')}

RETRIEVED REGULATION PASSAGES (IBM Docling RAG):
{regulation_context}

Provide a structured steward decision brief.
Format your response as:
1. REGULATION BREACH ASSESSMENT
2. SEVERITY SCORE (1-10) with justification  
3. PRECEDENT COMPARISON (2-3 comparable cases)
4. RECOMMENDED PENALTY RANGE
5. CONFIDENCE LEVEL
"""

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=GRANITE_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.2,
                    top_p=0.9
                )
                return {
                    "analysis": response.choices[0].message.content,
                    "model": GRANITE_MODEL,
                    "regulations_cited": len(retrieved_regulations),
                    "live": True
                }
            except Exception as e:
                print(f"⚠ Granite API error: {e}")
                return self._fallback_analysis(incident_data)
        else:
            return self._fallback_analysis(incident_data)

    def generate_fan_explanation(self, incident_data: dict, analysis: str) -> str:
        """Generate plain-language fan explanation using IBM Granite."""
        if not self.client:
            return incident_data.get("fan_explanation", "Analysis not available.")

        prompt = f"""
Based on this F1 steward analysis: {analysis[:500]}

Write a plain-language explanation for casual F1 fans (no jargon).
Explain: what happened, which rule was broken, why that penalty.
Use an analogy from everyday life if helpful. Maximum 100 words.
"""
        try:
            response = self.client.chat.completions.create(
                model=GRANITE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return incident_data.get("fan_explanation", "")

    def score_team_appeal(self, incident_analysis: str, team_argument: str) -> dict:
        """
        Score a team's appeal argument against the steward decision.
        
        Returns:
            Dict with: appeal_strength (0-100), key_arguments, recommendation
        """
        if not self.client:
            return {"appeal_strength": 50, "recommendation": "Consult legal team."}

        prompt = f"""
STEWARD DECISION:
{incident_analysis[:400]}

TEAM APPEAL ARGUMENT:
{team_argument}

Rate the appeal strength (0-100) and identify:
1. The 3 strongest regulatory arguments in the appeal
2. The 2 weakest points that stewards will likely reject
3. Appeal recommendation: STRONG (pursue) / MODERATE (negotiate) / WEAK (accept)

Be concise and cite specific regulation articles.
"""
        try:
            response = self.client.chat.completions.create(
                model=GRANITE_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            content = response.choices[0].message.content
            return {"appeal_analysis": content, "model": GRANITE_MODEL}
        except Exception as e:
            return {"appeal_analysis": f"Error: {e}"}

    def _fallback_analysis(self, incident_data: dict) -> dict:
        """Curated analysis when live Granite is unavailable."""
        return {
            "analysis": f"[Demo Mode] Pre-analysed incident: {incident_data.get('name')}. Connect HuggingFace token for live IBM Granite analysis.",
            "model": "curated_knowledge_base",
            "regulations_cited": 3,
            "live": False
        }


# ─── EXAMPLE USAGE ───────────────────────────────────────────────

if __name__ == "__main__":
    from docling_setup import retrieve_relevant_regulations

    client = GraniteClient(api_key=os.getenv("HF_TOKEN"))

    # Abu Dhabi 2021 example
    incident = {
        "name": "Abu Dhabi 2021 — Safety Car Controversy",
        "race": "2021 Abu Dhabi Grand Prix",
        "articles": ["Article 48.12", "Article 48.13"],
        "telemetry": {
            "Hamilton tyre age": "42 laps (mediums)",
            "Verstappen tyre age": "0 laps (fresh softs)",
            "Safety Car deployed": "Lap 53",
            "Lapped cars between leaders": "8",
            "Cars allowed to un-lap": "5 of 8",
            "Gap at restart": "0.0 seconds"
        },
        "description": "Race Director selectively applied Article 48.12, allowing only 5 of 8 lapped cars to un-lap before the Safety Car returned to the pits, placing fresh-tyred Verstappen directly behind Hamilton for the final lap."
    }

    # Retrieve relevant regulations from Docling RAG
    regulations = retrieve_relevant_regulations(
        "safety car lapped cars unlapping procedure article 48",
        top_k=5
    )

    # Run IBM Granite analysis
    result = client.analyse_incident(incident, regulations)
    print("\n" + "="*60)
    print("IBM GRANITE ANALYSIS RESULT")
    print("="*60)
    print(f"Model: {result['model']}")
    print(f"Regulations cited: {result['regulations_cited']}")
    print(f"Live inference: {result['live']}")
    print("\nAnalysis:")
    print(result['analysis'])
