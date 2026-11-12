"""Deterministic intent detection; no autonomous orchestration."""
SUMMARY = "SUMMARY"
CONCEPT_EXTRACTION = "CONCEPT_EXTRACTION"
SLIDE_GENERATION = "SLIDE_GENERATION"
VIVA_PREPARATION = "VIVA_PREPARATION"
CONCEPT_EXPLANATION = "CONCEPT_EXPLANATION"

def route_intent(text: str) -> str:
    value = text.lower()
    if any(word in value for word in ("viva", "oral exam", "questions", "quiz")):
        return VIVA_PREPARATION
    if any(word in value for word in ("slide", "presentation", "ppt", "powerpoint")):
        return SLIDE_GENERATION
    if any(phrase in value for phrase in ("explain the concept", "explain concept", "what is ", "what does ", "meaning of ", "define ")):
        return CONCEPT_EXPLANATION
    if any(word in value for word in ("concept", "contribution", "method", "algorithm", "extract")):
        return CONCEPT_EXTRACTION
    if any(word in value for word in ("summary", "summarize", "summarise", "overview")):
        return SUMMARY
    return CONCEPT_EXPLANATION
