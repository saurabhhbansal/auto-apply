# Survey: frameworks for writing experience accounts — what they are, and what they actually claim

Resolves #71 (research). Judged on **whether the framework survives this repo's constraints** —
a **Bullet** of `CHARS_PER_BULLET = 103` composed from **exactly one Claim**, up to six of them in
one **Entry**, with a **downgrade-only trace** to the bank — and, above all, on whether it has
anything to say about the **Entry as one account** rather than about one line. Provenance was
followed to the source that owns the claim; where a framework turns out to be blog-repeats-blog,
that is stated rather than smoothed over.

**Headline, stated up front so it is not buried.** Two of the nine candidates are the only ones with
a traceable owner *and* something to say above the bullet, and they say almost the same thing:
**OPM's CCAR** (US Office of Personnel Management) and the **Enelow–Kursmark "use context to create
impact" structure** both put the situation in a **lead unit that is not one of the bullets**, and both
treat Challenge/Context/Action/Result as a shape for **a whole account**, explicitly *not* for one
line. Enelow and Kursmark — the two people who built the résumé-writing certification industry — say
in their own words that a CAR story is **"typically too much for a résumé"** and belongs in
preparation, which is exactly where this repo already puts it (the Claim + Evidence in the bank).

---

## TL;DR classification

| # | Framework | Traceable origin? | Designed for | Evidence | Fits a 103-char Bullet? | Verdict for this repo |
|---|-----------|-------------------|--------------|----------|--------------------------|------------------------|
| 1 | **STAR** (Situation, Task, Action, Result) | Yes — **DDI, self-dated 1974**, inside Targeted Selection | **Spoken behavioural-interview answers**, and giving feedback | First-party assertion only; the *underlying* method (past-behaviour interviewing) is well validated, the *acronym* is not | **No.** Four beats, one of which is scene-setting | **Reject as a Bullet shape. Keep as the Entry arc's ancestor** — which is what #70 already did |
| 2 | **Behaviour Description Interviewing** (Janz) | Yes — Janz, *JAP* 1982; Janz/Hellervik/Gilmore book 1986 | Interviewer technique | **Real empirical study** (validity .54 vs .07 vs unstructured) | n/a — not a writing framework | **Read once.** It is STAR's evidential parent, and it is about interviewing, full stop |
| 3 | **CCAR** (Challenge, Context, Action, Result) | Yes — **US OPM**, published federal guidance | A **multi-paragraph written narrative** (SES ECQ statement) | Government-mandated procedure + published worked examples from real review-board cases | **No** — the unit is pages | **Take the structural lesson.** The single best public evidence that the account, not the line, is the unit |
| 4 | **CAR / PAR / SAR / CARS** | **No.** No coiner, no first publication, anywhere | Résumé accomplishment statements — but see below | **None.** Widely repeated, no traceable origin | Partly — three beats can fit | **Do not cite as authority.** Its most credentialed users say the full story is too big for the page |
| 5 | **Enelow–Kursmark entry structure** (scope/context paragraph → achievement bullets) | Yes — Enelow & Kursmark, named authors, published toolkit and books | **The résumé entry as a unit** | Practitioner authority (30+ yrs, 30+ books, founded the certifications); no experiment | The *bullets* do (≈97 chars typical); the lead paragraph does not | **The most directly useful source in the survey.** Adopt the idea, adapt the mechanism |
| 6 | **XYZ** — "accomplished [X] as measured by [Y] by doing [Z]" | Yes — **Laszlo Bock, LinkedIn, Sept 2014**, later *Work Rules!* | **Résumé lines specifically** | **None offered.** Worked examples and a rationale; no data | **Marginal.** Bock's own showcase example is **186 characters** | **Take the ordering rule, not the formula.** Lead with the change, then the method |
| 7 | **APR** (Action, Project, Result) — Yale OCS | Yes, as a career-centre restatement | Résumé bullets | Institutional guidance, no study | Yes | **Already what this repo does.** Nothing new |
| 8 | **SOAR** (Situation, Obstacle, Action, Result) | **No.** No coiner findable | Interview answers | **None** | No | **Ignore.** STAR with a synonym swapped in |
| 9 | **STAR-L / STARL** | **No.** Appears at several universities with no attribution | Reflection, then interviews | **None** | No | **Ignore for the résumé.** The `L` is for a learner's journal |
| 10 | **CARL** (Context, Action, Result, Learning) | Partly — Edinburgh's Reflection Toolkit, itself citing *"BlueSteps (2011)"* | **Reflective practice**, not résumés | Cites one dead-end secondary source | No | **Ignore.** Edinburgh is honest that it is a borrowed interview technique repurposed for reflection |
| — | **Parallelism rules** (Purdue OWL, Microsoft Style Guide, résumé research) | Yes — established style authorities | Lists in any document | Style-guide consensus + one empirical résumé study | n/a | **Actively contradicts `0027` §2.** Read the section below before defending that ADR |

---

## 1. STAR — Situation, Task, Action, Result

- **Link:** https://www.ddi.com/solutions/behavioral-interviewing/star-method ·
  https://www.ddi.com/solutions/targeted-selection
- **Origin.** DDI (Development Dimensions International, founded 1970 by William C. Byham and
  Douglas Bray) claims it as theirs: *"DDI introduced the STAR Method in 1974 with Targeted
  Selection and has been shaping behavioral interviewing for over 50 years."* That is a **first-party
  assertion on a marketing page**. No independent 1974 document was findable; the claim is plausible
  (Targeted Selection is genuinely a 1970s DDI product) but it is **not corroborated**.
- **What it was designed for.** DDI's own page names exactly two uses: **interviews** ("prompting
  candidates to share real-life examples rather than hypothetical responses") and **feedback**
  ("connecting specific actions to measurable outcomes"). **It does not mention résumés at all.**
  This is the ticket's question 1 answered by the framework's own owner.
- **Evidence.** The evidence people *mean* when they say STAR is evidence-based is the evidence for
  **structured past-behaviour interviewing** (item 2), which is real and which STAR merely packages.
  There is no study of the STAR acronym as such — no study of whether an answer with a labelled
  Situation beats one without.
- **Shape.** Note DDI's own gloss collapses the first two beats: **"ST: Situation/Task"**. Even the
  owner treats S and T as one move. The maker's *"STAR is sometimes TAR or SAR"* is not a heresy; it
  is closer to DDI than the four-letter version is.
- **Verdict at 103 characters: no.** Four beats in 103 characters produces the compression fault
  `0027` §1 was written against — a line that stops before its own argument is finished. STAR's
  real contribution to this project is the one #70 already took: **lift it a level, to the Entry.**

## 2. Behaviour Description Interviewing (Janz) — STAR's actual evidence

- **Link:** https://link.springer.com/article/10.1023/A:1022974232557 (Janz's 1982 study is
  *Journal of Applied Psychology* 67(5), 577–580) · book:
  https://archive.org/details/behaviordescript00janz
- **Origin.** Tom Janz, 1982, *"Initial comparisons of patterned behavior-based interviews versus
  unstructured interviews"*; book with Hellervik and Gilmore, Allyn & Bacon, 1986.
- **Evidence.** A real experiment: fifteen teaching assistants interviewed by trained and untrained
  interviewers. Validity **.54** for behaviour-description interviews vs **.07** for unstructured —
  though reliability went the other way (.46 vs .71), on a tiny sample.
- **Why it matters here.** It is the only genuinely empirical thing anywhere near this family, and
  **it is about the interviewer's questions, not the candidate's prose.** Anyone citing "STAR is
  proven" is borrowing this study's authority for a claim it never made.

## 3. CCAR — Challenge, Context, Action, Result (US OPM)

- **Link:** https://www.opm.gov/policy-data-oversight/senior-executive-service/reference-materials/guidetosesquals_2010.pdf
  (2010 edition, pp. 8–21 — the one that governs *written* narratives) ·
  https://www.opm.gov/policy-data-oversight/senior-executive-service/reference-materials/guide-to-ses-qualifications.pdf
  (current edition, Appendix 3, where CCAR now governs the interview)
- **Origin.** The US Office of Personnel Management, in its official *Guide to the Senior Executive
  Service Qualifications*. This is **published guidance from a government body that runs the process
  it describes** — the strongest provenance in the survey.
- **What it was designed for.** A **written Executive Core Qualification statement**: multiple
  paragraphs, per competency, read by a Qualifications Review Board. Not a line. Not a bullet.
- **Evidence.** Not a study, but better than a study for our purposes: **worked examples drawn from
  actual QRB cases**, annotated beat by beat, in a document that is the operative standard for a real
  selection process.
- **Four findings this repo should read carefully.** All four are direct quotes:
  1. **The account opens on a summary.** *"Begin your ECQ statement with a brief summary of your
     executive experience. Then use the following approach to describe your accomplishments."*
     An opening beat above the individual accomplishments — structurally what #70 is proposing.
  2. **Beats recur and interleave; they are not a sequence.** In OPM's own annotated example the
     labels run `(Context) … (Challenge) … (Action) … (Context) … (Result)` and then start over for a
     second example inside the same narrative. **CCAR is a set of beats an account must hit, not an
     order it must follow.** That is a strong external licence for #70's *"any beat may be absent"*.
  3. **The shape must not be visible.** *"Candidates should keep the CCAR model in mind as they write
     their qualifications statements but they should not annotate these statements with 'Challenge,'
     'Context,' 'Action,' or 'Result.'"* This is `0027` §2's *must not read like a form*, said by a
     government body, about the same shape #70 wants to adopt.
  4. **Multiple examples per unit are allowed and bounded.** *"An ECQ statement may include one or
     more examples of relevant experience. The number of examples is not as important as assuring
     that your experience matches the ECQ criteria."* The current edition tightens this to *"one or
     two examples (not more than two)"*. The unit of judgement is the **account**, and the count of
     items inside it is explicitly declared not to be the point — which is the same move #70 makes in
     retiring the six-Bullet quota.
- **Vocabulary collision.** OPM's **Context** is this repo's **Evidence** (the dug-out backstory),
  not anything that renders. OPM's **Challenge** is closest to #70's *opening beat*. OPM has no unit
  corresponding to a **Bullet** at all — and note that the current OPM résumé sample *does* use
  bullets, but groups them under **competency headings**, not as one flat column (see question 2).
- **Verdict at 103 characters: not applicable, and that is the point.** CCAR is evidence that the
  people who run a high-stakes selection process think the natural unit for a challenge-action-result
  shape is **an account of several hundred words**. Transplanting it to 103 characters is a
  reinterpretation this project is choosing to make — the sources do not support it, but neither do
  they contradict lifting it to the Entry, which is what #70 actually does.

## 4. CAR / PAR / SAR / CARS — the acronym family with no parent

- **Links (representative, none authoritative):**
  https://www.canr.msu.edu/news/challenge_action_result_statements_car_statements_part_3 ·
  https://ca.indeed.com/career-advice/resumes-cover-letters/challenge-action-result-resume ·
  https://careers.augustana.edu/resources/the-par-method/
- **Origin: none findable.** This was hunted specifically. There is no coiner, no first publication,
  no originating institution for **Challenge-Action-Result**, **Problem-Action-Result**,
  **Situation-Action-Result** or **CARS**. Every source that defines them defines them by restating
  the acronym and citing nobody. The Edinburgh reflection toolkit, which is unusually careful,
  attributes CAR to *"BlueSteps (2011) CAR interview Technique"* — an executive-search membership
  site, itself citing nothing.
- **What it was designed for.** Asserted to be résumé accomplishment statements. But the most
  credentialed practitioners who use it — Enelow and Kursmark, item 5 — use it as an **interview and
  memory-retrieval exercise** and say the story is too big for the page.
- **Evidence: none.** Not one study manipulates CAR-shaped bullets against non-CAR bullets. The
  closest empirical thing in the literature is Bright & Hutton (2000), *"The impact of competency
  statements on résumés for short-listing decisions"*, IJSA 8(2), 41–53
  (https://onlinelibrary.wiley.com/doi/abs/10.1111/1468-2389.00132) — sixty-two managers and HR
  consultants rating genuine résumés; résumés carrying **competency statements** were rated more
  suitable and more likely to be invited to interview. That supports *"say what you achieved and how
  it was measured"*. It says nothing about the C-A-R ordering. (Paywalled; abstract read.)
- **Verdict: usable, unauthoritative.** Three beats can fit 103 characters. But **do not put "CAR"
  in an ADR as though it were a standard.** It is a mnemonic with no owner.

## 5. Enelow–Kursmark — the entry as a unit (the survey's most useful source)

- **Link:** https://michiganross.umich.edu/sites/default/files/uploads/Alumni/pdfs/exectoolkit-resume-writing-guide.pdf
  (the *Enelow–Kursmark Executive Resume Toolkit*, hosted by Michigan Ross; the Professional
  Experience section is pp. 26–31 of the guide's own numbering, PDF pages 28–33) · worksheets:
  https://michiganross.umich.edu/sites/default/files/uploads/Alumni/pdfs/exectoolkit-worksheets.pdf
- **Origin.** Wendy Enelow and Louise Kursmark — between them 30+ years each as professional résumé
  writers, 30+ books, and the founders of the Resume Writing Academy, Career Masters Institute and
  Career Thought Leaders. If the résumé-writing profession has a canon, they wrote it.
- **Evidence.** Practitioner authority and worked examples. **No experiment, no citation of any.**
  Treat it as the best-informed opinion available, not as proof.
- **The rule, verbatim:** *"**Use context to create impact.** Before plunging into your achievements,
  help readers understand 'what was going on' so that they can better appreciate what you did. We
  recommend starting with a brief description of the company, job scope, and key challenges, followed
  by bullet points that describe specific accomplishments."*
- **The other rule, verbatim, and it is the one that decides question 1:** *"We recommend writing
  your achievements in the form of CAR (Challenge-Action-Results) stories. **Although typically too
  much for a resume**, these stories contain nuggets of information that you can pull out for your
  accomplishment statements."*
- **Five entry-level formats they publish** — this is the closest thing in existence to a taxonomy of
  Entry arcs:
  | Format | Shape | This repo's analogue |
  |---|---|---|
  | **Achievement** | Aggregate lead sentence → scope sentence → achievement bullets | Closing beat, moved to the front |
  | **CAR** | Literal `Challenge:` / `Action:` / `Results:` labels, bullets only under Results | What OPM explicitly forbids; a form on the page |
  | **Career Track** | Promotion stack → one paragraph carrying the **whole-tenure number** → bullets | The aggregate as a *fact about the entry* |
  | **Project Highlights** | Scope paragraph → named project blocks each ending `RESULTS:` | Thematic grouping across claims |
  | **Functional** | Scope paragraph → **thematic lead bullets** with indented sub-bullets carrying the numbers | The merge, and its evidence beneath it |
- **Measured against 103 characters.** Their ordinary achievement bullets sit comfortably in budget —
  *"Captured six new Fortune 1000 accounts within first eight months for $28 million in new
  revenues"* is **97**. Their **lead paragraphs do not**: the Achievement-format opener is **208**,
  the Career Track aggregate sentence **157**, the CAR `Challenge:` line **181**. **The opening beat
  is roughly twice a Bullet in every published example.**
- **Also worth noting for the Packer.** *"Devote the most effort, and the most space, to your most
  recent positions. As you work backwards, strive to come up with one or two sentences to highlight
  the most significant achievements of your early positions."* Depth allocation across Entries, stated
  as a rule — adjacent to, but not the same as, this repo's Entry floor.

## 6. XYZ — "accomplished [X] as measured by [Y] by doing [Z]"

- **Link:** https://www.linkedin.com/pulse/20140929001534-24454816-my-personal-formula-for-a-better-resume
  (Laszlo Bock, LinkedIn, September 2014; later folded into *Work Rules!*, 2015)
- **Origin.** Fully traceable, single-author, dated. Bock was Google's SVP of People Operations. Note
  the **framework is Bock's, not Google's** — Google's own hiring pages carry no such formula; the
  "Google formula" framing is a downstream invention.
- **What it was designed for.** **Résumé lines, explicitly** — the only framework in this survey that
  was born for the artefact this project renders. *"The sole purpose of a resume is to get you past
  that first screen and into an interview."*
- **Evidence: none offered.** Seven before/after examples and a rationale. No study, no hiring data,
  no A/B. For a claim this widely repeated, that is worth saying plainly.
- **The 103-character problem, measured.** Bock's own showcase "good" example is
  *"Improved portfolio performance by 12% ($1.2M) over one year by refining cost of capital
  calculations for information-poor markets and re-weighting portfolio based on resulting
  valuations"* — **186 characters**, i.e. **1.8× this repo's Bullet**, and it would need `width: 2`
  plus another 80 characters this template does not have. His "bad" example is **78**. So the
  formula's own demonstration of quality is **a line this project cannot render**.
- **What survives the transplant.** Not the three slots — the **ordering**: change first, measure
  attached to it, method last. That is already `0027`'s deleted-then-restored territory, and Yale
  restates it as its second recommended structure (*"[X] Lead with the impact you delivered + [Y]
  Numerically measure what you accomplished + [Z] Detail specifically what you did"*,
  https://ocs.yale.edu/resources/writing-impactful-resume-bullets/). Note that `0027` §2 explicitly
  refused to make *lead with the change* mandatory, and XYZ is exactly the rule it refused. **The
  sources do not settle that argument; they only show the rule is popular.**

## 7–9. SOAR, STAR-L/STARL, CARL — the derivative tier

Grouped because the finding is the same for all three: **an extra letter, no owner, no evidence.**

- **SOAR** (Situation, Obstacle, Action, Result). No coiner findable. Marketed as *"makes STAR look
  outdated"* by a careers blog (https://blog.theinterviewguys.com/the-soar-method/). Recruiting firms
  present it as a STAR variant (https://www.astoncarter.com/en-au/insights/articles/behavioural-interview-techniques-star-soar).
  **Obstacle** is Situation renamed. Ignore.
- **STAR-L / STARL** (…Learning). Turns up at Waterloo
  (https://uwaterloo.ca/centre-for-teaching-excellence/sites/default/files/uploads/files/reflection_prompts_and_frameworks_handout_1.pdf)
  and in Stanford career-education material, each without attribution. The `L` is a **reflection**
  beat — what the experience taught *you*. There is no reading of this repo's Bullet where a
  self-development sentence earns 103 characters against a JD. Ignore.
- **CARL** (Context, Action, Result, Learning). The one honest source is the University of
  Edinburgh's Reflection Toolkit (https://reflection.ed.ac.uk/reflectors-toolkit/reflecting-on-experience/carl),
  which says outright it is *"adapted from a job interview technique"* and cites *"BlueSteps (2011)
  CAR interview Technique"*. Edinburgh presents it as a **reflective-practice** tool, not a résumé
  tool. (Do not confuse it with the **Bass Model of Holistic Reflection** — Bass, Fenwick &
  Sidebotham, *Women and Birth* 30(3), 2017 — a genuinely peer-reviewed reflection model that is
  sometimes mis-cited as CARL's source. It is unrelated.)

---

## Question 1 — interview answer, or résumé bullet?

**Answered decisively, and against STAR.**

1. **STAR's owner says so.** DDI's own page lists STAR's uses as interviews and feedback and
   **never mentions résumés**. The evidential parent (Janz 1982/1986) is a study of *interviewer
   technique*.
2. **The résumé profession's own canon says so.** Enelow and Kursmark, who teach CAR to certified
   résumé writers, write that a CAR story is *"typically too much for a resume"* and that its role is
   to hold *"nuggets of information that you can pull out for your accomplishment statements."*
   **That is precisely this repo's Claim/Evidence-to-Bullet relationship, described by someone who
   arrived at it independently.** The bank is the CAR story; the Bullet is the nugget.
3. **The measurements confirm it.** Every published example of a full situation-carrying opener runs
   **157–208 characters**. Every published example of an achievement *bullet* runs **50–115**. The
   103-character line is a bullet-sized object in the sources' terms, and the situation-carrying
   sentence is not.
4. **The one framework born for résumés fails the width test anyway.** Bock's XYZ is résumé-native
   and its canonical good example is **186 characters**.

**Vocabulary collision to record.** When these sources say "bullet" they mean one to two typeset
lines across a full-width US-Letter page at 10–11pt — call it 110–190 characters of room. This
repo's Bullet is **103 characters and single-line by default**, because `CHARS_PER_BULLET` is a
measurement of the Template, not a policy (`0025`). **Every "this fits in a bullet" claim in the
external literature is made about roughly 1.5–2× the room this project has.** That is the transplant
cost, and it is the real reason a four-beat shape cannot land on one line here.

**Two further collisions, both uncomfortable, both to be recorded rather than argued away:**

- **Harvard OCS, *Resumes & Cover Letters* (2021), explicitly lists "Use a narrative style" under
  DON'T** (https://static1.squarespace.com/static/592b51c18419c2e1dd15123b/t/636e9bd189d2e53f6a7b693f/1668193233792/undergrad_resumes_and_cover_letters.pdf,
  p. 3). #70's destination is *"one account of what you did there"*. A major career service says the
  résumé is not the place for one. This is not fatal — Harvard is writing for undergraduates with
  three-line entries, and Enelow/Kursmark and OPM both disagree for senior candidates — but the
  disagreement is real and should be named in the ADR rather than discovered later.
- **Harvard also says "each line should be a phrase rather than a full sentence."** `0027` §1 says a
  Bullet **is** a complete sentence. This repo's rule is defensible on its own reasoning
  (grammaticality as the tripwire for over-compression) but it is **not** the majority convention.

---

## Question 2 — does anything operate ABOVE the bullet? (the valuable one)

**Yes. Three independent sources, and they agree on the mechanism.** This is the most important
section of this document.

### 2a. The situation lives in a lead unit that is not one of the bullets

Both credible sources put it there, and neither puts it in bullet 1.

- **Enelow–Kursmark:** *"Before plunging into your achievements, help readers understand 'what was
  going on' … We recommend starting with a brief description of the company, job scope, and key
  challenges, **followed by** bullet points that describe specific accomplishments."*
- **OPM:** *"Begin your ECQ statement with a brief summary of your executive experience. Then use the
  following approach to describe your accomplishments."*

**Implication for #70.** The Entry arc's **opening beat is architecturally a different kind of object
from a middle beat** in every source that has one. It is unbulleted, it is longer, it is not an
achievement, and it does not compete with the achievements for space — it buys their comprehension.
#70 currently proposes the opening beat as a Bullet like any other. The sources say it is not one.
This project cannot copy the mechanism (`0027` §2's *no fixed shape*, plus the one-Bullet-one-Claim
trace, plus 103 characters, plus a template with no unbulleted entry text) — but **the fact that both
independent sources reached the same structure is evidence the beat is real**, and it raises a
question #72 should answer explicitly: *does the opening beat get the same 103 characters as
everything else, or is it a different object?*

### 2b. Bullets are grouped thematically, not left as a flat column

This is the second above-the-bullet move, and it appears in three places:

- **Enelow–Kursmark's Functional format**: bullets carry a bold **theme label** (*"Turnaround
  Leadership / Revenue & Profit Performance:"*), a merged sentence, and then **indented sub-bullets
  carrying the individual numbers** (*"Grew revenues 225%, profits 353%, and customer base 24% in
  4 years"*). One theme, one claim-shaped lead, evidence beneath it.
- **Enelow–Kursmark's Project Highlights format**: named project blocks, each ending in `RESULTS:`.
- **OPM's own current sample résumé** (Appendix 2 of the current guide): a two-page executive résumé
  whose bullets are grouped under **ECQ competency headings** — *Driving Efficiency*, *Merit and
  Competence* — rather than run as one flat list.

**This is directly relevant to the Amex column that set #70 off.** Six bullets that are *"six
separate automations of pieces of the same monthly reporting cycle"* are, in the published
vocabulary, **one theme with five instances** — and every source that has faced that situation solves
it by naming the theme once and putting the instances beneath it, not by giving each instance an
equal, independent line.

### 2c. Ordering within an entry: "most relevant / most impressive first", and that is all anyone says

- **Purdue OWL**, Work Experience Section: *"Each job should have a minimum of three bulleted items
  with the most relevant duties listed first."*
  (https://owl.purdue.edu/owl/job_search_writing/resumes_and_vitas/resume_sections/work_experience_section.html)
- **UC San Diego Career Center**: *"Highlight your most impressive responsibilities or accomplishments
  first—recruiters will skim"*; *"On average, write 3-5 bullet points."*
  (https://career.ucsd.edu/resources/guides/resume.html)
- **Ladders' eye-tracking claim** that recruiters read in an F/E pattern is the usual justification.
  See the ATS/folklore section — it is a vendor study with no disclosed sample.

**Nobody in the literature describes an escalating arc, a closing beat, or a deliberate
weakest-to-strongest ordering inside an entry.** The consensus is flat: strongest first, then
whatever. **#70's closing beat has no external precedent as a closing beat.** Where the sources put a
summarising statement, they put it **first** (§3 below). That is a genuine and load-bearing
divergence, and #72 should decide it knowingly rather than inherit it.

### 2d. What emphatically does *not* exist

Stephen Risavy's *"The Resume Research Literature: Where Have We Been and Where Should We Go Next?"*,
*Journal of Educational and Developmental Psychology* 7(1), 2017, pp. 169–187
(https://www.ccsenet.org/journal/index.php/jedp/article/download/66404/35947) is a comprehensive
synthesis of the empirical résumé literature, deliberately excluding *"publications that involve
merely opinions without supporting research evidence."* Its Table 1 — the accumulated,
research-supported advice — contains **nothing** about bullet frameworks, bullet ordering inside an
entry, narrative arcs, or aggregate statements. The only bullet-level advice it can support is:

> *"be concise yet specific and avoid vague assertions"* · *"use traditional, short, bullet point
> resumes with bolding and action verbs"*

**So: there is no empirical evidence for or against the entry arc. None. In either direction.** That
is a clean result, and it means #72 is deciding on judgement and on two credible practitioner
sources, not against a body of contrary evidence.

---

## Question 3 — the summarising / aggregate bullet

**Recognised, published, and used — but at the top, not the bottom.**

**For it.** Enelow–Kursmark use an aggregate statement in three of their five entry formats, always
as the **lead**:

- Achievement format: *"Turned around a sinking business… drove operational improvements, cemented
  client relationships, improved customer satisfaction, and firmly positioned company to reach
  strategic goal of 100% revenue growth."* (208 chars)
- Career Track format: *"Built a top-tier global organization; recruited and developed a talented
  management team that **led the company from $8M revenue (1998) to 2006 volume of $24M**."*
  (157 chars) — **an aggregate figure spanning the whole tenure**, exactly the species of fact #70
  wants for Amex.
- Functional format: a merged theme sentence with the component numbers indented beneath it.

They also state the general principle when describing the summary section's Category format: the aim
is *"to present **the sum of your credentials rather than dispersing them throughout the resume**."*
That sentence is the closest thing in the literature to a first-principles argument for #70's
aggregate.

**And OPM does the same at the account level:** *"Begin your ECQ statement with a brief summary."*

**Against it.** The counter-argument exists but is **weak-sourced** — the *"one bullet, one idea"*
rule, which is real advice widely given but is blog-level (Indeed, iHire, résumé-writing SEO sites),
with no institutional or empirical backing found. It matters to this repo anyway, because **it is the
same rule as `0027` §6** (*one Bullet, one Claim, one citation*), which is load-bearing for
`check_number_trace`, the Omission view and the Packer's arithmetic. **The external world offers no
help defending §6 and no help demolishing it.** The decision is this project's alone.

**Two constraints the sources do impose on an aggregate.**

1. **It must be verifiable in an interview.** PARWCC's Code of Ethics (https://parwcc.com/code-of-ethics/)
   and the NRWA's (https://www.thenrwa.org/codeofethics) both bind practitioners to accurate,
   evidence-based achievements. #70's design — the agent computes, **the maker judges**, the tier
   stays `estimated`, and it renders under `0022`'s softening tilde — is already stricter than either
   code requires. **No source objects to an estimated aggregate that the candidate can defend.**
2. **Where the sources put a whole-tenure aggregate, they put it where the reader hits it first.**
   Given UCSD's *"recruiters will skim"* and Purdue's *"most relevant first"*, a closing beat is
   betting on the reader reaching line six. **This is the single most contestable thing in #70's
   design, and this survey found nothing that supports it.**

**Recommendation for #72:** the aggregate is well-supported as a *move*; its **position** is not.
Prototype it both ways on the Amex entry before the ADR fixes it as a closing beat.

---

## The repeated-shape question — testing `0027` §2

`0027` §2 asserts, with no external evidence at the time: *"six of those in a row read like a
template rather than like someone who did six different things."* This survey went looking. The
result is **mixed, and mostly against the ADR as written**.

**Against `0027` §2 — the style authorities require the opposite:**

- **Purdue OWL**: *"each bullet must be in parallel form (which means that each item must be
  grammatically formatted the same)"*, and in the professional/technical writing section,
  *"Particularly within entries, make sure that the structure of your phrases is exactly parallel."*
  (https://owl.purdue.edu/owl/subject_specific_writing/professional_technical_writing/parallel_structure.html)
- **Microsoft Writing Style Guide**, *Lists*: *"Make all the items in a list consistent in structure.
  For example, each item should be a noun or a phrase that starts with a verb."*
  (https://learn.microsoft.com/en-us/style-guide/scannable-content/lists)
- **Risavy's evidence-only table**: *"use traditional, short, bullet point resumes with bolding and
  action verbs"* — one shape, repeated, is the research-supported convention.
- **Harvard OCS** lists *"Be consistent in format and content"* under DO.

**For `0027` §2 — but only at the word level, not the sentence level:**

- Harvard's own margin annotation on its sample résumé is *"Use different verbs."*
- Career-centre and blog advice consistently warns against **repeating the opening verb**, never
  against repeating the sentence shape.

**Verdict.** The external world distinguishes two things `0027` §2 runs together. **Repeating the
opener is a recognised fault. Repeating the sentence's grammatical shape is a recognised
virtue** — it is called parallelism, and every style authority consulted mandates it. `0030`'s opener
rule is therefore **well-founded**; `0027` §2's broader *"no fixed shape"* is **this project's own
aesthetic position, held against the style guides, not with them.**

That does not make it wrong. It makes it **unsupported and worth restating honestly** — and it is
worth noticing that `0027` §2 was reasoning from a *lead-with-the-before-state* template that
produced *"this was the situation; did X instead"*, semicolon and all, six times. The style guides
mandate parallel **grammatical form**; they do not mandate a repeated rhetorical gimmick. Those are
separable, and `0027` §2 may only ever have needed to forbid the second.

**One incidental corroboration of the cap.** Microsoft: *"A list should have at least two items but
(if possible) no more than seven items."* UCSD: *"3-5 bullet points."* `0024`'s six sits inside both.

---

## ATS — what is documented, and what is folklore

**Documented, first-party, and narrow.** Every first-party parser document found constrains
**layout**, and **not one** says anything about bullet shape, sentence structure, or wording:

- **Workday**, admin documentation, *Concept: Resume Parsing*: *"Resume parsing results can vary based
  on resume format and order of words. For best results, use resumes that don't have images or
  image-based styles."* Also: it does not auto-fill Languages or Skills.
  (https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/candidates/set-up-prospects-and-candidates/hdc1552497830785.html)
- **Greenhouse**, support documentation, *Unsuccessful resume parse*: failures are attributed to files
  over 2.5MB, placeholder/fake data, and formatting — *"graphics, columned layouts, spaces between
  letters, resumes uploaded as images, complex table structures, incomplete job titles."*
  **No mention of bullet points, sentence structure, or wording.**
  (https://support.greenhouse.io/hc/en-us/articles/200989175-Unsuccessful-resume-parse)

**So the honest ATS finding is a negative one: parsing constrains the Template, not the Bullet.**
This repo's single-column, no-graphics, plain-heading LaTeX template already satisfies every
documented requirement. **#70 and #72 can proceed without an ATS constraint on bullet shape, because
no vendor documents one.**

**Two things widely believed that this survey could not substantiate:**

- **"75% of résumés are rejected by the ATS before a human sees them."** Not traceable to any
  first-party source. The nearest real document is Fuller & Raman, *Hidden Workers: Untapped Talent*,
  Harvard Business School / Accenture, September 2021
  (https://www.hbs.edu/ris/Publication%20Files/hiddenworkers09032021_Fuller_white_paper_33a2047f-41dd-47b1-9a8d-bd08cf3bfa94.pdf).
  It reports that **88% of surveyed employers agreed** qualified high-skilled candidates are filtered
  out because résumés don't match exact job-description criteria. **That is an executive-opinion
  survey about keyword criteria, not a measurement of parser behaviour**, and it says nothing about
  how a bullet should be written.
- **The 7.4-second F-pattern scan.** Ladders' 2018 eye-tracking study
  (https://www.prnewswire.com/news-releases/ladders-updates-popular-recruiter-eye-tracking-study-with-new-key-insights-on-how-job-seekers-can-improve-their-resumes-300744217.html;
  reported at https://www.hrdive.com/news/eye-tracking-study-shows-recruiters-look-at-resumes-for-7-seconds/541582/).
  It is a **vendor study**: the public release discloses no sample size, no recruiter selection, no
  roles screened, no statistical treatment; the full PDF is behind a bot wall. Its recommendations —
  *"bold job titles supported by bulleted lists of accomplishments"*, avoid *"long sentences, multiple
  columns"*, prefer *"short, declarative sentences"* — happen to agree with the style guides, which
  is the only reason to repeat them. **Label it folklore.** It should not be used to justify a closing
  beat's position or a bullet's shape.

---

## What this project should actually take

1. **Do not adopt STAR, CAR, PAR, SOAR, STARL or CARL as a Bullet shape.** Four of them have no
   traceable origin at all; the two that do were designed for spoken answers and page-long narratives.
   None of them has been tested against anything.
2. **Do keep the Entry-level arc — and cite CCAR and Enelow–Kursmark for it, not STAR.** #70's
   *situation → what you did → what it added up to*, with any beat allowed to be absent, is a
   near-exact restatement of what OPM publishes and what Enelow and Kursmark recommend. **OPM's
   annotated examples, where the beats recur and interleave and are never labelled on the page, are
   the strongest external support this map will get** — for the arc, for beats being optional, and
   for the shape being invisible.
3. **Cite the CAR-story-to-bullet relationship as vindication of the existing bank design.** *"Although
   typically too much for a resume, these stories contain nuggets of information that you can pull
   out"* is `0004`/`0014`'s Claim-and-Evidence model, arrived at independently by the profession's
   canon. Nothing in #70 needs to change here; the survey simply confirms the seam is in the right
   place.
4. **Reconsider whether the aggregate is a closing beat.** Every published aggregate is a **lead**.
   Every ordering rule found is **strongest first**. #70 has no external support for putting the sum
   last, and one plausible reason not to (skim behaviour). Prototype both on `american-express`.
5. **Take the thematic-grouping idea seriously for the merge.** Enelow–Kursmark's Functional and
   Project Highlights formats, and OPM's own competency-grouped résumé, all solve *"five instances of
   one theme"* by naming the theme once. That is #70's merge, and it is published practice — which
   means the merge is on **firmer external ground than the closing beat is**.
6. **Split `0027` §2 when it is next touched.** Forbidding the repeated *opener* is supported.
   Forbidding a repeated *grammatical shape* runs against Purdue OWL, the Microsoft Style Guide and
   the empirical convention. Say which one is meant.
7. **Take XYZ's ordering, not its formula.** And record that its own canonical example is 186
   characters — useful ammunition next time raising `CHARS_PER_BULLET` is proposed, in either
   direction.
8. **Drop ATS from the reasoning about bullet shape.** No vendor documents any constraint on it.

---

## What this survey could not answer

- **Whether any of this works.** There is no study — none — comparing STAR/CAR/XYZ-shaped bullets
  against unshaped ones for interview callbacks. Risavy's review, which set out to find exactly this
  kind of evidence, does not list one. Every framework in the survey is asserted, not demonstrated.
- **Where CAR/PAR came from.** Genuinely untraceable. The trail ends at *"BlueSteps (2011)"* via
  Edinburgh, and BlueSteps cites nobody.
- **Whether DDI really coined STAR in 1974.** Only DDI says so, on a marketing page. No 1974
  document, no trademark record, no third-party corroboration was findable.
- **What the certification bodies actually teach.** The **NCRW Study Guide** (NRWA) and the **CPRW**
  materials (PARWCC) are member-only. Their public pages describe *"career storytelling"* and
  *"personal branding"* as competencies but publish no standard. If #72 wants one more credible voice
  on the entry-as-narrative question, **buying the NCRW Study Guide is the cheapest way to get it** —
  it is the only body of knowledge in this space that is written down and not public.
- **Whether a closing beat outperforms a leading one.** No source addresses it. This will have to be
  settled on the maker's read of a real page.
- **Two peer-reviewed papers were paywalled** and are cited from abstracts only: Thoms et al. (1999),
  *Journal of Business and Psychology* 13, 339–356; and Bright & Hutton (2000), *IJSA* 8(2), 41–53.
  Neither, on its abstract, addresses bullet shape.
