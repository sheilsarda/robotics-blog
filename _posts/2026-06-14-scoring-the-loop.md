---
title: "Scoring the loop: a four-axis scorecard for robot foundation models and the markets they fit"
short_title: "Scoring the loop"
date: 2026-06-14
slug: scoring-the-loop
description: "A MECE framework for grading robot foundation models on data, architecture, loop, and capability, a filled-in scorecard across seven labs, and the end-markets each profile actually unlocks."
---

## Glossary

**Vision-language-action model (VLA).** A single network mapping camera images and a language instruction to robot actions. RT-2 and OpenVLA are the reference points. What decides deployability is what runs underneath to turn the output into motion at control rate.

**Dual-system stack (S2/S1/S0).** A decomposition by rate. S2 is a slow vision-language model reasoning about scene and task, 5 to 10 Hz. S1 is a fast visuomotor policy, 100 to 200 Hz. S0 is low-level control, around 1 kHz. Figure's Helix runs S2 at 7 to 9 Hz and S1 at 200 Hz, and Helix 02 adds S0 at 1 kHz.

**Action chunking and flow matching.** Action chunking predicts a short horizon of future actions in one inference pass, then executes the chunk before predicting the next. Flow matching is a continuous-action generation method, a close cousin of diffusion, that emits those chunks without discretizing the action space. Physical Intelligence's action expert pairs the two at up to 50 Hz.

**Real-time chunking (RTC).** Physical Intelligence's inference scheme that generates the next chunk while the current one is still executing, so the loop does not stall on the model. It holds up under inference delays above 300 ms.

**Inverse dynamics model (IDM).** The component that reads a predicted state transition, two frames or a short clip, and outputs the action that causes it. The bridge from predicted pixels to motor commands.

**World Action Model (WAM).** A model that predicts future video and the actions that produce it jointly, inside one network, rather than bolting an action decoder onto a separate video model. DreamZero is the reference implementation; Rhoda's two-box Direct Video-Action is the split-network version of the same thesis.

**Evidence grade.** Not a property of the robot, a property of the public record. Whether a claim is backed by open weights and a peer-reviewed eval, a blog with numbers, an uncut demo, or nothing.

![Rate stack: where each company closes the loop]({{ site.baseurl }}/assets/posts/model-scorecards/option3/rate-stack-ladder.png)


## Why the old scorecard was the wrong shape

I graded these companies once before, on three lenses: loop legibility, action representation, and data economics. The framework worked as a narrative, but it was not MECE, and the seam shows under load. Loop legibility is not a peer of the other two. It overlaps both, because legibility is just the question of whether the data economics and the action representation are disclosed at all. You cannot put "is it disclosed" on the same axis as "what is it" without double-counting.

The fix is to separate substance from evidence. A robot foundation model is a closed loop: data trains an artifact, the artifact runs at some rate, and that produces outcomes. Every technical metric that matters lives in exactly one stage of that pipeline, which is what makes the spine mutually exclusive and collectively exhaustive. Four axes: data economics, policy architecture, real-time loop, demonstrated capability. Then one dimension cuts orthogonally across all four, the evidence grade, which is where the old "legibility" lens actually belonged. You score what a company does on the four axes, and how much you can trust each claim separately.

The payoff is the third question, the one the first post only gestured at. Once the four axes are clean, each one maps onto a property of the task, and the metric profile of a company tells you which end-market it is actually built for. That mapping is the back half of this post.

## The metrics that matter

The first axis is **data economics**, and it has three measurable parts: the pretraining substrate and its scale, the marginal cost of the next task in hours of robot data, and whether that data has to carry action labels. The spread across the field is enormous. Generalist's GEN-0 pretrained on more than 270,000 hours of manipulation data growing about 10,000 hours a week, and GEN-1 adapts a new task on one hour of robot data. Rhoda trains its video model on hundreds of millions of unlabeled internet videos and post-trains a task on 10 to 20 hours, its decanting policy on 11 and container breakdown on 17, with an inverse dynamics model that can learn from random, non-expert motion. NVIDIA's DreamZero (arXiv 2602.15922) is sharper still: 30 minutes of play data for a brand new robot, 10 to 20 minutes of video-only demonstration for an unseen task, no action labels at all. The label-requirement sub-metric is the one that separates the video-prediction camp from everyone paying for teleoperation.

The second axis is **policy architecture and action representation**, which decides where in the loop the model actually emits motion. Three sub-questions: how the stack decomposes by rate, what the action representation is, and how long a horizon each inference covers. Physical Intelligence's π0 (arXiv 2410.24164) pairs a 3B vision-language backbone with a flow-matching action expert producing continuous chunks at up to 50 Hz, and π0.5 (arXiv 2504.16054) adds a two-level pass that writes the next subtask in language before the expert produces commands. DreamZero collapses the two boxes of Rhoda's Direct Video-Action into one 14B autoregressive diffusion transformer with a joint video-and-action flow-matching objective, so the inverse dynamics fall out of the same network that predicts frames. Toyota Research Institute's Large Behavior Models (arXiv 2507.05331) sit in between, a multitask diffusion transformer predicting 1.6-second chunks.

![π0 VLM plus flow-matching action expert (Black et al.)]({{ site.baseurl }}/assets/posts/model-scorecards/option3/pi0-architecture-paper.png)


The third axis is **the real-time loop**, and it is the axis that separates a demo from a deployment. At Fulfil we run a planning and controls stack over more than 20,000 SKUs, and the question that decides whether a model ships is never the success rate in the highlight reel. It is what happens to the loop when inference is slow, when the network adds latency, and when the action the model proposed is half-executed and the world has already moved. Three sub-metrics answer it: the control-rate stack in Hz, the inference latency and its robustness to delay, and the hardware class the loop runs on. This is where Physical Intelligence is alone in disclosing the whole budget. Real-Time Execution of Action Chunking Flow Policies (arXiv 2506.07339, NeurIPS 2025) generates the next chunk while the current one executes, holds up under delays above 300 ms at roughly 97 ms of model latency, and the weights are released through openpi. DreamZero quantifies the opposite end: it reaches 7 Hz only on two GB200s, after a 38x optimization pass that cut latency from 5.7 seconds to 150 ms per chunk, and the paper concedes a VLA clears 20 Hz on a single consumer GPU. The hardware-class sub-metric is the gate the whole field is stuck behind.

![Real-time execution of action chunking flow policies (Black et al., NeurIPS 2025)]({{ site.baseurl }}/assets/posts/model-scorecards/option2/rtc-paper.png)


The fourth axis is **demonstrated capability**, and the sub-metrics matter more than the headline number: in-distribution success on a shared benchmark rather than a self-chosen task, out-of-distribution generalization to unseen objects and tasks, cross-embodiment transfer, and autonomy over time. The distinction between a shared benchmark and a self-chosen one is the whole game. Dyna's DYNA-1 folding napkins at 99.4% over a 24-hour autonomous run is the strongest autonomy signal in the field, and it is also a self-run demo on a task the company picked. DreamZero is the opposite: 62.2% average task progress against 27.4% for the best pretrained VLA baseline, 39.5% on tasks entirely absent from training where from-scratch VLAs score under one percent, benchmarked head to head against π0.5 and GR00T N1.6 on shared AgiBot and DROID tasks, with a robot-to-robot and a human-to-robot transfer posted on the same eval. One is a robustness claim you take on faith, the other is a generalization claim you can check.

![DreamZero World Action Model closed-loop architecture (Ye et al.)]({{ site.baseurl }}/assets/posts/model-scorecards/option3/dreamzero-wam-paper.png)


Then the orthogonal dimension. **Evidence grade** runs from open weights with a peer-reviewed eval, down through a blog with numbers, down through an uncut demo, down to nothing disclosed. It is not a fifth axis, it is a confidence interval on the other four. A company can post a strong value on data economics and a blank on the real-time loop, and the evidence grade is what stops you from averaging the two into a number that means nothing.

## The scorecard

Each cell carries the disclosed value and, in parentheses, a grade for that axis. The final column is the evidence grade across the row, the orthogonal read.

| Company | A. Data economics | B. Architecture | C. Real-time loop | D. Capability | Evidence |
|---|---|---|---|---|---|
| **Physical Intelligence** | teleop corpus, multitask pretrain cuts per-task data; marginal cost moderate (B) | dual-level VLA, flow-matched chunks, 50 Hz, knowledge insulation (A) | RTC 97 ms, holds >300 ms delay, 50 Hz on RTX 5090 (A) | dexterous laundry/open-world, π0.5 is the shared-benchmark baseline (A) | **A** open weights (openpi), arXiv |
| **NVIDIA GEAR (DreamZero)** | 500 hrs teleop/22 envs; new robot on 30 min, unseen task on 10-20 min video-only, no labels (A) | WAM, single DiT, joint video-action flow matching, 14B on Wan2.1 (A) | 7 Hz on 2x GB200 after 38x; edge is future work (C) | 62.2% vs 27.4%; 39.5% vs <1% unseen; cross-embodiment, shared AgiBot/DROID (A) | **A** open weights, code, eval sets |
| **Generalist AI** | GEN-0 270k hrs (+10k/wk), base = wearable gloves, GEN-1 1 hr/task, scaling laws (A) | Harmonic Reasoning, paged attention, not specified to Hz (C) | control loop named, not specified, hardware undisclosed (D) | GEN-1 99% vs prior 64%, ~3x speed, self-reported not shared (C) | **C** blog with numbers |
| **Toyota Research Institute** | multitask pretrain cuts per-task data ~80% (B) | multitask diffusion transformer, 1.6 s chunks (A) | dexterous without exotic machinery; rate not the focus (B) | careful examination, rigorous multitask eval methodology (A) | **A-** arXiv, methodical study |
| **Rhoda AI** | ~10^8 internet videos, IDM on random motion, 10-20 hr/task (A, conceptual) | Direct Video-Action, causal video model + separate IDM (B) | on-robot rate and hardware not disclosed; 10 Hz is an analyst estimate (D) | uncut demos (decanting, breakdown, returns, sort, pack), no shared table (D) | **C-** research post + demos, blank on loop |
| **Dyna Robotics** | scalable reward model self-generates training data; marginal cost undisclosed (C) | no rate stack, no action rep, no model card (F) | undisclosed (F) | DYNA-1 99.4% over 24 h autonomous, self-chosen task (B on autonomy) | **D** one number + demo |
| **Skild AI** | human video + large-scale sim, no marginal numbers (D) | omni-bodied in-context, no rate stack or action rep (F) | undisclosed (F) | no benchmark table, no model card (F) | **F** undisclosed, ~$14B valuation |

Two reads come off the same matrix. The substance read is which company posts the strongest disclosed value on a given axis: Generalist on data, Physical Intelligence on the loop, DreamZero on capability. The evidence read is how much of the row you can underwrite: Physical Intelligence and NVIDIA at the top, Skild at the bottom with the highest valuation in the table and the least disclosure. A company that scores well on substance and badly on evidence, like Rhoda, is not a weak company. It is an unauditable one, which is a different and more honest thing to say.

The interesting pattern is that no single company sweeps. The two open labs, Physical Intelligence and NVIDIA, split the field on the deepest axes: PI owns the real-time loop, NVIDIA owns capability and data economics, and they are attacking from opposite paradigms. That split is not noise. It is the structure of the end-market question.

## The two clocks

The scorecard ranks companies axis by axis, but it hides the tradeoff they are all making. Two of the four axes are costs, and they are the costs that decide whether a company can scale. Reframe each as a clock. The learning clock is how long it takes to onboard a new task, measured in hours of robot data. The control clock is how long each action takes to compute, measured in milliseconds and in the silicon required to hit control rate. The two are orthogonal. A company's data cost does not predict its inference cost, which is exactly what makes them a clean 2x2.

```
                       CHEAP TO TEACH               EXPENSIVE TO TEACH
                    (low data cost / new task)    (pays for robot data)
                  +-----------------------------+-----------------------------+
  EXPENSIVE       |                             |                             |
  TO RUN          |   X  DreamZero              |                             |
  (datacenter,    |   X  Rhoda *                |        (loser corner)       |
   ~2x GB200,     |                             |           empty             |
   7 Hz)          |   [ video-prediction camp ] |                             |
                  |                             |                             |
                  +-------- X Generalist * -----+-----------------------------+
                  |                             |                             |
  CHEAP           |   ★ THE FRONTIER            |   X  Physical Intelligence  |
  TO RUN          |   cheap to teach AND run    |   X  TRI                    |
  (edge / 1 GPU,  |   NO CONFIRMED OCCUPANT     |                             |
   ~50 Hz)        |                             |   [ flow-matching VLA camp ]|
                  |                             |                             |
                  +------------ X Dyna * -------+-----------------------------+

  *  one clock undisclosed; placement inferred, sits on the border not the corner
  Skild AI: off-map. Neither clock disclosed.
```

![The two clocks: where each robot foundation model pays its cost]({{ site.baseurl }}/assets/posts/model-scorecards/option3/two-clocks.png)


The field splits across the anti-diagonal, and the split is the whole story. The video-prediction camp sits top-left, cheap to teach and expensive to run. DreamZero onboards a new robot on 30 minutes of play and an unseen task on 10 to 20 minutes of video, then pays for it at 7 Hz on two GB200s. Rhoda makes the same trade on 10 to 20 hours per task off an internet-video prior, though its run clock is an outside analyst's 10 Hz estimate rather than a disclosed number, so it sits on the border with a dashed mark. The flow-matching camp sits bottom-right, the mirror image. Physical Intelligence and TRI pay for teleoperation up front, then run the loop cheap, 50 Hz on a single RTX 5090 with RTC holding past 300 ms of delay.

The placements that cannot be pinned are the revealing ones. Generalist onboards a task on one hour of robot data, which fixes it in the cheap-to-teach column, but it never specifies the loop to a control rate, so its control clock is unknown and it floats on the left border. Dyna runs deployed on edge hardware around the clock, which fixes its control clock cheap, but it has shown only one task, so the marginal cost of the next one is undisclosed and it floats on the bottom border. Skild discloses neither clock, so it cannot be placed at all, off-map at a $14B valuation.

The corner that decides the field is empty. Nobody has confirmed a policy that is both cheap to teach and cheap to run. That empty frontier is the prediction the rest of this post builds toward. The company that reaches the bottom-left corner wins, and slow-propose, fast-comply is the explicit attempt to get there by stacking the top-left camp's data-cheap prior over the bottom-right camp's run-cheap loop.

![DreamZero inference latency optimization (Ye et al.)]({{ site.baseurl }}/assets/posts/model-scorecards/option2/dreamzero-latency-paper.png)


## The tasks each profile unlocks

The four axes are not equally important for every task, and that is the point. Two of them map directly onto two properties of manipulation work, which lets the scorecard predict fit rather than just rank companies.

The real-time loop, axis C, governs **cycle dynamics**: whether a task is quasi-static, where the world holds still long enough for a slow loop to catch up, or dynamic and high-speed, where success is decided by reactivity at control rate. Data economics, axis A, governs **task diversity**: whether the work is low-mix and repetitive, the same motion all shift, or high-mix and long-tail, a new object or task every few minutes. Contact-richness and tight tolerance overlay both as a difficulty multiplier, stressing architecture and loop together. The 2x2 is the load-bearing map.

| | Low-mix, repetitive | High-mix, long-tail |
|---|---|---|
| **Quasi-static** | 24/7 single-station (Dyna napkin fold, 99.4%/24 h) | warehouse pick, sort, returns (PI, Generalist, Rhoda's actual demos) |
| **Dynamic, high-speed** | high-rate packaging lines | fast assembly, dynamic handling, the contested expansion case |

The mapping rule is simple: a company's metric profile lights up the quadrant its strongest axis dominates. Strong data economics (cheap marginal task, no action labels) lights up the right column, the high-mix long-tail work where the cost of the next task is the binding constraint. This is exactly where Rhoda and DreamZero's data efficiency pays, and it is the column the warehouse market mostly lives in. Strong real-time loop (low latency, cheap hardware) lights up the bottom row, the dynamic high-speed work, which is precisely where DreamZero's 7-Hz-on-two-GB200s economics fail and where Physical Intelligence's RTC still wins. Strong cross-embodiment lights up multi-embodiment fleets and humanoids. Strong long-run autonomy lights up the top-left single-station cell, which is the cell Dyna already owns.

The honest read of the market is that the top-right cell, high-mix quasi-static warehousing, is where Physical Intelligence, Dyna, Generalist, and Rhoda are all converging, because it is large, real, and tolerant of a slow loop. It is contested, not unlocked, by any one approach. The expansion case that would actually differentiate the video-prediction camp is the bottom row, high-speed contact-rich work, and that is exactly the row where video generation's inference cost is the binding constraint. The scorecard's axis C is the gate on the most valuable unclaimed quadrant.

![Toyota Research Institute Large Behavior Models (TRI et al.)]({{ site.baseurl }}/assets/posts/model-scorecards/option2/tri-lbm-paper.png)


## Position sizing the next axis

Collapse the scorecard into one diagnostic and the picture is clean. The four axes are not won by one company, and the evidence grade tells you which wins to trust. Physical Intelligence owns the loop with the only auditable latency budget in the field. NVIDIA's DreamZero owns capability and data economics with open weights, and proves the video-prediction thesis is real on shared benchmarks. Generalist owns the data story but blanks the loop. Dyna owns autonomy on a self-chosen task. Skild owns a valuation and nothing else. The advantage that gets won next is on the axis where the two open leaders disagree, and the disagreement is not about whether video prediction generalizes. DreamZero settled that. It is about whether video prediction can close the loop on hardware you could bolt to a robot.

That makes the prediction a single gate, and it is falsifiable. The pick today is Physical Intelligence, because the most valuable unclaimed quadrant is the bottom row, and the bottom row is decided by axis C, where PI leads and the video camp runs at 7 Hz on two datacenter GPUs. The pick flips when a video-prediction policy holds 10 Hz or better on a single consumer-class GPU rather than a pair of GB200s. Everything else the video camp needed, the shared-benchmark table, the cross-embodiment transfer, the data efficiency, it now has, ahead of schedule. The one thing it does not have is the deployment rate on deployable hardware, and the team that built DreamZero files edge deployment under future work.

The bet I would actually make still sits between the two camps, and the scorecard is the argument for it. Put the data-economics winner on top, a video-prediction model proposing at low rate from the internet-video prior, and the real-time-loop winner underneath, a flow-matching controller closing the loop at 200 Hz. Slow-propose, fast-comply. NVIDIA labels DreamZero the other way, a System 1 it hopes to shrink onto an edge device, but its own economics, two GB200s for 7 Hz, are the strongest case I have seen that video generation belongs in the slow half of the stack, not the fast loop where the robot lives. The framework does not just grade the companies. It tells you which axis each one should be assigned to in the stack that finally ships.

![Slow-propose, fast-comply hybrid control stack]({{ site.baseurl }}/assets/posts/model-scorecards/option3/slow-propose-fast-comply.png)


## References

Black, Kevin, et al. "π0: A Vision-Language-Action Flow Model for General Robot Control." *arXiv*, 31 Oct. 2024, arxiv.org/abs/2410.24164.

Black, Kevin, et al. "Real-Time Execution of Action Chunking Flow Policies." *arXiv*, 7 June 2025, arxiv.org/abs/2506.07339.

Brohan, Anthony, et al. "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control." *arXiv*, 28 July 2023, arxiv.org/abs/2307.15818.

Cheang, Chi-Lam, et al. "GR-2: A Generative Video-Language-Action Model with Web-Scale Knowledge for Robot Manipulation." *arXiv*, 8 Oct. 2024, arxiv.org/abs/2410.06158.

Dyna Robotics. "Dyna Robotics Unveils DYNA-1." *PR Newswire*, 30 Apr. 2025, prnewswire.com/news-releases/dyna-robotics-unveils-dyna-1-the-first-commercial-ready-robot-foundation-model-offering-fully-autonomous-round-the-clock-dexterity-302441437.html.

Figure AI. "Helix: A Vision-Language-Action Model for Generalist Humanoid Control." *Figure*, 20 Feb. 2025, figure.ai/news/helix.

Generalist AI. "GEN-1: Scaling Embodied Foundation Models to Mastery." *Generalist*, 2 Apr. 2026, generalistai.com/blog/apr-02-2026-GEN-1.

Kim, Moo Jin, et al. "OpenVLA: An Open-Source Vision-Language-Action Model." *arXiv*, 13 June 2024, arxiv.org/abs/2406.09246.

NVIDIA. "GR00T N1: An Open Foundation Model for Generalist Humanoid Robots." *arXiv*, 18 Mar. 2025, arxiv.org/abs/2503.14734.

Physical Intelligence, et al. "π0.5: a Vision-Language-Action Model with Open-World Generalization." *arXiv*, 22 Apr. 2025, arxiv.org/abs/2504.16054.

Physical Intelligence, et al. "Knowledge Insulating Vision-Language-Action Models." *arXiv*, May 2025, arxiv.org/abs/2505.23705.

Rhoda AI. "Causal Video Models Are Data-Efficient Robot Policy Learners." *Rhoda AI*, Mar. 2026, rhoda.ai/research.

Toyota Research Institute. "A Careful Examination of Large Behavior Models for Multitask Dexterous Manipulation." *arXiv*, 7 July 2025, arxiv.org/abs/2507.05331.

Ye, Seonghyeon, et al. "World Action Models are Zero-shot Policies." *arXiv*, 17 Feb. 2026, arxiv.org/abs/2602.15922.

## Figures

Black, Kevin, et al. "π0." *arXiv*, 31 Oct. 2024, arxiv.org/abs/2410.24164. Fig. 3 reproduced from arXiv PDF page 4 for commentary.

Black, Kevin, et al. "Real-Time Execution of Action Chunking Flow Policies." *arXiv*, 7 June 2025, arxiv.org/abs/2506.07339. Figure 1 reproduced from arXiv PDF page 1 for commentary. NeurIPS 2025.

Sarda, Sheil. "Rate Stack Ladder for Robot Foundation Models." *Diagram*, 2 June 2026. Robotics blog illustration.

Sarda, Sheil. "Slow-Propose, Fast-Comply Hybrid Stack." *Diagram*, 2 June 2026. Robotics blog illustration.

Toyota Research Institute. "A Careful Examination of Large Behavior Models." *arXiv*, 7 July 2025, arxiv.org/abs/2507.05331. Figure 9 reproduced from arXiv PDF page 12 for commentary.

Ye, Seonghyeon, et al. "World Action Models are Zero-shot Policies." *arXiv*, 17 Feb. 2026, arxiv.org/abs/2602.15922. Figure 4 and the latency table reproduced from arXiv PDF pages 6 and 8 for commentary.
