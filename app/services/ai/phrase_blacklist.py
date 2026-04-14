"""AI Phrase Blacklist - Detects and replaces robotic AI-sounding phrases."""

import re
from typing import List, Tuple, Dict

# Comprehensive blacklist of AI-sounding phrases and their human alternatives
AI_PHRASE_BLACKLIST = {
    # Overused action verbs
    "spearheaded": ["led", "managed", "directed", "drove"],
    "orchestrated": ["coordinated", "organized", "managed", "ran"],
    "leveraged": ["used", "applied", "built with", "took advantage of"],
    "utilized": ["used", "built", "worked with", "applied"],
    "implemented": ["built", "created", "developed", "shipped"],
    "architected": ["designed", "built", "created", "structured"],
    "engineered": ["built", "developed", "created", "designed"],
    "pioneered": ["started", "built", "created", "launched"],
    "championed": ["led", "promoted", "drove", "advocated for"],
    "catalyzed": ["sparked", "started", "drove", "led to"],
    
    # Buzzword phrases
    "cutting-edge": ["modern", "new", "advanced", "latest"],
    "state-of-the-art": ["modern", "advanced", "latest"],
    "best-in-class": ["top-quality", "high-quality", "excellent"],
    "world-class": ["excellent", "top-quality", "high-performing"],
    "seamless integration": ["connected", "linked", "integrated", "combined"],
    "robust solution": ["reliable system", "solid approach", "stable system"],
    "comprehensive suite": ["full set", "complete set", "full range"],
    "end-to-end solution": ["complete system", "full system", "complete solution"],
    "holistic approach": ["complete approach", "full approach", "overall approach"],
    "paradigm shift": ["major change", "big change", "new approach"],
    "game-changer": ["major improvement", "significant change", "key innovation"],
    "synergistic": ["combined", "cooperative", "collaborative"],
    "transformative": ["significant", "major", "important"],
    "unprecedented": ["new", "unique", "first-of-its-kind"],
    
    # Corporate jargon
    "deep dive": ["detailed analysis", "thorough review", "close look"],
    "circle back": ["follow up", "revisit", "discuss again"],
    "move the needle": ["make progress", "show results", "improve metrics"],
    "low-hanging fruit": ["easy wins", "quick wins", "simple improvements"],
    "think outside the box": ["creative approach", "innovative thinking", "new ideas"],
    "at the end of the day": ["overall", "ultimately", "in the end"],
    "drill down": ["analyze", "examine", "look into"],
    "bandwidth": ["time", "capacity", "availability"],
    "pain point": ["problem", "issue", "challenge"],
    "value add": ["improvement", "benefit", "advantage"],
    "key takeaway": ["main point", "key finding", "main insight"],
    
    # AI-specific filler
    "delve": ["explore", "examine", "investigate", "look into"],
    "tapestry": ["mix", "combination", "range", "variety"],
    "testament": ["proof", "evidence", "sign", "example"],
    "landscape": ["field", "area", "space", "industry"],
    "nuanced": ["detailed", "complex", "subtle", "careful"],
    "multifaceted": ["complex", "varied", "diverse", "multi-part"],
    "pivotal": ["key", "critical", "important", "central"],
    "underscore": ["highlight", "emphasize", "show", "demonstrate"],
    "showcase": ["show", "display", "demonstrate", "present"],
    "foster": ["support", "encourage", "build", "develop"],
    "cultivate": ["build", "develop", "grow", "create"],
    "navigate": ["handle", "manage", "deal with", "work through"],
    "realm": ["area", "field", "space", "domain"],
    "elevate": ["improve", "raise", "boost", "enhance"],
    "harness": ["use", "apply", "take advantage of", "leverage"],
    "embark": ["start", "begin", "launch", "undertake"],
    "garner": ["gain", "earn", "receive", "collect"],
    "bolster": ["strengthen", "support", "boost", "improve"],
    "epitomize": ["represent", "show", "demonstrate", "embody"],
    "exemplify": ["show", "demonstrate", "represent", "illustrate"],
    "underscore": ["highlight", "emphasize", "stress", "show"],
    
    # Resume-specific AI patterns
    "instrumental in": ["helped", "contributed to", "supported", "worked on"],
    "played a key role": ["helped", "contributed to", "supported", "worked on"],
    "spearheaded the development": ["led development of", "built", "created"],
    "drove significant improvements": ["improved", "made better", "increased"],
    "cross-functional collaboration": ["teamwork", "worked with other teams", "collaborated"],
    "stakeholder engagement": ["worked with stakeholders", "communicated with teams", "partnered with"],
    "data-driven decisions": ["decisions based on data", "used data to decide", "analyzed data to"],
    "actionable insights": ["useful findings", "clear recommendations", "practical insights"],
    "thought leadership": ["expertise", "knowledge sharing", "industry expertise"],
    "strategic initiatives": ["key projects", "important projects", "major projects"],
}


def detect_ai_phrases(text: str) -> List[Tuple[str, str]]:
    """Detect AI-sounding phrases in text and suggest alternatives.
    
    Args:
        text: The text to analyze
        
    Returns:
        List of tuples: (found_phrase, suggested_alternative)
    """
    if not text:
        return []
    
    found = []
    text_lower = text.lower()
    
    for phrase, alternatives in AI_PHRASE_BLACKLIST.items():
        if phrase.lower() in text_lower:
            found.append((phrase, alternatives[0]))  # Suggest first alternative
    
    return found


def replace_ai_phrases(text: str) -> Tuple[str, int]:
    """Replace AI-sounding phrases with human alternatives.
    
    Args:
        text: The text to process
        
    Returns:
        Tuple of (cleaned_text, number_of_replacements)
    """
    if not text:
        return text, 0
    
    replacements = 0
    result = text
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_phrases = sorted(AI_PHRASE_BLACKLIST.keys(), key=len, reverse=True)
    
    for phrase in sorted_phrases:
        # Case-insensitive replacement, preserving original case pattern
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        if pattern.search(result):
            alternative = AI_PHRASE_BLACKLIST[phrase][0]
            result = pattern.sub(alternative, result)
            replacements += 1
    
    return result, replacements


def get_blacklist_stats() -> Dict:
    """Get statistics about the blacklist."""
    return {
        "total_phrases": len(AI_PHRASE_BLACKLIST),
        "categories": {
            "action_verbs": sum(1 for p in AI_PHRASE_BLACKLIST if p in ["spearheaded", "orchestrated", "leveraged", "utilized", "implemented", "architected", "engineered", "pioneered", "championed", "catalyzed"]),
            "buzzwords": sum(1 for p in AI_PHRASE_BLACKLIST if p in ["cutting-edge", "state-of-the-art", "best-in-class", "world-class", "seamless integration", "robust solution"]),
            "corporate_jargon": sum(1 for p in AI_PHRASE_BLACKLIST if p in ["deep dive", "circle back", "move the needle", "low-hanging fruit", "think outside the box"]),
            "ai_filler": sum(1 for p in AI_PHRASE_BLACKLIST if p in ["delve", "tapestry", "testament", "landscape", "nuanced", "multifaceted", "pivotal"]),
            "resume_patterns": sum(1 for p in AI_PHRASE_BLACKLIST if p in ["instrumental in", "played a key role", "spearheaded the development", "drove significant improvements"]),
        }
    }
