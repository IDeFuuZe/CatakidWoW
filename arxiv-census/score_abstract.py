#!/usr/bin/env python3
"""Honest Phase-A abstract scorer for Dec-1 desks. No fetch pre-filter — scoring only."""
from __future__ import annotations

import re
from typing import Any

# --- Domain signals (AID) ----------------------------------------------------

SPORTS_STRONG = re.compile(
    r"\b("
    r"sports?\s+bett(?:ing|or|ers)|betting\s+odds|"
    # "point spread" as betting line only — never optics "point spread (function)" / HST PSF
    r"(?:(?:betting|wagering|sportsbook|moneyline|handicap)\s+)?point\s+spreads?"
    r"(?!\s+function)(?!\s+of\s+the)(?!\s+wings?)(?!\s+profile)"
    r".{0,40}(?:bet|odds|wager|sportsbook|moneyline|handicap|ats\b|cover(?:s|ing)?\b)|"
    r"(?:bet|odds|wager|sportsbook|moneyline|handicap|ats\b).{0,40}point\s+spreads?(?!\s+function)|"
    r"moneylines?|"
    r"handicap(?:ping)?\s+(?:market|odds|model)|sportsbook|bookmaker|"
    r"match\s+betting|in[- ]play\s+betting|closing\s+line\s+value|"
    # bare CLV collides with astronomy "centre-to-limb variation (CLV)"
    r"closing[- ]line|\bCLV\b.{0,30}(?:bet|odds|wager|sportsbook)|"
    r"predicted?\s+(?:match|game)\s+odds|football\s+betting|soccer\s+betting|"
    r"nba\s+betting|nfl\s+betting|tennis\s+betting|horse\s+rac(?:e|ing)\s+betting|"
    r"pari[- ]mutuel|fixed[- ]odds\s+betting|betting\s+market(?:s)?|"
    r"wagering\s+market|sports\s+wagering|"
    # bare "odds forecasting" can be Bayes/astro; require sports/bet frame
    r"(?:sports?\s+|betting\s+|match\s+|game\s+)odds\s+forecasting|"
    r"elo\s+(?:rating|model).{0,40}(?:bet|odds|wager)|"
    r"(?:bet|wager).{0,40}elo\s+(?:rating|model)|"
    r"expected\s+goals.{0,30}(?:bet|odds|market)|"
    r"player\s+prop(?:s|\s+bet)"
    r")\b",
    re.I | re.S,
)

# Astrophysics / optics false friends — if present and no true sports-betting frame, demote AID_SPORTS
ASTRO_SPORTS_FP = re.compile(
    r"\b("
    r"point[- ]spread\s+function|\bPSF\b|HST\s+point\s+spread|"
    r"telescope\s+point\s+spread|optical\s+point\s+spread|"
    r"surface\s+brightness|globular\s+cluster|stellar\s+(?:core|magnitude|density)|"
    r"post[- ]collapse\s+(?:core|cluster)|core[- ]collapse|"
    r"centre[- ]to[- ]limb|center[- ]to[- ]limb|"
    r"redshift|supernova|black\s+hole|neutron\s+star|"
    r"dark\s+matter|cosmology|quasar|galaxy\s+cluster"
    r")\b",
    re.I,
)

SPORTS_BETTING_FRAME = re.compile(
    r"\b("
    r"sports?\s*book|bookmaker|moneyline|betting\s+odds|sports?\s+bett|"
    r"wagering|pari[- ]mutuel|in[- ]play\s+betting|closing\s+line|"
    r"player\s+prop|match\s+betting|fixed[- ]odds\s+betting|"
    r"nba|nfl|mlb|nhl|premier\s+league|march\s+madness"
    r")\b",
    re.I,
)

SPORTS_MED = re.compile(
    r"\b("
    r"sports?\s+analytics|match\s+outcome\s+prediction|game\s+outcome\s+prediction|"
    r"predict(?:ing|ion of)\s+(?:football|soccer|nba|nfl|mlb|nhl|tennis|cricket)\s+(?:match|game|results?)|"
    r"team\s+strength\s+(?:rating|model)|rating\s+system.{0,40}(?:sport|match|team)|"
    r"football\s+match\s+prediction|soccer\s+match\s+prediction|"
    r"tennis\s+match\s+prediction|march\s+madness\s+bracket|"
    r"win\s+probability.{0,30}(?:nba|nfl|mlb|nhl|match|team)"
    r")\b",
    re.I | re.S,
)

POKER_STRONG = re.compile(
    r"\b("
    r"texas\s+hold'?em|holdem|no[- ]limit\s+hold'?em|\bNLHE\b|\bHUNL\b|"
    r"poker\s+(?:bot|agent|ai|solver|endgame|abstraction)|"
    r"counterfactual\s+regret.{0,40}poker|poker.{0,40}counterfactual\s+regret|"
    r"\bCFR\+?\b.{0,40}poker|poker.{0,40}\bCFR\+?\b|"
    r"heads[- ]up\s+(?:no[- ]limit\s+)?(?:poker|hold'?em)|"
    r"pluribus|libratus|deepstack|slumbot|"
    r"poker\s+hand\s+history|poker\s+strategy|exploitab(?:le|ility).{0,30}poker|"
    r"imperfect[- ]information.{0,40}poker|poker.{0,40}imperfect[- ]information|"
    r"omaha\s+poker|seven[- ]card\s+stud|video\s+poker"
    r")\b",
    re.I | re.S,
)

POKER_MED = re.compile(
    r"\b("
    r"\bpoker\b|betting\s+rounds?.{0,30}(?:card|hand|chip)|"
    r"card\s+game.{0,40}(?:nash|equilibrium|cfr|regret)|"
    r"extensive[- ]form\s+game.{0,40}(?:poker|hold'?em)"
    r")\b",
    re.I | re.S,
)

# Crypto TRADING / memecoins — exclude cryptography (AES, RSA, lattice crypto, etc.)
CRYPTO_STRONG = re.compile(
    r"(?:"
    r"\b(?:"
    r"cryptocurrenc(?:y|ies)\s+(?:trad(?:e|ing)|price|market)|"
    r"bitcoin\s+(?:price|trad(?:e|ing)|market|volatilit)|"
    r"ethereum\s+(?:price|trad(?:e|ing)|market)|"
    r"memecoin|meme\s+coin|shitcoin|"
    r"token\s+(?:price\s+prediction|trad(?:e|ing)|pump)|"
    r"defi\s+(?:trad(?:e|ing)|liquidity|swap)|"
    r"maximal\s+extractable\s+value|"
    r"dex\s+(?:trad(?:e|ing)|liquidity|arbitrage)|"
    r"decentralized\s+exchange|"
    r"crypto\s+(?:trad(?:e|ing)|market\s+microstructure|price\s+prediction)|"
    r"on[- ]chain\s+(?:trad(?:e|ing)|market|whale)|"
    r"pump[- ]and[- ]dump|token\s+sniping|bonding\s+curve.{0,30}(?:token|coin|trad)|"
    r"solana\s+(?:token|memecoin|trad)|"
    r"nft\s+(?:flip|trad(?:e|ing)|price\s+prediction)"
    r")\b"
    # Do NOT match physics "MeV" (mega-electron-volt). Trading MEV only:
    # - no preceding mass digit ("5 MeV both" must NOT hit)
    # - word-bounded bot/auction/sandwich/extractor (bots? alone matched "both")
    r"|defi.{0,30}maximal\s+extractable|"
    r"(?<!\d)(?<!\d )mev\s+(?:bots?\b|auctions?\b|sandwich(?:es)?\b|extractors?\b)|"
    r"(?:sandwich|flash[- ]?loan)\s+mev\b"
    r")",
    re.I | re.S,
)

CRYPTO_MED = re.compile(
    r"\b("
    r"bitcoin|ethereum|\bBTC\b|\bETH\b|blockchain\s+(?:market|price|trad)|"
    r"cryptocurrenc(?:y|ies)|digital\s+asset\s+(?:price|trad|market)|"
    r"stablecoin|uniswap|binance|coinbase|"
    r"order\s+book.{0,40}(?:crypto|bitcoin|token)|"
    r"high[- ]frequency.{0,30}(?:crypto|bitcoin|token)"
    r")\b",
    re.I | re.S,
)

CRYPTOGRAPHY_NEG = re.compile(
    r"\b("
    r"cryptograph(?:y|ic)|public[- ]key|private[- ]key\s+encrypt|"
    r"\bAES\b|\bRSA\b|\bSHA[- ]?\d|lattice[- ]based\s+crypto|"
    r"homomorphic\s+encrypt|zero[- ]knowledge\s+proof|"
    r"post[- ]quantum\s+crypto|block\s+cipher|stream\s+cipher|"
    r"cryptanalysis|encryption\s+scheme|digital\s+signature\s+scheme"
    r")\b",
    re.I,
)

TRANSFER = re.compile(
    r"\b("
    r"kelly\s+criterion|fractional\s+kelly|bankroll\s+management|"
    r"probability\s+calibration|isotonic\s+calibration|platt\s+scaling|"
    r"market\s+microstructure|limit\s+order\s+book|optimal\s+execution|"
    r"online\s+(?:learning|convex\s+optimization).{0,40}(?:trad|bet|market|forecast)|"
    r"time[- ]series\s+(?:forecast|prediction).{0,40}(?:financ|market|return|price)|"
    r"financial\s+(?:time[- ]series|forecasting|return\s+prediction)|"
    r"reinforcement\s+learning.{0,50}(?:trad(?:e|ing)|portfolio|market\s+making)|"
    r"portfolio\s+optimiza|risk[- ]neutral\s+pricing|"
    # Never bare CFR (Italian cfr.; astronomy "cluster formation rate (CFR)")
    r"counterfactual\s+regret(?:\s+minimization)?|(?<![A-Za-z])CFR\+(?![A-Za-z])|"
    r"imperfect[- ]information\s+game|extensive[- ]form\s+game|"
    r"nash\s+equilibrium.{0,40}(?:game|poker|bet)|"
    r"sequential\s+decision.{0,30}(?:uncertain|risk|market)|"
    # "odds favoring the hypothesis" (Bayes factors) is NOT betting
    r"bayesian\s+(?:updating|inference).{0,40}(?:forecast|betting\s+odds|market\s+odds|wager)|"
    r"proper\s+scoring\s+rule|brier\s+score|log\s+loss\s+calibration|"
    r"bandit.{0,30}(?:portfolio|trad|market)|"
    r"stochastic\s+game|zero[- ]sum\s+game\s+solver|"
    r"opponent\s+modeling|exploitability|"
    r"parimutuel|prediction\s+market|"
    r"odds\s+ratio\s+forecast|probability\s+forecasting"
    r")\b",
    re.I | re.S,
)

UNCERTAIN_HINT = re.compile(
    r"\b("
    r"betting|wagering|gambling|casino|trad(?:e|ing)\s+strateg|"
    r"market\s+efficiency|efficient\s+market|price\s+prediction|"
    r"game[- ]theoretic|multi[- ]agent\s+(?:rl|reinforcement)|"
    r"auction\s+theory|mechanism\s+design.{0,30}(?:bet|market)"
    r")\b",
    re.I,
)


def _norm_text(title: str, abstract: str) -> str:
    return f"{title or ''}\n{abstract or ''}"


def score_abstract(
    *,
    title: str,
    abstract: str,
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """Return labels + brief rationale. Multi-label AID_* allowed."""
    text = _norm_text(title, abstract)
    cats = categories or []
    cat_str = " ".join(cats)

    labels: list[str] = []
    reasons: list[str] = []

    # --- AID_SPORTS ---
    sports_strong = SPORTS_STRONG.search(text)
    sports_med = SPORTS_MED.search(text) and re.search(
        r"\b(bet|odds|wager|market|forecast|predict)\b", text, re.I
    )
    if sports_strong or sports_med:
        # Kill astrophysics/optics collisions (e.g. HST "point spread", cluster cores)
        if ASTRO_SPORTS_FP.search(text) and not SPORTS_BETTING_FRAME.search(text):
            reasons.append("astro/optics lexicon — sports AID suppressed")
        else:
            labels.append("AID_SPORTS")
            reasons.append(
                "sports-betting/odds lexicon (strong)"
                if sports_strong
                else "sports prediction + market/forecast lexicon"
            )

    # --- AID_POKER ---
    if POKER_STRONG.search(text):
        labels.append("AID_POKER")
        reasons.append("poker/CFR-holdem lexicon (strong)")
    elif POKER_MED.search(text) and not re.search(
        r"\bpoker[- ]face\b|video\s+poker\s+machine\s+hardware", text, re.I
    ):
        # bare "poker" still AID if not obviously metaphorical/hardware
        if re.search(r"\bpoker\b", text, re.I):
            labels.append("AID_POKER")
            reasons.append("poker domain mention")

    # --- AID_CRYPTO (trading) ---
    crypto_hit = CRYPTO_STRONG.search(text) or (
        CRYPTO_MED.search(text)
        and re.search(r"\b(trad|price|market|forecast|liquidity|token)\b", text, re.I)
    )
    if crypto_hit:
        # demote pure cryptography papers that only match weak "crypto" stems via BTC miss
        if CRYPTOGRAPHY_NEG.search(text) and not CRYPTO_STRONG.search(text) and not re.search(
            r"\b(bitcoin|ethereum|memecoin|defi|uniswap|token\s+price)\b", text, re.I
        ):
            reasons.append("cryptography context — not trading AID")
        else:
            labels.append("AID_CRYPTO")
            reasons.append("crypto/memecoin trading lexicon")

    # Category soft boosts (still require some text signal for AID; cats alone → TRANSFER/UNCERTAIN)
    if not labels:
        if any(c.startswith("q-fin") for c in cats) and TRANSFER.search(text + " " + cat_str):
            labels.append("TRANSFER")
            reasons.append("q-fin + transferable quant methods")
        elif any(c in {"cs.GT", "cs.AI", "cs.LG", "stat.ML"} for c in cats) and TRANSFER.search(text):
            labels.append("TRANSFER")
            reasons.append("GT/AI/ML + transferable decision/game methods")
        elif TRANSFER.search(text):
            labels.append("TRANSFER")
            reasons.append("transferable method lexicon")
        elif UNCERTAIN_HINT.search(text):
            labels.append("UNCERTAIN")
            reasons.append("ambiguous market/game language")
        else:
            labels.append("NO_AID")
            reasons.append("no desk-relevant signal in abstract")
    else:
        # AID present — do not also add TRANSFER/NO_AID
        pass

    # If only weak signals conflict, keep UNCERTAIN over false AID — already handled by strong/med tiers

    primary = labels[0]
    return {
        "labels": labels,
        "primary": primary,
        "aid_sports": "AID_SPORTS" in labels,
        "aid_poker": "AID_POKER" in labels,
        "aid_crypto": "AID_CRYPTO" in labels,
        "transfer": "TRANSFER" in labels,
        "uncertain": "UNCERTAIN" in labels,
        "no_aid": labels == ["NO_AID"],
        "rationale": "; ".join(reasons),
        "phase": "abstract",
    }


if __name__ == "__main__":
    demos = [
        ("Kelly criterion for sports betting bankrolls", "We apply fractional Kelly to NFL moneylines."),
        ("Solving Heads-Up Limit Hold'em", "We use CFR+ to solve poker."),
        ("Memecoin pump detection on Solana", "We study bonding curves and sniping on DEX pools."),
        ("Higgs boson mass bounds", "We compute loop corrections in the MSSM."),
        ("Calibration of probabilistic classifiers", "Platt scaling and isotonic regression for forecast calibration."),
    ]
    for t, a in demos:
        print(t, "=>", score_abstract(title=t, abstract=a))
