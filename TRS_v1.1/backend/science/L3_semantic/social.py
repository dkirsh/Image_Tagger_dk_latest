"""
Social disposition analyzer for architectural spaces.

WARNING: All outputs from this module are L3 HYPOTHESES.
They depend on VLM inference and should be treated as provisional
until validated against ground truth.

Generates VLM prompts specifically for Architectural Psychology social
affordance assessment:
- Sociopetal (encourages interaction)
- Sociofugal (discourages interaction)
- Privacy (visual/acoustic isolation)
- Hierarchy (clear distinction of status)

Ported to L3_semantic with add_hypothesis() API.
"""

from science.core import AnalysisFrame


class SocialDispositionAnalyzer:
    """
    Generates VLM Prompts specifically for Architectural Psychology.
    """

    name = "social_disposition"
    tier = "L3"
    requires = ["original_image"]
    provides = [
        "social.sociopetal",
        "social.sociofugal",
        "social.privacy",
        "social.hierarchy",
    ]

    _MODEL_NAME = "vlm_social"
    _PROMPT_HASH = "social_disposition_v1"
    
    PROMPT_TEMPLATE = """
    Analyze this architectural interior as an environmental psychologist.
    Assess the following social affordances on a scale of 0.0 to 1.0:
    
    1. Sociopetal (Encourages interaction): {sociopetal_score}
    2. Sociofugal (Discourages interaction): {sociofugal_score}
    3. Privacy (Visual/Acoustic isolation): {privacy_score}
    4. Hierarchy (Clear distinction of status): {hierarchy_score}
    
    Output strictly in JSON format: { "sociopetal": 0.X, "sociofugal": 0.X, "privacy": 0.X, "hierarchy": 0.X }
    """

    @staticmethod
    async def analyze(frame: AnalysisFrame, perception_engine):
        """
        Uses the shared PerceptionProcessor (VLM) to run this specific study.
        """
        _MN = SocialDispositionAnalyzer._MODEL_NAME
        _PH = SocialDispositionAnalyzer._PROMPT_HASH
        _SRC = "social.SocialDispositionAnalyzer.analyze"

        # In a real system, 'perception_engine' is the VLM client wrapper
        # result = await perception_engine.ask(frame.original_image, PROMPT_TEMPLATE)
        
        # MOCK RESULT (until VLM is live)
        frame.add_hypothesis("social.sociopetal", 0.75, source=_SRC, model_name=_MN, prompt_hash=_PH, confidence=0.8)
        frame.add_hypothesis("social.privacy", 0.30, source=_SRC, model_name=_MN, prompt_hash=_PH, confidence=0.8)
