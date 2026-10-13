# salparadiise.github.io

My corner of the internet. I am Jeffrey Marciniak-Haynosch, a microbiologist
devoted to harnessing the microbial world at the interface of bacteriophages
and their hosts.


**The site:** <https://salparadiise.github.io/SalParadiise/>

> *"Nothing behind me, everything ahead of me."* — Jack Kerouac

## What's here

| Page | What it is |
|---|---|
| `index.html` | The landing page — what I work on, where I've been, what's new |
| `cv.html` | My CV |
| `thesis.html` | My master's thesis, with the PDF |
| `JWWMH_CV.pdf` | The CV as a download |

## A note on how this is put together

I don't write these pages by hand, and there's a story behind that.

The first version of this site *was* hand-written. Within the hour, my
graduation month moved from August to September 2026. I updated my CV, and the
website quietly went on saying August — because nothing connected the two. A
personal site that disagrees with your own CV is worse than no site at all.

So now the pages are built from the CV itself. I change the CV, run the
builder, and the site follows. One source, one truth, no stale copies of my own
history floating around.

```bash
python3 JobSearch/site.py --build     # builds into ~/awy-site
```

The builder lives in my notes vault (`JobSearch/site.py`), not in this repo.
**Everything in here is generated — don't edit the HTML, it will be overwritten.**

## `verify.py` — yes, my résumé has a test suite

That sounds excessive. Here's why it isn't.

A CV is a professional-integrity document. The failure I'm actually worried
about isn't a broken layout, it's **a sentence that reads a little better than
the truth**. Nobody notices a bullet that quietly gained a word. On a public
page with my name at the top, that's the expensive kind of wrong.

```bash
python3 verify.py     # exit 0 = every page matches the CV of record
```

It checks five things, and each one exists because something actually went
wrong:

1. **No home address or phone on any page.** It reads those values *out of the
   CV PDF* at check time rather than having them typed into the script — so the
   guard can't become the leak. The phone is matched on digits alone, so
   reformatting it doesn't sneak it past.
2. **No address or phone in the downloadable PDF either.** This is the one that
   was genuinely broken. The HTML was careful — city and state only — and then
   the "Download PDF" link handed over the unredacted file. The care stopped
   one line short of the thing it linked to.
3. **Every claim traces back to the CV** — employers, trial numbers, degrees,
   dates, supervisors, techniques.
4. **No invented credential, and no drifted date.** Both checks run *backwards*:
   they read the credentials and dates off the page and demand the CV account
   for each one. That way a claim nobody thought to add to a list still gets
   caught.
5. **Nothing silently dropped.** An omission is quieter than an invention and
   just as misleading.

### The one that convinced me this was worth building

I changed `M.S.` to `Ph.D.` on the page as a test, and **every check passed.**

A list of expected claims can notice something that *vanished*. It can't notice
something that *changed*. The single most damaging edit possible on a
scientific CV — inflating a master's into a doctorate — was invisible to the
thing I'd built to prevent exactly that.

Checks 4 and 5 exist because of that afternoon. A few others came out of the
same session: `AutoDock Vina` tripped a placeholder scan because `AuTODOck`
contains `TODO`, and `Sébastien` failed to match my own CV because Unicode
normalisation split the accent into a separate character and broke the word in
half.

## Updating my CV

1. Edit `APersonal/JWWMH_CV_Coordinator.html` in my vault and re-render it:
   `weasyprint <that file> 'APersonal/CV and Resumes/JWWMH_CV.pdf'`
2. `python3 JobSearch/spine.py --check` — confirm the parser still reads it
3. `python3 JobSearch/cv_md.py --write` — refresh the readable Markdown copy
4. `python3 JobSearch/site.py --build`, copy here, `python3 verify.py`
5. Push

## Elsewhere

Email: jwyhaymar@proton.me
