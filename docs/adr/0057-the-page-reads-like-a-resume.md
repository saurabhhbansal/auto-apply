# The page reads like a résumé a recruiter would shortlist

**Status:** accepted — reverses `0035` §1, `0046` §4–§5, `0049`; narrows `0030` §3, `0032`, `0044` §2

## Context

Fifty-six decisions in, every rule on the page could be defended on its own, and the page they
added up to read like no résumé a recruiter would recognise. `runs/zs-btsa-english` (2026-08-24),
read cold:

- **Eight Bullets for four entries, every one of them two lines and most citing two or three
  Claims** — *"Kept unsupported claims off the page, failing the build on any figure no recorded
  claim carries, leaving what fits to a script no model can reach, and reporting the gaps it cannot
  fill."* `0049` made every Claim of a placed Entry reach the page, the merge was the only way to
  fit them, and a sentence carrying four accomplishments gets none of them read. It also put a gym
  app's 50m GPS radius on a consulting-technology résumé, because the radius was a Claim of an
  Entry that placed.
- **A narrative line above every entry's Bullets** — *"Every line of a manual was copied out by
  hand, run through an AI, pasted back in, then checked by a translator."* `0035` §1 forbade the
  run to withhold a lead the bank held, so four entries carried four scenes.
- **Random words in bold** — *reporting*, *computer science*, *prompt design* — because `0046`
  bolded up to two declared terms per line from the bank's skills and the posting's terms; and one
  bug: `~95% came`, the unit extension taking the verb after a percentage.
- **Education at the bottom of a final-year student's page**, below Skills, with nothing but the
  year.
- **`Personal project` / `Open source` on a second header row** under every project — a line
  saying nothing, twice — and no word of what either project was built with.
- **Openings no person writes** — *"Got the other product teams…"*, *"Two custom GPTs moved
  analysts…"* — because `0030` §3 allowed each opening word once per page and fifteen Bullets ran
  out of plain verbs.
- **The page 15% empty** while every Bullet was crammed. The allocation said *Spent 30, 1 left*:
  the budget was right; 8 two-line Bullets, 4 leads and two-row project headers spent it.

The tailor skill that produced it was 1,953 lines, most of it rules written to correct the
previous rule.

## Decision

### 1. The Bullet is a recruiter's bullet

One accomplishment, verb first, what was built or changed, with what, and the result — the stored
figure where there is one. **One line by default** (`width: 1`, about 95 characters); `2` only for
an entry's one or two strongest Claims when the result, the method and the scale cannot share a
line. No adjectives about the person; no sentence whose subject is a thing. The tailor skill is
rewritten around this standard and keeps every file contract the scripts read.

### 2. Education leads while the degree is recent

`render.py` places Education above Experience when the latest year in any Education row's `dates`
is this year or later, or last year — still studying, or a new graduate — and at the bottom
otherwise. `education_first: yes|no` in the profile overrides it. The last row takes the job
header's `-8pt` tail at the top, rather than a `\vspace` after the list: a separate glue node
between two lists stops their skips merging and measured a whole line. The probe calibrates
`PAGE_LINES` against both placements; 54 holds.

An optional `gpa:` key on an Education row is set after the degree.

### 3. A project's header is one row: name, stack, link, dates

`\resumeProjectHeading`, charged `PROJECT_HEADER_LINES = 1` (measured 13.66pt at a `-9pt` tail;
14.66pt at `-8pt` rounded to two). Projects gain optional `stack:` and `link:` frontmatter and may
omit `org` and `location`. `bankcheck.py` names any `stack:` technology no Claim of that project
carries — the header is typeset and traced by nothing else.

### 4. Bold is the figures and nothing else

Every `MAX_*_KEYWORDS` is 0. The keyword pass still runs, because it is how a version number
(`Python 3.11`) is recognised and left plain. A figure whose unit is already attached — `%`, `x` —
takes no following word.

### 5. A résumé is a selection

`check_coverage` no longer refuses a page that leaves a placed Entry's Claim off it: the strongest
Claims of each Entry take a line each, and the rest are reported in the Omission view exactly as
`0001` designed. Merges are for two halves of one accomplishment, not for fitting more in.

**A lead line is the run's choice.** `render.py` refuses only a lead charged that the bank cannot
supply, charged and not written, or written and not charged. The skill's default is `n`; a lead is
for an employer or product that needs one line of introduction. The x-ray no longer flags an entry
without one.

### 6. An opening word may repeat twice on a page, never in one entry

`MAX_OPENER_USES = 2`. A reader notices the same verb three times down a column; they do not notice
*Built* once under each of two jobs.

### 7. The bank holds only what a résumé or an interview can use

Added after the first review of `zs-btsa-refined`, which carried *"verifies GPS check-ins
server-side against each gym's 50m radius"* — true, traced, bold, and useless to any reader. Every
rule above checked that a fact was **true**; nothing checked that it was **worth telling**, and the
`ingest` depth pass actively asked for it (*"on a project, dig the implementation… where the data
lives, what constraint forced this design"*).

- `ingest` §3.1 adds **the résumé test**: a fact is written only if a recruiter would use it to
  decide, or the user would need it to answer *"tell me more"*. Settings, file and field names,
  plumbing, unused features, anecdote and commentary about the user stay out of the file, with
  examples. A project's technical approach is asked at architecture level, one decision per claim.
- `tailor` §5.1 and §5.3: only recruiter-relevant detail reaches a Bullet, even when the Evidence
  carries more, and **a number on the page measures impact or scale, never a setting**. The cold
  read asks it of every line.
- `bank-audit` gains a fifth check, **a cluttered claim**, quoting the phrase to delete.
- The maker's own bank was trimmed by hand under the same test: 7,054 words to 3,971, every claim
  id, figure and provenance sentence kept.

## Rejected

**Removing the Summary for students.** Recruiters disagree about it; a two-line Summary that names
the degree, the internships and the employers is useful to a screener and to keyword matching, and
`0044`'s budget already pays for it. What changed is what it may say (`tailor` §5.5): identity and
proof by name, no adjectives.

**Generalising Skills (`PostgreSQL` → `SQL`) at compose time.** The old skill licensed it and
`check_skills_trace` never allowed it. The bank stays the repair surface: the general term goes on
the Claim's `skills:` line, as a revise the user states.

## The cost, stated rather than waved past

**Claims leave the page that used to reach it.** On `zs-btsa-refined`, `american-express/c1` —
the fuzzy-matching pipeline, ~98% accurate — loses to the entry's six-line depth cap at 0.70. Under
`0049` it would have been fused into a three-claim sentence. It is reported in the Omission view
and the Gap report; on a data-management posting it places.

**The page can end short.** Eighteen one-line Bullets spend fewer lines than eight crammed ones
and a bank with little relevant evidence leaves white space. Honest white space is the right
failure; a GPA line, coursework or a supporting section is the fix, never padding.

## Consequences

`runs/zs-btsa-refined` (2026-10-10), same bank and posting as `zs-btsa-english`: 18 single-focus
Bullets against 8, no merges, no leads, Education at the top, both project headers carrying their
stacks, figures the only bold, Skills rows of hard skills only, one page, every figure traced.

`0035` §1, `0046` §4–§5 and `0049` are superseded where they conflict with the above. `CONTEXT.md`
is updated for **Lead**, **Merge**, **Opener**, **Emphasis**, **Project header** and **Education
placement**.
