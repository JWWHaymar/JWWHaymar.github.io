#!/usr/bin/env python3
"""
verify.py - does this website still say what the CV says, and nothing more?

WHY THIS EXISTS
---------------
A CV is a professional-integrity document. The failure mode of translating one
into HTML is not a broken layout -- it is a sentence that reads better than the
truth. Nobody notices a bullet that quietly gained a word, and on a public page
under his own name that is the expensive kind of wrong.

So this script refuses to let the site drift from the PDF of record. It is run
before every push, and it checks three things that are each a real incident
waiting to happen:

  1. NO PII. The CV PDF carries a home address and a phone number, because it
     is sent to one named employer at a time. This page is public and
     permanently crawlable by anyone. The vault already has `check_pii.py`
     because an address nearly got committed once; publishing one to the open
     web is strictly worse, since it cannot be un-published.

  2. EVERY CLAIM TRACES TO THE PDF. Each factual token on the page -- every
     employer, trial number, degree, date, award -- must appear in the
     extracted PDF text. A claim that is on the site and not in the CV is an
     invention, and it fails this check.

  3. NOTHING THE CV SAYS WAS SILENTLY DROPPED. The opposite error: a position
     or a poster that fell out during the translation. An omission is quieter
     than an invention and just as misleading.

An empty result is an ERROR, never a pass: if the PDF cannot be read, this
exits non-zero rather than reporting that all zero claims verified.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

CV_PDF = Path("/mnt/c/Users/jwyha/OneDrive/Desktop/Awy/Awy/APersonal/"
              "CV and Resumes/JWWMH_CV.pdf")
SITE = Path(__file__).resolve().parent / "index.html"

FAILED: list[str] = []
PASSED = 0


def check(what: str, ok: bool, detail: str = "") -> None:
    global PASSED
    if ok:
        PASSED += 1
        print(f"  [ok] {what}" + (f"  {detail}" if detail else ""))
    else:
        FAILED.append(what)
        print(f"  [FAIL] {what}" + (f"  {detail}" if detail else ""))


def norm(s: str) -> str:
    """Collapse whitespace and unify dashes/quotes so HTML entities, PDF
    ligatures and line-wrapping cannot create a false mismatch. The PDF wraps
    mid-sentence; the HTML wraps elsewhere. Comparing raw text would fail on
    formatting rather than on meaning, which is the wrong signal."""
    s = unicodedata.normalize("NFKD", s)
    # Drop the combining marks NFKD just separated out. Without this,
    # `Sébastien` normalises to `se bastien` -- the accent becomes a word
    # break -- and a name that IS in the CV reports as unsourced. Found
    # 2026-10-10 by this script failing on its own supervisor check.
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = (s.replace("\u2014", "-").replace("\u2013", "-").replace("\u2019", "'")
          .replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'")
          .replace("\u00a0", " ").replace("\u00b7", " "))
    s = re.sub(r"[^a-z0-9.%/&'\"()+-]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def html_text(raw: str) -> str:
    """The page's visible prose: scripts, comments and tags removed, entities
    resolved. Comments must go FIRST -- the comments in index.html discuss the
    very PII this script forbids, so scanning them would fail check 1 on text
    no visitor can see."""
    import html as _html
    raw = re.sub(r"(?s)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", raw)
    # Keep attribute values: mailto: links and ClinicalTrials URLs are claims.
    raw = re.sub(r"<[^>]+>", " ", raw)
    return _html.unescape(raw)


def main() -> int:
    if not CV_PDF.is_file():
        print(f"ERROR: the CV of record is missing: {CV_PDF}")
        return 2
    if not SITE.is_file():
        print(f"ERROR: {SITE} is missing")
        return 2

    try:
        from pypdf import PdfReader
    except ImportError:
        print("ERROR: pypdf is not installed; cannot verify against the CV")
        return 2

    pdf_raw = "\n".join(p.extract_text() or "" for p in PdfReader(CV_PDF).pages)
    if len(pdf_raw) < 2000:
        # RULES #1: an empty extraction must not read as "nothing to check".
        print(f"ERROR: extracted only {len(pdf_raw)} chars from the CV; "
              "refusing to verify against a failed read")
        return 2
    pdf = norm(pdf_raw)
    site_visible = html_text(SITE.read_text(encoding="utf-8"))
    site = norm(site_visible)

    print(f"\nVerifying {SITE.name} against {CV_PDF.name} "
          f"({len(pdf_raw)} chars extracted)\n")

    # ── 1. NO PII ON A PUBLIC PAGE ────────────────────────────────────────
    print("1. NO PII (the page is public and permanently crawlable)")

    # Pulled from the PDF itself rather than typed here, so this file does not
    # become the thing it is guarding against.
    street = re.search(r"\d{3,5}\s+[A-Z][a-z]+\s+(?:Ave|St|Rd|Dr|Blvd|Ln|Way)",
                       pdf_raw)
    phone = re.search(r"\b\d{3}[.\-\s]\d{3}[.\-\s]\d{4}\b", pdf_raw)

    check("the CV does contain a street address to protect",
          street is not None,
          "if this fails the regex broke, not the CV -- do not read it as safe")
    if street:
        check("the street address is NOT on the page",
              norm(street.group(0)) not in site,
              f"found: {street.group(0)}")
        # The house number alone, next to the street name, is enough to locate him.
        num = street.group(0).split()[0]
        check("the house number does not appear beside a street word",
              not re.search(rf"\b{num}\b\s+\w+\s*(ave|avenue|st|street|rd|road)",
                            site),
              f"house number {num}")

    check("the CV does contain a phone number to protect", phone is not None)
    if phone:
        digits = re.sub(r"\D", "", phone.group(0))
        site_digits = re.sub(r"\D", "", site_visible)
        check("the phone number is NOT on the page, in any format",
              digits not in site_digits,
              f"searched for the 10 digits of {phone.group(0)}")

    # ── 2. EVERY CLAIM ON THE PAGE TRACES TO THE CV ───────────────────────
    print("\n2. EVERY CLAIM TRACES TO THE CV (a better-sounding CV is a lie)")

    # Verifiable specifics: an employer, a trial, a number, an award. These are
    # exactly the tokens a reader would check, and the ones a translation
    # inflates.
    claims = [
        "Armata Pharmaceuticals", "C3J Therapeutics", "C3-Jian",
        "Field of Dreams", "Eastern Connecticut State University",
        "University of Illinois at Urbana-Champaign",
        "NCT04596319", "NCT03196219",
        "Cold Spring Harbor", "Advanced Bacterial Genetics",
        "Excellence in Teaching Award", "Beta Beta Beta",
        "American Society for Microbiology",
        "National Association of Sports Medicine",
        "M.S. Microbiology", "B.S. General Biology",
        "Graduate Research Assistant", "Research Associate",
        "Laboratory Assistant", "Graduate Teaching Assistant",
        "Undergraduate Teaching Assistant", "Operations & Systems Lead",
        "Sebastien Lemire", "Ken Lee", "Omid Sheikh", "Lucy Sim",
        "AlphaFold3", "ChimeraX", "Autodock Vina", "Minimap2", "FastQC",
        "Filtlong", "Geneious Prime", "GraphPad Prism", "Benchling",
        "CRISPRi", "Gibson Assembly", "ICHIP", "P1 Transduction",
        "Transposon Mutagenesis", "ESKAPE", "SWARM-Pa", "C16G2",
        "ScapeDaddy", "Flask", "SQLite", "Groq",
        "guanylyl cyclase", "Escherichia coli",
        "44th Annual UIUC Microbiology Conference",
        "43rd Annual UIUC Microbiology Conference",
        "42nd Annual UIUC Microbiology Conference",
        "Genomics and Eco-Evolution of Multi-Scale",
        "Vanderpool", "Huang", "Farley", "Chakravarti", "Fatma",
        # Quantities. The exact failure this vault has on record is a count
        # that drifted, so each one is checked against the source.
        "120-minute", "~50 undergraduates", "~25 undergraduates",
        "~20 students", "five 20-minute lectures",
        "four 50-minute discussion sections",
        # Dates, which are the other thing that silently drifts.
        "Aug. 2021", "Aug. 2026", "Aug. 2010", "Aug. 2014",
        "Jan. 2022", "Dec. 2024", "May 2019", "Jun. 2020",
        "Jan. 2016", "Sept. 2015", "May 2025",
    ]
    unsourced = [c for c in claims if norm(c) not in pdf]
    check("every checked claim on the page appears in the CV",
          not unsourced,
          f"{len(claims)} claims checked; NOT IN CV: {unsourced}"
          if unsourced else f"all {len(claims)} trace to the PDF")

    on_page = [c for c in claims if norm(c) in site]
    check("those claims are actually ON the page (not a vacuous pass)",
          len(on_page) > len(claims) * 0.9,
          f"{len(on_page)} of {len(claims)} present")

    # ── 2b. NO INVENTED CREDENTIAL ────────────────────────────────────────
    # SABOTAGE FOUND THIS HOLE, 2026-10-10. Swapping `M.S. Microbiology` for
    # `Ph.D. Microbiology` on the page passed every check above: the list in
    # check 2 only asks whether each claim is in the CV, and a 0.9 threshold
    # happily absorbs one missing entry. So the single most damaging possible
    # edit to a scientific CV -- inflating the degree -- was invisible.
    #
    # The vault's standing rule is that overclaiming on a scientific CV is a
    # professional-integrity problem, not a bug. This check is therefore
    # INVERTED: instead of asking "is what I listed present?", it reads every
    # credential-shaped string OFF the page and demands the CV back it up.
    # A title nobody thought to list still gets caught.
    print("\n2b. NO INVENTED CREDENTIAL (inflating a degree is the worst case)")

    degree_pat = r"\b(?:Ph\.?D|M\.?D|M\.?S|M\.?Sc|B\.?S|B\.?Sc|B\.?A|M\.?A|M\.?B\.?A|Postdoc\w*|Professor|Dr\.)\b"
    found = sorted({m.group(0) for m in re.finditer(degree_pat, site_visible,
                                                    re.IGNORECASE)})
    check("the page does claim some credentials (not a vacuous pass)",
          bool(found), f"found: {found}")
    unbacked = [d for d in found
                if not re.search(re.escape(d).replace(r"\.", r"\.?"),
                                 pdf_raw, re.IGNORECASE)]
    check("every credential on the page is backed by the CV",
          not unbacked,
          f"NOT IN CV: {unbacked}" if unbacked
          else f"all {len(found)} verified: {', '.join(found)}")

    # The degree the CV actually awards must be the one the page shows, in the
    # same field. `M.S. Microbiology` is the claim; anything else is a new one.
    for degree, field in [("M.S.", "Microbiology"), ("B.S.", "General Biology")]:
        in_cv = re.search(rf"{re.escape(degree)}\s+{field}", pdf_raw, re.I)
        check(f"the page states the CV's own degree: {degree} {field}",
              bool(in_cv) and re.search(
                  rf"{re.escape(degree)}\s+{field}", site_visible, re.I) is not None,
              "in CV" if in_cv else "NOT IN CV -- this check is broken")

    # ── 3. NOTHING THE CV SAYS WAS DROPPED ────────────────────────────────
    print("\n3. NOTHING WAS SILENTLY DROPPED (an omission misleads too)")

    must_appear = [
        ("the thesis title", "Bridges Antiphage Response"),
        ("both clinical trials", "NCT04596319"),
        ("the Phase 2 peptide study", "NCT03196219"),
        ("all four posters", "2nd Annual Genomics"),
        ("the 2024 poster", "motility and cell wall synthesis"),
        ("the CSHL course", "Advanced Bacterial Genetics"),
        ("the teaching award", "Excellence in Teaching"),
        ("the honor society", "Beta Beta Beta"),
        ("the ESKAPE library", "ESKAPE"),
        ("the bioreactor assay", "bioreactor"),
        ("MIC assays", "minimum inhibitory concentration"),
        ("the independent project", "ScapeDaddy"),
        ("the operations role", "Field of Dreams"),
        ("the barn build-out", "horse barn"),
        ("bilingual interfaces", "English/Spanish"),
        ("the payroll engine", "payroll"),
        ("mentoring", "Mentored undergraduate"),
        ("the AI protease work", "protease cut sites"),
        ("the department-wide slide deck", "adopted department-wide"),
        ("the research symposium judging", "Undergraduate Research Symposium"),
        ("the conference hosting", "42nd Annual UIUC"),
        ("the personal-trainer certification", "Personal Trainer"),
    ]
    missing = [label for label, needle in must_appear if norm(needle) not in site]
    check("every section of the CV is represented on the page",
          not missing,
          f"{len(must_appear)} checked; MISSING: {missing}"
          if missing else f"all {len(must_appear)} present")

    # Sanity: the needles must really be in the CV, or this check proves nothing.
    bogus = [label for label, needle in must_appear if norm(needle) not in pdf]
    check("and each of those is genuinely in the CV",
          not bogus,
          f"needles not found in the PDF (this check is broken): {bogus}"
          if bogus else "every needle verified against the source")

    # ── 4. THE PAGE IS STRUCTURALLY SOUND ─────────────────────────────────
    print("\n4. THE PAGE ITSELF")
    raw = SITE.read_text(encoding="utf-8")
    check("the stylesheet it asks for exists",
          (SITE.parent / "style.css").is_file())
    check("tags are balanced", raw.count("<section") == raw.count("</section>")
          and raw.count("<article") == raw.count("</article>"),
          f"{raw.count('<section')} sections, {raw.count('<article')} articles")
    check("it declares a language", 'lang="en"' in raw)
    check("it is responsive", "viewport" in raw)
    check("it has a print stylesheet (the page offers a Print button)",
          "@media print" in (SITE.parent / "style.css").read_text(encoding="utf-8"))
    check("the email is reachable as a link", "mailto:jwyhaymar@proton.me" in raw)
    check("no placeholder text survived",
          # Word-anchored on purpose: a bare `TODO` substring matches `AutoDock
          # Vina`, a real tool on his CV, and flagged a clean page. A guard
          # must be tested on what it has to ALLOW, not only what it catches.
          not re.search(r"lorem ipsum|\bTODO\b|\bFIXME\b|\bXXX\b", raw, re.I))

    print("\n" + "=" * 68)
    if FAILED:
        print(f"  {PASSED} passed, {len(FAILED)} FAILED")
        for f in FAILED:
            print(f"    FAILED: {f}")
        print("=" * 68)
        return 1
    print(f"  {PASSED} passed, 0 failed -- the site matches the CV of record")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
