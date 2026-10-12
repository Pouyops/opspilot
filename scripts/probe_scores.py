import httpx

IN_DOMAIN = [
    "how do I change my billing email",
    "I lost my two-factor recovery codes",
    "what happens to my data if I delete my account",
    "how do I add a new payment method",
    "can I redeem a coupon",
    "how do I transfer a repository to an organization",
    "why is my email not verified",
    "what is a personal access token",
]
OUT_OF_DOMAIN = [
    "how long can I take parental leave",
    "what is the capital of France",
    "recipe for chocolate cake",
    "how do I reset my Netflix password",
    "who won the football world cup",
    "what is the company dress code",
]


def top_score(question: str) -> float | None:
    r = httpx.get(
        "http://localhost:8000/search",
        params={"q": question, "limit": 1, "min_score": -100},
        timeout=60,
    )
    results = r.json().get("results", [])
    return results[0]["rerank_score"] if results else None


for label, questions in [("IN-DOMAIN", IN_DOMAIN), ("OUT-OF-DOMAIN", OUT_OF_DOMAIN)]:
    print(f"\n{label}")
    for q in questions:
        print(f"  {top_score(q)!s:>8}  {q}")
