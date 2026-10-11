<!--
  The committed template you hand-write bank/profile.md from.

  This is the Static profile — name, contact, links and Education. It is NOT a
  Bank entry: it never competes for Slots, and no ingestion session writes it
  (docs/adr/0013-ingestion-shape.md §7). You write it once, by hand, and edit it
  when your phone number changes.

  THE KEYS BELOW ARE THE CONTRACT. tools/render.py validates bank/profile.md by
  field name against them and fails naming the key — a missing key and an unknown
  key are both hard failures, so a typo in your own contact block stops the run
  instead of rendering an empty header.

  `name`, `location` and `email` are required and may not be blank. `phone`,
  `linkedin` and `github` are optional: leave one out, or blank, and the header
  drops it with its separator.

  Shape mirrors an Entry file on purpose: a YAML-ish frontmatter block of loose
  `key: value` lines for the scalars, then one `###` section per school. The
  parser is stdlib-only and line-based — do not expect real YAML (no nesting, no
  quoting, no lists in the frontmatter). Values are taken literally to end of
  line, so write `location: Bengaluru, India` and not `location: "Bengaluru, India"`.

  Education ids (e1, e2, …) are opaque, sequential and content-independent, the
  same convention as Claim ids. Nothing traces to them; they exist so each school
  has a heading.

  `email`, `linkedin` and `github` land inside LaTeX \href targets, so keep them
  plain — no spaces, %, #, &, $, ^, backslashes or braces. Underscores and tildes
  are fine. A bad character inside a link target breaks the link rather than the
  compile, which is the kind of failure nothing downstream will catch.

  KEEP THE HEADER TO TWO LINES. `name` is one typeset line, and `location`,
  `phone`, `email`, `linkedin` and `github` are joined into a second — around 120
  characters between them at the current template. The page budget charges the
  header exactly that, so a line that wraps spends a line of evidence nobody
  granted. tools/render.py refuses to finish the run if either wraps, names which
  one, and says roughly how many characters to cut; the choice of what to shorten
  is yours.

  THE ONE OPTIONAL BLOCK, and the only free-prose part of this file: `## Standing`.
  It holds what you are, in your own words — the durable self-description no single
  Claim carries and no Entry header states. It is what the Summary at the top of the
  page is composed from where the Claims cannot supply the fact
  (docs/adr/0044-the-page-opens-on-a-summary.md §3).

  One fact per line, and nothing wrapped: a line is a fact. Write what is true across
  every application and would otherwise have to be inferred from a couple of job
  titles — what you are studying or have studied, what kind of work you build, what
  you are looking for. Nothing here is typeset, nothing validates it, and nothing on
  the page may cite it.

  WHAT IT IS FOR is keeping the Summary honest. Without it the only self-description
  available is one the model made up: your titles are what your entries say they are,
  and a Summary opening with a title you do not hold is exactly the failure the
  Summary's own rules forbid. Leave the block out and the page still renders — the
  Summary is composed from the entry headers and the Claims, and tools/bankcheck.py
  prints a line saying so.

  WHAT A RECRUITER LOOKS FOR HERE, briefly:

  - `location` is a city and country — `Bengaluru, India`, not `India`. Recruiters
    filter on it, and a bare country reads as a field left half-filled.
  - An Education row's `dates` say when the degree ends; while you are still
    studying write `Expected May 2027`, so nobody reads a future year as a typo.
  - Two OPTIONAL keys, left out of the example below because neither is needed:
      `gpa: CGPA 8.4/10` on an Education row — set after the degree, as written.
        Include it when it helps (roughly 3.5/4 or 8/10 and up, or when the posting
        asks); leave it out otherwise.
      `education_first: yes` or `no` in the frontmatter — where Education sits.
        Left out, the dates decide: still studying, or finished within the last
        year, puts it at the top of the page, where a new graduate's reader looks
        first. Anyone further along keeps it at the bottom.
  - School rows beyond your degree (Class 12, a diploma) are worth a line only
    while you're a student; drop them a year or two into work.

  Delete this comment block in your own bank/profile.md, or leave it — the parser
  ignores HTML comments.
-->

---
name: Ada Lovelace
location: Bengaluru, India
phone: +91 98765 43210
email: ada.lovelace@example.com
linkedin: linkedin.com/in/adalovelace
github: github.com/adalovelace
---

## Education

### e1
institution: Indian Institute of Technology Bombay
location: Mumbai, India
degree: B.Tech., Computer Science and Engineering
dates: Aug 2013 -- May 2017

## Standing

Computer Science graduate (IIT Bombay, 2017).
Builds distributed systems and the analytical tooling around them.
Looking for backend platform work.
