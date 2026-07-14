"""
cnfa_algs.validation.probes — ordinary-language probe battery for
VLM/human validation of attribute operationalizations.

Each probe maps an algorithmic attribute to plain-language questions in
three formats:
  ordinal       : 1-7 rating with anchored endpoints
  pairwise      : two-image forced choice (more reliable than absolute)
  localization  : "return a bbox [x0,y0,x1,y1] in relative coords" for
                  comparison with the algorithm's evidence region (IoU)

Validation logic (see stats.py):
  ordinal  -> Spearman rho vs algorithm scalar across the image set
  pairwise -> % agreement with the algorithm's sign of difference
  localization -> IoU vs algorithm evidence bbox

Discipline: checker != author. The judge model must not be tuned against;
it is one rater in a panel. Report inter-rater agreement, not just
judge-vs-algorithm.
"""

PROBES = {
    "cnfa.spatial.enclosure_index": {
        "construct": "physical enclosure of the visible space",
        "ordinal": ("How physically enclosed does this space feel? "
                    "1 = almost entirely open/glazed to the outside, "
                    "7 = fully enclosed by solid walls and ceiling with no view out. "
                    "Answer with a single integer 1-7, then one sentence of reasoning."),
        "pairwise": "Which of these two interiors is MORE physically enclosed (fewer/smaller openings, more solid boundary)? Answer 'A' or 'B' and one sentence.",
        "localization": None,
        "expected_direction": "+",
    },
    "cnfa.spatial.prospect": {
        "construct": "how far one can see through the space",
        "ordinal": ("From the camera position, how far could a person standing here see "
                    "through the space along the longest unobstructed line? "
                    "1 = only a couple of metres, 7 = a very long view (a long corridor "
                    "or vista of 15m+). Single integer 1-7 + one sentence."),
        "pairwise": "In which of these two interiors can a person see FARTHER along the longest clear sightline? 'A' or 'B' + one sentence.",
        "localization": "Draw a box around the region of the image where the LONGEST clear view runs (the visual corridor). Return [x0,y0,x1,y1] as fractions of image width/height.",
        "expected_direction": "+",
    },
    "cnfa.fluency.processing_load_proxy": {
        "construct": "visual information load / clutter",
        "ordinal": ("How visually busy or cluttered is this interior? "
                    "1 = extremely spare and minimal, 7 = extremely busy: many objects, "
                    "materials, patterns and details competing for attention. "
                    "Single integer 1-7 + one sentence."),
        "pairwise": "Which of these two interiors is MORE visually busy/cluttered? 'A' or 'B' + one sentence.",
        "localization": "Draw a box around the MOST visually cluttered region. Return [x0,y0,x1,y1] as fractions.",
        "expected_direction": "+",
    },
    "cnfa.light.warm_vs_cool_ratio": {
        "construct": "warm vs cool material/light character",
        "ordinal": ("Is the colour character of this interior warm or cool? "
                    "1 = distinctly cool (blues, greys, white light), "
                    "7 = distinctly warm (wood tones, ambers, warm light). "
                    "Single integer 1-7 + one sentence."),
        "pairwise": "Which of these two interiors reads WARMER in material and light colour? 'A' or 'B' + one sentence.",
        "localization": None,
        "expected_direction": "+",
    },
    "acoustic_absorption_proxy": {
        "construct": "acoustic deadness inferred from visible materials",
        "ordinal": ("Judging only from the visible surfaces (hard vs soft materials, "
                    "carpet, curtains, upholstery, glass, concrete), how would this room "
                    "sound if you clapped once? 1 = very echoey/live (all hard surfaces), "
                    "7 = very dead/muffled (lots of soft absorbing material). "
                    "Single integer 1-7 + one sentence."),
        "pairwise": "In which of these two rooms would a hand-clap sound MORE echoey? 'A' or 'B' + one sentence.",
        "localization": "Draw a box around the largest sound-ABSORBING (soft) surface visible. Return [x0,y0,x1,y1] as fractions.",
        "expected_direction": "+",   # scalar is mean absorption = deadness
    },
    "cnfa.cognitive.landmark_salience": {
        "construct": "presence of a dominant orienting landmark",
        "ordinal": ("If you had to describe where to meet someone in this space using one "
                    "visible object or feature, how obvious is the choice? 1 = nothing "
                    "stands out, 7 = one feature is unmistakably dominant. "
                    "Single integer 1-7 + one sentence."),
        "pairwise": "Which of these two interiors has a MORE obvious single landmark feature? 'A' or 'B' + one sentence.",
        "localization": "Draw a box around the single most landmark-like feature (the thing you'd use to anchor directions). Return [x0,y0,x1,y1] as fractions.",
        "expected_direction": "+",
    },
    "glare-risk": {
        "construct": "visual glare discomfort risk",
        "ordinal": ("How likely is it that a person in this space would experience "
                    "uncomfortable glare (harsh bright light in the field of view)? "
                    "1 = no glare risk, 7 = strong glare risk. Single integer + sentence."),
        "pairwise": "Which of these two interiors poses MORE glare risk? 'A' or 'B' + one sentence.",
        "localization": "Draw a box around the brightest potential glare source. Return [x0,y0,x1,y1] as fractions.",
        "expected_direction": "+",
    },
}


def ordinal_prompt(key: str) -> str:
    p = PROBES[key]
    return (f"You are rating one photograph of a building interior.\n"
            f"{p['ordinal']}\n"
            f"Respond in JSON: {{\"rating\": <int 1-7>, \"reason\": \"<one sentence>\"}}")


def pairwise_prompt(key: str) -> str:
    p = PROBES[key]
    return (f"You are comparing two photographs of building interiors, A then B.\n"
            f"{p['pairwise']}\n"
            f"Respond in JSON: {{\"choice\": \"A\"|\"B\", \"reason\": \"<one sentence>\"}}")


def localization_prompt(key: str) -> str:
    p = PROBES[key]
    if not p["localization"]:
        return ""
    return (f"You are analysing one photograph of a building interior.\n"
            f"{p['localization']}\n"
            f"Respond in JSON: {{\"bbox\": [x0, y0, x1, y1], \"reason\": \"<one sentence>\"}}")
