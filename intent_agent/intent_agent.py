import re

# Patterns for intent agent                 


# NAVIGATIONAL
# INFORMATIONAL
# TECHNICAL
# COMPARISON
# RESEARCH

NAVIGATIONAL_PATTER=[
    r"\.com",r"\.ai",r"\.org",r"\.in",r"\.net",r"website", r"homepage",r"official website"
]

COMPARISON_PATTER=[
    r"vs",r"versus",r"compare",r"difference",r"similar",r"alternative",r"vs",r"versus",r"compare",r"difference",r"similar",r"alternative"
]

INFORMATIONAL_PATTER=[
    r"what",r"how",r"why",r"when",r"where",r"who",r"which",r"what",r"how",r"why",r"when",r"where",r"who",r"which"
]

TECHNICAL_PATTER=[
    r"api",r"sdk",r"documentation",r"tutorial",r"guide",r"example",r"code",r"api",r"sdk",r"documentation",r"tutorial",r"guide",r"example",r"code"
]

RESEARCH_PATTER=[
    r"research",r"study",r"paper",r"journal",r"conference",r"research",r"study",r"paper",r"journal",r"conference"
]


def detect_intent(querry:str):
    q=querry.lower()

    #checking for navigational intent
    for pattern in NAVIGATIONAL_PATTER:
        if re.search(pattern,q):
            return "navigational"

    #checking for comparison intent
    for pattern in COMPARISON_PATTER:
        if re.search(pattern,q):
            return "comparison"

    #checking for informational intent
    for pattern in INFORMATIONAL_PATTER:
        if re.search(pattern,q):
            return "informational"

    #checking for technical intent
    for pattern in TECHNICAL_PATTER:
        if re.search(pattern,q):
            return "technical"

    #checking for research intent
    for pattern in RESEARCH_PATTER:
        if re.search(pattern,q):
            return "research"

    #default intent
    return "informational"


