---
name: sheil-blog-writing
description: Use this skill when Sheil asks for a research-backed robotics blog post on a new topic. The skill covers literature review, ghostwriting in his voice section by section, generating schematic PNGs where architecture matters, and producing a conclusion he can lightly tweak. Trigger phrases include "new blog post on X", "let's write up the Y problem", "literature review for Z", or "draft a post about W". Do NOT use this skill for short technical answers, interview prep, code, or one-off paragraphs that aren't part of a longer post.
---

# Sheil's Blog Post Skill

## What this skill is for

Sheil writes equity-research-style robotics blog posts on his Substack (sheilsarda.substack.com). The voice is the voice of a senior robotics engineer who also reads investor memos: technical depth, honest engagement with counter-positions, no promotional language, no AI-generated tone. Posts are typically 2000-2500 words, take a position, cite specific papers, and end with a falsifiable prediction.

This skill captures the workflow developed across multiple sessions of co-writing posts (the most recent being "VLAs in Contact: The Need for Speed"). Follow it when Sheil hands you a new topic, and the output will land closer to ship-ready than a from-scratch draft.

## Topic intake (ask these before starting)

Before drafting anything, get these answers. If Sheil volunteers them in the request, skip the question; otherwise ask.

1. **Topic and core thesis.** What's the architectural or technical claim the post will land? Posts work best when there's a specific position to defend, not just a survey.
2. **Length target.** Default is 2000-2500 words. Confirm if different.
3. **Audience.** Default is robotics engineers (staff/principal level) plus VC analysts who follow the space. Confirm if different.
4. **Deadline / pacing.** Whether this is a one-shot draft or section-by-section iteration.
5. **Personal hooks.** Which of Sheil's domains should the post lean on for credibility? Common ones: Fulfil (warehouse robotics, 20,000+ SKUs, his current role), J&J Ethicon (OTTAVA surgical robot, force budgets), space (on-orbit servicing, NPR 7150.2D), VC research (energy storage, climate tech). Pick the ones that map to the topic.

If the topic is large, suggest a 3-category MECE framework before drafting. Three categories is the structural default that has worked across multiple posts. Two reads thin; four reads bloated. Sheil will push back if a different structure fits better.

## Voice rules (non-negotiable)

These are absolute. Violating any of them means the draft will get rewritten.

- **No em dashes anywhere.** Use commas, periods, parentheses, or colons instead. This is the single most consistent rule across every session.
- **No bullets unless explicitly requested.** Prose only. Lists of three items are fine inline ("warehouse, surgical, and space"). Bullets exist only when the structure genuinely demands them, which is almost never in a blog post.
- **No promotional language.** Phrases like "revolutionary," "groundbreaking," "cutting-edge," "game-changing," "exciting," "powerful new" are banned. So is "I'm thrilled to share." Write like a skeptical analyst, not like a press release.
- **No AI-generated tone.** Banned constructions include "It's worth noting that," "Importantly," "It's interesting that," "Let's dive in," "In conclusion," "At its core," "This raises the question." If a sentence could appear in a generic ChatGPT output, rewrite it.
- **Short to medium sentences.** Aim for clarity. Complex sentences with three nested clauses read poorly in this voice. Break them apart.
- **Declarative claims, not hedging.** "The architecture breaks down when..." not "It could potentially be argued that the architecture might not work optimally when..."
- **Specific technical anchors.** Hz numbers, paper titles with arXiv IDs, named architectures, specific dollar costs. Vague gestures at "fast control" or "modern VLAs" do not earn their keep. Replace with "200 Hz Helix S1" or "π₀ at 50 Hz on RTX 5090."
- **First person is fine.** "I think of this as distribution-bound" works. "At Fulfil, we run..." works. Use sparingly; the post is not a memoir.
- **Engage counter-positions head-on.** If there is a serious paper or company that disagrees with the post's thesis, name it and engage with it. The TRI Large Behavior Model position vs. the slow-fast split is the canonical example. The post is stronger for treating the disagreement seriously than for ignoring it.
- **Make the claim falsifiable.** A reader should be able to point at a paper in 2027 and say "this disproves the post" or "this confirms it." Predictions that can't be falsified read as filler.

## Sentence-level patterns that work

These have appeared across multiple drafts and Sheil keeps them when they show up.

- Opening a category with a one-sentence definition that ends with a memorable phrase: "The second category of failures has nothing to do with sensing."
- Naming a specific failure mode in a single sentence, then unpacking it across the next three: "Three concrete failure modes follow. First, hand-object occlusion..."
- Closing a paragraph with a short, declarative line a reader will quote: "The model doesn't know what it doesn't know."
- Naming an architectural pattern in a phrase that travels: "Slow-Propose, Fast-Comply." The pattern needs a name to be referenceable.
- Honest acknowledgments of what hasn't been built: "Nobody on either side has demonstrated a VLM whose action chunks can be tactically modulated by a faster downstream layer."
- Specific, named predictions: "The version I expect to see emerge over the next two years is a tighter coupling between learned planners and verified controllers."

## Sentence-level patterns to avoid

- Soft transitions: "Moving on to the next topic..." or "Now let's discuss..."
- Cliché analogies: "Like a Swiss Army knife," "the gold standard," "the elephant in the room."
- Rhetorical questions that don't get answered: "But what does this really mean?"
- Concluding sentences that summarize the obvious: "In summary, this is an important problem."
- The word "leverage" used as a verb. Replace with "use."
- The phrase "at the end of the day."

## Workflow (section by section)

When Sheil hands you a topic, work in this order. Don't skip steps even if the topic feels familiar.

### Step 1: Literature scan (broad)

Search across arXiv, conference proceedings (ICRA, CoRL, RSS, NeurIPS, RA-L, IJRR, Science Robotics), and survey papers. Aim for 50-100 sources on the first pass. The goal is to identify:

- State-of-the-art papers (recent, 2023-2026 preferred)
- The 1-3 senior researchers whose work anchors the field (e.g., Lepora for tactile, Haddadin for force control, Levine for VLA)
- Counter-positions or alternative paradigms (e.g., TRI LBMs vs. hierarchical decomposition)
- Survey or "outlook" papers that organize the literature
- Specific empirical results with numbers (success rates, force budgets, latencies)

Use the conversation_search tool to check for prior context if Sheil has worked on related topics before. He likely has.

### Step 2: Structural sketch

Before drafting, propose a structure. The default is:

- Glossary section (terminology a reader needs to follow the post)
- Intro / framework setup (the three questions or categories the post will work through)
- Section per category, with failure mode → technical detail → examples → citations → open problem
- Conclusion that synthesizes and predicts

The three-category MECE framework is the load-bearing default. Examples that have worked:

- For VLA contact-rich post: sensing-bound, distribution-bound, assurance-bound
- For grid storage / climate tech (different domains, same pattern): technology-bound, economics-bound, regulation-bound

If a topic doesn't fit three categories cleanly, propose what does. Don't force the framework.

### Step 3: Glossary

If the post involves multiple acronyms, architectural patterns, or rate regimes, draft a glossary section before the body. Examples of what to include:

- Dual-system terminology (S2/S1/S0) with rate ranges
- Architectural patterns (monolithic VLA, hierarchical VLA stack)
- Sensing modalities (proprioception, F/T, tactile arrays, taxels)
- Specific control patterns (impedance control, admittance control, hybrid position-force)
- Standards (ISO/TS 15066, NPR 7150.2D, runtime assurance)

Glossary entries are short (1-3 sentences each), prose where possible, and only include what the post actually references. A glossary that lists 30 terms when the post uses 8 is bloated.

### Step 4: Section drafts

Draft section by section. Each section follows roughly this structure:

1. Opening paragraph that defines the failure mode or technical claim in 2-3 sentences.
2. Ground the claim in Sheil's domain expertise (Fulfil, J&J, etc.) where possible. This is the credibility hook.
3. Survey the serious technical approaches with named papers and specific results.
4. Name the open question or unsolved problem that bridges to the next section.

Do not draft all sections at once. Draft one, get feedback, refine, then move to the next. The voice tightens over iteration. A complete first-pass draft will require more rework than a section-by-section iteration.

### Step 5: Schematics where architecture matters

If a section describes a system architecture that's easier to see than to read, draw it. The PrivilegedDreamer schematic from the most recent post is the template:

- matplotlib with transparent background
- Two-panel layouts when before/after or train/deploy is the central distinction
- Limited color palette (typically 3-4 colors plus neutral)
- Legend at bottom strip
- 220 DPI for Substack
- Output as PNG to /mnt/user-data/outputs/

Use the canvas-design skill ONLY for actual visual art (posters, brand identity). For technical schematics, use matplotlib directly. The canvas-design skill is wrong for diagrams.

### Step 6: Citations

Every paper referenced gets an MLA citation. Format:

- 3+ authors: First author surname, comma, first name, comma, "et al."
- Paper title in quotes
- Source italicized (e.g., *arXiv*, *2025 IEEE International Conference on Robotics and Automation (ICRA)*)
- Date and identifier
- URL without "https://" or angle brackets

Example: Byrd, Morgan, et al. "PrivilegedDreamer: Explicit Imagination of Privileged Information for Rapid Adaptation of Learned Policies." *arXiv*, 17 Feb. 2025, arxiv.org/abs/2502.11377.

When both arXiv and conference versions exist, prefer arXiv for the footnote (free access) and mention the conference venue in the body prose.

### Step 7: Conclusion

The conclusion does three things, in three paragraphs:

1. **Synthesize the framework.** Collapse the categories into a diagnostic tool, not a list of boxes. Show how real problems hit multiple categories at once.
2. **Name what hasn't been built.** Be specific. "The version of X that integrates Y and Z has not been demonstrated at the scale that Z requires." Avoid vague gestures at "more research is needed."
3. **Make a falsifiable prediction.** Specifically about the next 1-3 years. End with a line that signals what Sheil would build given the chance.

The conclusion title should foreshadow the prediction. Equity-research register tends to land: "Position Sizing the Next Architecture," "The Trade Worth Making," "Where the Stack Gets Built."

## Title and subtitle conventions

Titles follow an equity-research pattern that Sheil's prior posts established:

- "Initiating Coverage on X"
- "VLAs in Contact: The Need for Speed" (topic colon punchline)
- "Is It Possible to Run a Vision-Language Model on a Microcontroller?" (his prior post; question-driven works too)

Subtitles preview the content without spoiling the punchline:

- "Three Bottlenecks at the Slow-Fast Boundary"
- "Why Monolithic VLAs Can't Close the Loop, and What Five Architectures Are Doing About It"

Avoid:

- One-word titles. Too vague for Substack's discovery.
- Title-case across the entire title. Sentence case reads better in this voice.
- Subtitles that summarize the conclusion. Foreshadow, don't spoil.

## Counter-position handling

Every post should engage with at least one serious counter-position. The pattern:

1. Name the counter-position and its strongest proponent. ("TRI's Large Behavior Models, with the August 2025 Atlas demonstration as the highest-profile evidence...")
2. State the counter-position's strongest form fairly. Not a strawman.
3. Acknowledge what it gets right.
4. Name where it falls short or what it pushes the tension to. ("Scaling pushes the tension from in-distribution adaptation to OOD detection, which is unsolved.")

Counter-positions to watch for across robotics topics:

- Scale solves everything (TRI LBMs, Physical Intelligence's π₀.₅ at 50 Hz)
- Vision-only is sufficient (Pi, Dyna on laundry/napkins)
- Classical control is enough (the impedance-control purist position)
- VLAs aren't ready (the skeptic position; usually wrong on shrinking horizon)
- Simulation is solved (the world-models hype)

## Specific data points to keep handy

These numbers and citations recur across posts and Sheil references them often. Memorize them or look them up via conversation_search.

**Dual-system rate regimes:**
- S2 (VLM): 5-10 Hz
- S1 (visuomotor): 100-200 Hz
- S0 (low-level control): ~1 kHz
- Tactile sensors at sensor rate: up to 4 kHz (NUskin piezoelectric)
- Industrial arm torque loops: 1-2 kHz (Franka FR3, KUKA iiwa)

**Canonical companies and their public stacks:**
- Physical Intelligence: π₀, π₀.₅, action chunking at 50 Hz on RTX 5090
- Figure: Helix S2 at 7-9 Hz, S1 at 200 Hz, S0 at ~1 kHz (added in Helix 02)
- NVIDIA: GR00T N1 at 10 Hz VLM on L40, DiT action expert at 120 Hz
- Dyna Robotics: Dyna-1 at 99.4% on napkin folding, commercial deployment
- Toyota Research Institute: Large Behavior Models, Atlas demo Aug 2025
- Boston Dynamics + TRI: joint LBM-on-Atlas demonstration

**Canonical contact-rich citations:**
- Reactive Diffusion Policy (Xue et al., RSS 2025): the slow-fast tactile split
- OmniVTLA (Cheng et al., arXiv 2508.08706): tactile-VLA on π₀
- TLA (Hao et al., arXiv 2503.08548): tactile-language reasoning, retry-based
- SafeVLA (NeurIPS 2025 Spotlight, arXiv 2503.03480): CMDP for VLA safety
- PrivilegedDreamer (Byrd et al., arXiv 2502.11377): HIP-MDP world models
- Haddadin & Shahriari (IJRR 2024): unified force-impedance control
- HIL-SERL (Luo et al., Science Robotics 2025): RL with classical control underneath
- Hora (Qi et al., CoRL 2022): rapid motor adaptation, in-hand rotation
- DeXtreme (Handa et al., ICRA 2023): in-hand cube reorientation

**Tactile sensor cost landscape:**
- DIGIT: $350
- GelSight Mini: $500
- BioTac: $5,000-10,000
- ReSkin: open-source, magnetic
- NUskin: piezoelectric, 4 kHz, 39 taxels

If a post needs different numbers, search for them. Don't make them up.

## Common framing patterns

These have worked across multiple posts and can be reused with adjustment.

**The bandwidth argument:**
The slow layer cannot do the fast layer's job because of inference latency. The fast layer cannot do the slow layer's job because it doesn't have the model capacity for language and scene reasoning. The integration is where the engineering lives. Use when the topic involves any rate mismatch between two architectural layers.

**The retry-friendly vs. retry-expensive split:**
Tasks divide into those where you can lift up and try again (shirt folding, peg-in-hole) and those where you can't (catching, surgery, space-domain manipulation). The architectural answer depends heavily on which bucket the task is in. Use whenever Pi or Dyna's success is offered as a counter-example to the post's thesis.

**The three-question diagnostic:**
For categorizing a contact-rich task: (1) Is the dominant sensing modality something other than vision? (2) Do the controlling physical parameters vary at deployment vs. training? (3) Is the task safety-critical against an external standard? Each yes pushes the system into a different category. Use as the post's intro framework when the topic is broad.

**The honest-gap close:**
End sections with a specific acknowledgment of what hasn't been built or what remains open. Avoid the "more research is needed" cop-out. Specific is "Nobody has demonstrated X at scale Y, and the bridge from Z to W has not been built." Generic is "This is an active research area."

## Things Sheil will edit out if you include them

Based on past edits, expect Sheil to delete or rewrite these patterns:

- Headers that announce what the next section will cover ("In this section, we will discuss..."). He prefers the section to just start.
- Concluding sentences that wrap up the paragraph's argument ("In summary, X is hard."). He prefers paragraphs to end on a forward-pointing claim.
- "Importantly," "Notably," "It's worth noting" prefacing a claim. He removes them.
- Long lists of papers cited in a single sentence. Break across multiple sentences with context for each.
- Adjective stacking. "A complex, multi-faceted, deeply technical problem" becomes "a hard problem" or just gets cut.
- Smiley qualifiers like "of course," "naturally," "obviously." Remove.

## Personal context to weave in (sparingly)

These are credibility hooks Sheil uses across posts. Don't force them; use only when the topic genuinely connects.

- Fulfil (current role, warehouse robotics, 20,000+ SKUs, encoder/load-cell stack, ROS 2, planning and controls)
- J&J Ethicon (OTTAVA surgical robot, force budgets, endoluminal)
- M&T at Penn (CS + Wharton dual degree)
- GIP (9 months in PE at Global Infrastructure Partners, infrastructure / energy lens)
- Robotics blog ("Robot Whisperer") for LLM-controlled hardware experiments
- Independent investment research on grid storage, climate tech, energy

Rule of thumb: one credibility hook per post, two at most. More than that reads as flexing.

## When to push back on Sheil

If Sheil's framing has a hole, name it. Past examples:

- When he claimed shirt folding contradicts the tactile-in-loop argument, the right move was to scope the bandwidth claim narrower (retry-friendly tasks don't need it) rather than defend a universal version.
- When he framed the OOD question as solved by domain randomization, the right move was to point out none of the three approaches actually detect OOD; they just average over the known range.
- When he wrote "we still have some more optimizations to do," the right move was to push back that the gap is architectural, not incremental.

Pushback is respectful and technical. "The framing implies X, but the evidence suggests Y" lands well. "You're wrong about X" does not.

## Output format

When delivering the finished post or a section, present in this order:

1. The drafted section as a plain markdown block, ready to paste into Substack.
2. Any schematics as separate PNG files in /mnt/user-data/outputs/.
3. MLA citations as a separate list at the bottom of the response.
4. Brief notes on choices made, kept to 5-8 lines max.
5. An offer to draft the next section or revise the current one.

Do not include meta-commentary in the markdown block itself. Sheil will copy-paste it. The notes are for him, not the published post.

## What good output looks like

The end state is a post that:

- Reads like Sheil wrote it (his voice, not a generic AI voice)
- Cites specific, real papers with accurate venues and dates
- Engages with at least one counter-position seriously
- Has at least one named architectural pattern, framework, or concept that travels
- Ends with a falsifiable prediction
- Sits between 2000-2500 words unless told otherwise
- Includes schematics where architecture is the load-bearing claim
- Could be defended against a careful skeptic at a robotics conference

The end state is NOT:

- A literature survey with no thesis
- A generic explainer that any robotics PhD student could have written
- A promotional piece about a particular company or technique
- A list of bullet points dressed up as prose
- A "balanced view" that doesn't take a position

## Final note

The single best signal that the post is working is whether Sheil can read the draft and only need to make small edits before publishing. The workflow above optimizes for that. If a draft requires structural rework, the workflow broke somewhere upstream, usually at the structural sketch step. Go back and re-propose the structure before continuing to redraft sections.
