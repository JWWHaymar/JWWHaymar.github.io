# salparadiise.github.io

The source of [salparadiise.github.io](https://salparadiise.github.io/) — a web
version of Jeffrey Marciniak-Haynosch's CV.

> *"Nothing behind me, everything ahead of me."* — Jack Kerouac

## What this is

Three files, no build step, no dependencies, no framework:

| File | What it is |
|---|---|
| `index.html` | The CV as semantic HTML. The content. |
| `style.css` | One hand-written stylesheet. Dark mode, responsive, and a real print stylesheet. |
| `verify.py` | **The important one.** Checks the page against the CV of record. |

GitHub Pages serves `index.html` from `main` directly. There is nothing to
compile, so the page cannot break because a toolchain moved on, and it loads in
two requests.

## `verify.py` — why a résumé site has a test suite

A CV is a professional-integrity document. The failure mode when translating one
into HTML is **not** a broken layout — it is a sentence that ends up reading
better than the truth. Nobody notices a bullet that quietly gained a word, and
on a public page under your own name that is the expensive kind of wrong.

So the page is checked against `APersonal/CV and Resumes/JWWMH_CV.pdf`, the CV
of record, on four axes:

1. **No PII.** The PDF carries a home address and a phone number, because it
   goes to one named employer at a time. This page is public and permanently
   crawlable, so neither appears on it. Both values are read *out of the PDF* at
   check time rather than typed into the script, so the guard cannot become the
   leak. The phone check compares **digits only**, so reformatting does not
   evade it.
2. **Every claim traces to the CV.** 75 verifiable specifics — every employer,
   both `NCT` trial numbers, degrees, dates, counts, named supervisors, every
   tool — must appear in the extracted PDF text.
3. **Nothing was silently dropped.** The opposite error. 22 landmarks across all
   sections must still be present. An omission is quieter than an invention and
   just as misleading.
4. **No invented credential.** Reads every credential-shaped string *off the
   page* and demands the CV back it up, so a title nobody thought to list still
   gets caught.

Run it before every push:

```bash
python3 verify.py     # exit 0 = the site matches the CV
```

An unreadable PDF **fails** rather than reporting that all zero claims verified.
An empty result is an error, never a pass.

### Three defects it caught on its first run

Worth recording, because each one is the reason the check is shaped the way it
is:

- **`AutoDock Vina` tripped the placeholder scan.** A bare `TODO` substring
  matches `AuTODOck`, so a clean page was flagged. A guard has to be tested on
  what it must **allow**, not only on what it catches. Now word-anchored.
- **`Sébastien` normalised to `se bastien`.** Unicode NFKD splits the accent
  into a combining mark, which became a word break, so a name that *is* in the
  CV reported as unsourced. Combining marks are now dropped.
- **`M.S.` → `Ph.D.` passed silently.** Found by sabotage, not by reading. The
  claim-list check only asked whether each listed claim was in the CV, and the
  0.9 threshold absorbed one missing entry — so the single most damaging edit
  possible to a scientific CV was invisible. That is why check 4 exists and is
  **inverted**: it reads credentials off the page rather than looking for
  expected ones.

Each is verified to fail against the old code.

## Editing it

The CV is the source of truth, not this page. When the PDF changes, update
`index.html` to match and re-run `verify.py`; if you add a new claim, add it to
the claim list so it is held to the same standard. The script is the thing that
keeps the two honest, so **do not** edit the page and skip it.

## Print

The page has a *Print / save as PDF* button, so `@media print` is a feature and
not an afterthought: the dark header inverts to ink-on-paper, interactive
controls disappear, and no entry is allowed to break across a page boundary.
