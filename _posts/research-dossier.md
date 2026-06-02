# Five Robot-Foundation-Model Companies, One Pick: Why Physical Intelligence's Disclosed Stack Wins, and What Rhoda's Video-Prediction Bet Really Buys

*Research dossier supporting the Substack post "Reading the loop." Compiled May 31, 2026. Primary sources prioritized over press. Figures current to the compile date.*

## TL;DR

- **Physical Intelligence (Pi) is the winner on full-solution system-design credibility.** It is the only one of the five with arXiv papers, model cards, open weights, and exact rate/latency numbers for a coherent hierarchical VLA: flow-matching action chunking up to 50 Hz, a high-level VLM that emits the next subtask in language, and a real-time-chunking inference scheme (NeurIPS 2025) robust to inference delays above 300 ms. Dyna and Generalist publish credible deployment numbers but thinner architecture. Skild and (so far) Rhoda publish mostly demos, valuation, and, in Rhoda's case, one substantive research blog with no Hz or hardware numbers.
- **Rhoda is real and identified.** Rhoda AI (Palo Alto; CEO Jagdeep Singh, ex-QuantumScape) came out of stealth March 10, 2026 with $450M at a reported $1.7B valuation. It frames control as "Direct Video-Action" (DVA): pre-train a causal video model on internet video, predict future frames, and invert them to actions with a separate inverse-dynamics model in a closed loop. Differentiated and intellectually honest in its research post, but it discloses no control-loop Hz, no inference hardware, and no success-rate table.
- **Verdict on video-prediction-as-control along the three vectors.** Generalizability: plausibly better than action-chunking VLAs for cross-task transfer because the pre-training objective absorbs internet video, but unproven beyond curated demos and no clear cross-embodiment win. Data collection: genuinely advantaged, since passive video needs no action labels and Rhoda claims 10 to 20 hr of robot data per task vs. the teleop-heavy pipelines of VLAs. TAM: today the reachable tasks (folding, kitting, decanting, packing) are the same high-mix manipulation niches every player is chasing, and video-gen inference cost is the gating risk for the high-speed, high-Hz tasks that would expand TAM.

## Key findings

1. **Disclosure quality is the real differentiator.** Physical Intelligence and the academic/world-model literature publish exact rate regimes, arXiv IDs, and benchmark tables. Dyna and Generalist publish strong, specific deployment numbers (99.4% over 24h; 99% on six named tasks) but keep architecture mostly closed. Skild publishes valuation and "omni-bodied" marketing but essentially no control-loop detail. Rhoda published one substantive research blog (good) but with zero rate/hardware/success-rate numbers (a red flag for an equity thesis).

2. **The canonical dual-system rate stack is now well-anchored.** Figure's Helix: System 2 VLM at 7 to 9 Hz, System 1 visuomotor at 200 Hz; Helix 02 adds System 0 at 1 kHz for whole-body control. NVIDIA GR00T N1 uses the same System-2/System-1 split (VLM plus diffusion transformer). Physical Intelligence's π0/π0.5 instead run a single VLA with flow-matching action chunking up to 50 Hz, with the high-level subtask in language produced by the same model.

3. **Rhoda's DVA is a clean instantiation of a decade-old idea (UniPi/AVDC/GR-2) with two genuine novelties:** training a causal video model from scratch (not distilled from a bidirectional model) and doing full video denoising during real-time closed-loop control, plus "Context Amortization" training and "Leapfrog Inference" to hide latency. The economic claim, roughly 10 to 20 hr robot data per task, is its sharpest selling point.

4. **The strongest counter-position to the video thesis comes from Pi and TRI:** action chunking plus flow matching is cheaper at inference and already hits dexterous, high-frequency tasks; TRI's Large Behavior Models show diffusion-policy scaling works with far less exotic machinery. Video generation is repeatedly characterized in the literature as computationally expensive and slow at inference, the exact risk that could cap Rhoda's reachable TAM.

## Company teardowns

### 1. Physical Intelligence (Pi) — the most transparent full stack
Founded 2024 (Chelsea Finn, Sergey Levine, Karol Hausman, Brian Ichter, Lachy Groom, et al.), backed by Jeff Bezos, Khosla, OpenAI, Sequoia, Thrive, Lux, Redpoint, Bond, CapitalG.

Control loop and decomposition: π0 (arXiv 2410.24164, Oct 2024) is a VLA built on a 3B PaliGemma VLM backbone plus a separate ~300M-parameter action expert producing continuous actions via flow matching, enabling action chunking up to 50 Hz for dexterous tasks like laundry folding. π0.5 (arXiv 2504.16054, Apr 2025) adds open-world generalization via a two-level inference procedure: the model first emits a high-level subtask in language, then its flow-matching action expert emits the motor commands. Knowledge Insulation (arXiv 2505.23705) trains the VLM backbone on discrete FAST tokens while the action expert learns continuous flow-matching, with gradients blocked from the expert to the backbone.

Action representation: flow-matching continuous action chunks (horizon ~50); FAST is a DCT-based autoregressive action tokenizer used for pretraining and the π0-FAST variant.

Inference realism: "Real-Time Execution of Action Chunking Flow Policies" (RTC; arXiv 2506.07339, NeurIPS 2025) is the standout: an inference-time freeze-and-inpaint scheme that generates the next chunk while executing the current one, robust to inference delays in excess of 300 ms (more than 30% of the prediction horizon) and about 20% faster than synchronous inference; model latency ~97 ms with 10 to 20 ms added for remote inference, 20 ms controller timestep. openpi releases π0, π0-FAST, and π0.5 weights pretrained on 10k+ hours of robot data.

Benchmarks and demos: laundry folding from a hamper, box assembly, bussing tables, packing eggs and to-go boxes; π0.5 cleans entirely unseen kitchens and bedrooms (10 to 15 min multi-stage behaviors). π*0.6 (arXiv 2511.14759, Nov 2025) introduces RECAP (RL with experience and corrections); on the hardest tasks it more than doubles throughput and roughly halves failure rate (~13 h continuous deployment).

Verdict: the only company here with a fully legible, peer-reviewable, reproducible stack from VLM to action expert to real-time controller.

### 2. Dyna Robotics — credible deployment, thin architecture
Founded 2024 to 2025 by Lindon Gao and York Yang (sold Caper AI for $350M) and ex-DeepMind scientist Jason Ma. Seed $23.5M (Mar 2025, CRV/First Round); Series A $120M (Sep 2025) at a reported >$600M post.

Disclosed: DYNA-1 (Apr 2025) is a single-weight, general-purpose foundation model running a pair of stationary arms. Headline result: napkin folding, >99.4% success without human intervention over 24h at ~60% of human throughput, 700 to 900+ napkins; later HITEC 2025 showcase 99.9% over three 8h shifts (one towel dropped). Key claimed innovation is a scalable reward model enabling autonomous exploration, intentional error recovery, and auto-generation of training data.

Gaps: no public arXiv paper, no model card with control-loop Hz, no action-representation disclosure. High on demonstrated commercial robustness, low on system-design transparency.

### 3. Rhoda AI — identity confirmed; differentiated but under-disclosed
Identity: Rhoda AI (Palo Alto), out of stealth March 10, 2026 with $450M at a reported $1.7B valuation (led by Premji Invest; plus Khosla, Temasek, Mayfield, Capricorn, Leitmotif, Matter, Prelude, Xora, John Doerr). Founders: CEO Jagdeep Singh (founder/CEO of QuantumScape and Infinera), CSO Eric Ryan Chan (ex-World Labs, Stanford generative-model researcher), and Stanford professor Gordon Wetzstein (Computational Imaging Lab). Note: outlets disagree on the round label; Rhoda's own Business Wire release calls it a "$450 million Series A," while Humanoids Daily reports a "Series B." Treat Rhoda's primary release ("Series A") as authoritative and flag the discrepancy.

The approach (from Rhoda's research blog, "Causal Video Models Are Data-Efficient Robot Policy Learners," Mar 2026): a Direct Video-Action (DVA) model. Pre-train a causal video model from scratch on hundreds of millions of internet videos (causal next-frame generation). Conditioned on a long video history plus proprioception and language, predict short-horizon future frames; a separate inverse-dynamics model translates predicted frames into end-effector motion; execute, re-observe, repeat in a streaming closed loop. Two stated novelties: first to pre-train a causal video model from scratch for this, and first to do full video denoising during real-time closed-loop control. Supporting techniques: Context Amortization (predict future at every position in a long noise-free context) and Leapfrog Inference (predict far enough ahead to cover the next inference's latency; KV-caching reuses encoded context).

Data strategy (its sharpest claim): internet-scale passive video for the prior; 10 to 20 hr of robot data per task for post-training. Decanting used 11 hours, container breakdown used 17 hours; the inverse-dynamics model needs only ~10 hr and can use random (non-task, non-expert) motions. Long-context visual memory enables long-horizon tasks, the shell game (object permanence), and one-shot human-demo following at test time without weight updates.

What is missing (and it matters for the thesis): no control-loop Hz, no inference hardware (onboard vs cloud), no per-step latency, no success-rate table. Rhoda's own materials say only the loop runs "multiple times per second" / "every few hundred milliseconds." The widely-cited "10 Hz closed-loop" figure comes only from an independent analyst (Shashi Bellamkonda, Info-Tech Research Group), who frames it conditionally. Academic literature confirms this is the crux: video diffusion is widely called computationally inefficient and unsuitable for real-time control (MinD, arXiv 2506.18897), with real-time only demonstrated at very low resolution (VILP, arXiv 2502.01784, reports ~5 Hz at 96x160).

### 4. Generalist AI — strongest data-scaling story, partial architecture
Founders: Pete Florence (CEO), Andy Zeng (Chief Scientist), Andrew Barry (CTO). Florence and Zeng co-authored PaLM-E and worked on the RT-2/Gemini-Robotics lineage at Google DeepMind; Barry built Atlas/Spot/Stretch work at Boston Dynamics. ~$140M raised; inception round co-led by NVIDIA and boldstart.

Disclosed: GEN-0 (Nov 2025), a large multimodal model pretrained on 270,000+ hours (growing ~10,000 hr/week) of real-world manipulation data, and the first demonstration of robotics scaling laws (downstream performance scales as a power law with pretraining data). The base model is trained with no robot data; it uses low-cost wearable data gloves capturing human activity. GEN-1 (Apr 2, 2026), per Generalist's own blog, "improves average success rates to 99% on tasks where previous models achieve 64%, completes tasks roughly 3x faster than state of the art, and requires only 1 hour of robot data." Per-task figures: servicing robot vacuums at 99% (vs GEN-0's 50%), folding boxes 99% (vs 81%), packing phones 99% (vs 62%). Uses "Harmonic Reasoning" inference and new forms of paged attention.

Gaps: no exact Hz stack or formal action-representation disclosure. High on data strategy and benchmark credibility, medium on control-loop transparency.

### 5. Skild AI — biggest valuation, least control-loop disclosure
Founded 2023 by ex-CMU professors Deepak Pathak (CEO) and Abhinav Gupta (President), both ex-Meta FAIR. Funding: $300M Series A ($1.5B, Jul 2024); a $135M Series B at $4.5B (mid-2025); then a ~$1.4B Series C at >$14B valuation (Jan 2026, led by SoftBank), bringing total capital raised to over $2B. Per Skild's Series C blog, live revenue grew from zero to about $30M in a few months in 2025.

Disclosed: "Skild Brain," an omni-bodied foundation model claimed to control any embodiment (quadrupeds, humanoids, arms, mobile manipulators) without prior knowledge of body form, adapting via in-context learning. Data strategy: human internet video plus large-scale physics simulation, sim-to-real.

Gaps: essentially no public control-loop rate, no action representation, no benchmark success-rate table, no arXiv model card. Highest hype-to-disclosure ratio of the five.

## Comparative scorecard (public disclosures only)

| Axis | Physical Intelligence | Dyna | Generalist | Skild | Rhoda |
|---|---|---|---|---|---|
| Control-loop transparency | High (50 Hz chunking; RTC ~97 ms; arXiv) | Low (interview only) | Med (real-time; no Hz) | Very low | Low ("few hundred ms"; no Hz) |
| System decomposition | High (VLM + flow action expert) | Low | Med | Very low | Med-High (causal video + IDM) |
| Action representation | High (flow matching, FAST, chunking) | Unknown | Partial | Unknown | Med (predicted frames to IDM) |
| Data strategy | High (10k+ hr robot + web; RL experience) | Med (fleet + RM self-improvement) | High (270k+ hr; data gloves; scaling laws) | Med (sim + human video) | High (internet video + ~10 to 20 hr robot) |
| Inference/hardware realism | High (latency-robust, quantified) | Low | Med | Low | Low (undisclosed; cost risk) |
| Result credibility | High (papers + open weights) | High (24h commercial, 99.4%) | High (99%, named tasks, A/B) | Low | Med (uncut videos; no success table) |

Pick: Physical Intelligence for most coherent, defensible full-solution system design. Runner-up on deployment evidence is Dyna; runner-up on scaling thesis is Generalist. Skild looks the most demo/valuation-driven relative to disclosure. Rhoda is the most intellectually interesting and possibly highest-ceiling bet, but its public record is one research blog without the rate/hardware/success numbers a deployment claim requires.

## Opinion on Rhoda's approach along three vectors

(a) Generalizability. Bullish, with caveats. The structural argument is real: reducing control to video prediction lets the pre-training objective consume internet-scale video, and the literature (UniPi 2302.00111; AVDC 2310.08576; GR-2 2410.06158 at 97.7% across 100+ tasks; GR00T N1 2503.14734) shows video/world-model pretraining transfers to novel objects, backgrounds, and tasks. Rhoda's long-context memory and one-shot demo-following are genuine generalization affordances VLAs lack natively. But the embodiment gap is unsolved by video alone, and the inverse-dynamics model still must be trained per embodiment (~10 hr each). Read: plausibly better cross-task transfer, no clear cross-embodiment win vs. Pi, all on curated demos.

(b) Ease of data collection for fine-tuning. Clearly advantaged, the strongest leg. Video-prediction pretraining uses passive, unlabeled video; only the inverse-dynamics stage needs robot data, which can even be random motions. Rhoda's 10 to 20 hr/task compares favorably to Pi's 10k+ hr pretraining plus per-task post-training. Net: the video approach genuinely lowers the marginal data cost of a new task, if the prior transfers.

(c) TAM for reachable tasks. Mixed. The tasks Rhoda shows (decanting, container breakdown, returns, sorting, packing) are precisely the high-mix, low-rate, quasi-static manipulation tasks every player is targeting. Large but contested, not unique. The expansion case (high-speed, contact-rich, high-Hz) is where video generation's inference cost is the gating constraint. The literature repeatedly calls video diffusion unsuitable for real-time control (MinD 2506.18897); real-time has been shown only at low resolution (VILP, ~5 Hz at 96x160). Until Rhoda discloses on-robot Hz and hardware, assume its reachable TAM is the same quasi-static manipulation market as the VLAs, with upside gated by inference economics.

## Literature map (arXiv IDs, venues, dates)

Video-prediction / world-model / generative-video-as-policy:
- UniPi, "Learning Universal Policies via Text-Guided Video Generation," Du, Yang et al., arXiv 2302.00111 (NeurIPS 2023).
- AVDC, "Learning to Act from Actionless Videos through Dense Correspondences," Ko et al., arXiv 2310.08576 (ICLR 2024).
- UniSim, "Learning Interactive Real-World Simulators," arXiv 2310.06114 (ICLR 2024 Outstanding Paper).
- GR-1, "Unleashing Large-Scale Video Generative Pre-training for Visual Robot Manipulation," arXiv 2312.13139.
- GR-2, "A Generative Video-Language-Action Model with Web-Scale Knowledge," Cheang et al. (ByteDance), arXiv 2410.06158 (38M clips; 97.7% across 100+ tasks).
- VILP, "Imitation Learning with Latent Video Planning," Xu et al., arXiv 2502.01784 (RA-L 2025; ~5 Hz at 96x160).
- Additional: DreamGen (2505.12705), Video Prediction Policy (2412.14803), "Video Generators are Robot Policies" (2508.00795), Unified Video Action Model (2503.00200).
- VPT, "Video PreTraining: Learning to Act by Watching Unlabeled Online Videos," NeurIPS 2022.
- Genie / Genie 2 (DeepMind), learned interactive world models.
- Diffusion Forcing, arXiv 2407.01392 (the training scheme Rhoda contrasts against).

Dual-system and action-chunking VLAs:
- RT-2, Brohan et al., arXiv 2307.15818. OpenVLA, arXiv 2406.09246.
- π0, arXiv 2410.24164; π0.5, arXiv 2504.16054; Knowledge Insulation, arXiv 2505.23705; RTC, arXiv 2506.07339 (NeurIPS 2025); π*0.6, arXiv 2511.14759.
- GR00T N1 (NVIDIA), arXiv 2503.14734 (VLM System 2 plus diffusion-transformer System 1).
- Figure Helix (figure.ai/news/helix), S2 at 7 to 9 Hz, S1 at 200 Hz; Helix 02 adds S0 at 1 kHz.
- Gemini Robotics / Gemini Robotics-ER (DeepMind).

Counter-positions to the video thesis:
- Action chunking plus flow matching is sufficient and cheaper at inference: the π0/RTC line (RTC robust to >300 ms latency without video generation).
- Scale solves it: TRI Large Behavior Models, "A Careful Examination of Large Behavior Models for Multitask Dexterous Manipulation," arXiv 2507.05331 (scaled multitask diffusion transformers; 1.6 s chunks; multitask pretraining cuts per-task data ~80%). Boston Dynamics/TRI Atlas LBM: 450M-param diffusion-transformer plus flow-matching, 30 Hz images, 1.6 s chunks.
- Video-gen inference-cost critiques: MinD, arXiv 2506.18897 ("computationally inefficient and unsuitable for real-time control"); VILP, arXiv 2502.01784 (~5 Hz at 96x160).

## Recommendations

1. Anchor the post's pick on disclosure, not demos. Lead with Physical Intelligence and show the actual stack (VLM high-level to flow-matching action expert at <=50 Hz to RTC inference robust to >300 ms).
2. Treat Rhoda as the high-variance contrarian bet and grade it explicitly. Credit the data-efficiency thesis and the two real novelties, but state plainly that the missing Hz/hardware/success-table numbers make it un-underwritable today.
3. Thresholds that change the pick. Flip toward Rhoda if it publishes (a) on-robot closed-loop Hz of at least ~10 Hz on an embedded GPU with per-step latency, (b) a head-to-head success-rate table vs. a π0.5/GR00T baseline on shared tasks, and (c) evidence the internet-video prior transfers to a new embodiment with <=10 hr IDM data. Flip toward Generalist if its robotics scaling laws keep holding and GEN-1's 99%/1-hr numbers replicate on third-party tasks.
4. For VC readers: weight Dyna's 24h commercial autonomy and Generalist's scaling laws as the most de-risked near-term signals; treat Skild's >$14B as priced for a generality not yet publicly evidenced; treat Rhoda's $450M/$1.7B as a bet on the data-efficiency curve, gated by inference economics.

## Caveats

- Rhoda round-naming is inconsistent across sources ("Series A" in Rhoda's own release vs. "Series B" in Humanoids Daily). Use Rhoda's primary release as authoritative and flag the discrepancy.
- Rhoda's "10 Hz" is an analyst attribution, not a Rhoda disclosure. Rhoda primary sources say only "multiple times per second" / "every few hundred milliseconds."
- Skild's mid-2025 round was a $135M Series B at $4.5B (TechCrunch); total raised is over $2B per CEO Pathak.
- Dyna and Skild publish no peer-reviewable architecture; their numbers are company-reported (Dyna's 99.4%/24h is a self-run demo, not an independent benchmark).
- All five companies' headline success rates are self-reported on self-chosen tasks; cross-company comparison is apples-to-oranges. Pi and TRI are the only parties with shared simulation benchmarks (LIBERO, LBM Eval).
- Figures and dates are current to May 31, 2026; the space is moving fast (π0.7, Helix 02, GEN-1 all landed within ~6 months).
