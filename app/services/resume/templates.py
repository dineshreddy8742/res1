from typing import Dict, List

TEMPLATES: Dict[str, Dict] = {
    "ats_standard": {
        "id": "ats_standard",
        "name": "ATS Standard (High Success)",
        "type": "ATS",
        "description": "Clean, single-column layout optimized for 100% ATS readability.",
        "spacing": "tight"
    },
    "modern_pro": {
        "id": "modern_pro",
        "name": "Modern Professional",
        "type": "Advanced",
        "description": "Modern look with blue accents and justified text for a crisp finish.",
        "spacing": "relaxed"
    },
    "executive_dark": {
        "id": "executive_dark",
        "name": "Executive Elite",
        "type": "Advanced",
        "description": "Sophisticated dark grey accents for senior management roles.",
        "spacing": "normal"
    },
    "minimalist": {
        "id": "minimalist",
        "name": "Minimalist White",
        "type": "Basic",
        "description": "Ultra-clean design focusing purely on content and white space.",
        "spacing": "relaxed"
    },
    "technical_focused": {
        "id": "technical_focused",
        "name": "Technical Architect",
        "type": "ATS",
        "description": "Prioritizes skills and technical projects at the top.",
        "spacing": "tight"
    },
    "creative_flow": {
        "id": "creative_flow",
        "name": "Creative Impact",
        "type": "Advanced",
        "description": "Stylized section headers and unique bullet styles for creative roles.",
        "spacing": "relaxed"
    },
    "academic_cv": {
        "id": "academic_cv",
        "name": "Academic Scholar",
        "type": "Basic",
        "description": "Traditional layout perfect for research, education, and grants.",
        "spacing": "normal"
    },
    "compact_one_page": {
        "id": "compact_one_page",
        "name": "The 1-Pager",
        "type": "ATS",
        "description": "Dense layout designed to fit extensive experience into one page.",
        "spacing": "compressed"
    },
    "bold_sidebar": {
        "id": "bold_sidebar",
        "name": "Bold Distinction",
        "type": "Advanced",
        "description": "Uses bold lines and distinct hierarchy for maximum impact.",
        "spacing": "normal"
    },
    "internship_ready": {
        "id": "internship_ready",
        "name": "Student/Internship",
        "type": "Basic",
        "description": "Tailored for those with more education/projects than work history.",
        "spacing": "relaxed"
    }
}
