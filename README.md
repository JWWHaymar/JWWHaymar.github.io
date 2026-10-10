# salparadiise.github.io

Jeffrey Marciniak-Haynosch — microbiologist and bacteriophage researcher.
Live at [salparadiise.github.io](https://salparadiise.github.io/).

> *"Nothing behind me, everything ahead of me."* — Jack Kerouac

## This directory is generated. Do not hand-edit it.

Everything here is built by **`JobSearch/site.py`** in the Awy vault, from
`APersonal/CV and Resumes/JWWMH_CV.pdf` via `spine.parse()`:

```bash
python3 JobSearch/site.py --build     # writes ~/awy-site
```

Then the contents are copied here and pushed.

**Why generated and not written by hand** — this is `site.py`'s own reasoning,
and it was proven correct the day this site went up:

> A hand-written site would be a FIFTH copy of his history, the only one with no
> parser and no gate, published under his name on the public internet. When he
> updates his CV — and he will — the site would silently become the stale one.

That is exactly what happened. The first version of this site *was*
hand-written, and within the hour the graduation month changed from August to
September 2026. The hand-written page had to be found and edited; the generated
one picked the new date up from the CV with no edit at all. Hence: **change the
CV, rebuild, push.** Never edit the HTML.

## Pages

| Page | What it is |
|---|---|
| `index.html` | Landing page — research focus, news, positions |
| `cv.html` | The full CV |
| `thesis.html` | The master's thesis, with the PDF |
| `JWWMH_CV.pdf` | Downloadable CV, **regenerated with the address and phone removed** |

## `verify.py` — why a résumé site has a test suite

A CV is a professional-integrity document. The failure mode is not a broken
layout, it is **a sentence that reads better than the truth**. Nobody notices a
bullet that quietly gained a word, and on a public page under your own name that
is the expensive kind of wrong.

```bash
python3 verify.py     # exit 0 = every page matches the CV of record
```

Five axes, each one a real incident:

1. **No PII on any page.** The protected values are read *out of the CV PDF* at
   check time rather than typed into the script, so the guard cannot become the
   leak. Phone is matched on **digits only**, so reformatting does not evade it.
2. **No PII in the downloadable PDF.** The other half, and the one that was
   actually broken: see below.
3. **Every claim traces to the CV** — employers, both `NCT` numbers, degrees,
   counts, supervisors, tools.
4. **No invented credential, and no drifted date.** Both *inverted*: they read
   credentials and date ranges *off the page* and demand the CV back each one,
   so a value nobody thought to list is still caught.
5. **Nothing was silently dropped.** An omission is quieter than an invention
   and just as misleading.

### What it caught, and what the design cost

Recorded because each one explains a line of the script:

- **`site.py` published the unredacted CV.** `build()` did
  `shutil.copy2(CV_PDF, ...)`, and page 1 of that PDF carries a street address
  and phone, because a CV is sent to *one named employer at a time*. The HTML
  was already careful — city and state only — so the care stopped exactly one
  line short of the file it linked as "Download PDF". The PDF is now
  **regenerated** from the CV's HTML source with the contact line rewritten, and
  if the redaction cannot be verified it **refuses to publish** rather than
  falling back to the unredacted file.
- **`M.S.` → `Ph.D.` passed silently.** Found by sabotage, not by reading. A
  list of expected claims can notice a value that *vanished*, never one that
  *changed*, and a 0.9 threshold swallowed the difference. Checks 2b and 2c
  exist because of this.
- **A date change passed too** — `Aug. 2026` → `Sept. 2026`, and Armata inflated
  from `2019–2020` to `2017–2023`, a four-year tenure that never happened.
- **"Looking for a PhD lab" is not a claimed PhD.** The credential check flagged
  it. A guard that cries wolf is one that gets switched off, so a match is
  skipped when the surrounding words make it an aspiration.
- **`AutoDock Vina` tripped the placeholder scan** (`AuTODOck`), and
  **`Sébastien` normalised to `se bastien`** because Unicode NFKD turns the
  accent into a word break.

Every one is verified to fail against the code that preceded it.

## Updating

1. Edit `APersonal/JWWMH_CV_Coordinator.html` — the HTML the CV PDF is rendered
   from — and regenerate: `weasyprint <that file> 'APersonal/CV and
   Resumes/JWWMH_CV.pdf'`.
2. `python3 JobSearch/spine.py --check` — confirm the parse still reads it.
3. `python3 JobSearch/site.py --build`, copy to this repo, `python3 verify.py`.
4. Push.
