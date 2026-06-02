---
title: "Is It Possible to Run a Vision-Language-Action Model in a Safety-Critical Loop?"
date: 2026-05-07
slug: vlas-in-safety-critical-applications
description: "The intersection of sampling-based model predictive control and control barrier functions."
---

# Is It Possible to Run a Vision-Language-Action Model in a Safety-Critical Loop?

*The intersection of Sampling-based Model Predictive Control (MPC) and Control Barrier Functions (CBFs)*

Should one ask a Vision-Language-Action model to drive an excavator?

In 2026, nothing is technically stopping you from taking an off-the-shelf Vision-Language-Action (VLA) model like Pi-0.5 and wiring it to a fully autonomous excavator. Physical Intelligence released the weights, the task is multi-input multi-output control, and a competent imitation policy should track a human operator given the right demonstration data. Whether you should, and can this system ever be certified to operate in real-world scenarios and not just a robot farm is a different question, and it's the one this post is about.

I've spent the last few years writing planning, collision-checking, and trajectory-optimization algorithms for robots, and from my perspective, the capability gap between a hand-tuned planner and a learned policy on novel tasks is closing. There's a world where a synthetic training set from simulation runs generalizes in zero shot.

However, a robot with a hierarchical control system and closed loop motor control architecture is an easier system to reason about / write an FMEA for than a VLA model emitting joint-space commands. It is also more testable.

## Why can't a Vision-Language-Action model just learn safety from demonstrations?

The intuition is straightforward. If a Vision-Language-Action model is trained on enough hours of expert robot operators, the demonstrations themselves should encode safety. The expert never crashes the excavator into the trench wall, swings the boom into a worker, etc.

The VLA learns to imitate the expert. Therefore the VLA also does not crash. The argument is so clean that it forms the implicit business case behind every robotics startup raising on a "scaling laws will solve it" thesis. Train on more data, the model gets better, the failure modes go away.

A behavior cloning model is trained open-loop on demonstrations that were collected under an expert policy: the expert acted, the world responded, the next observation arrived, and the dataset recorded the pair. At inference time the model operates closed-loop: its action shapes the next observation. Consequently, unlike the training distribution, in deployment small errors compound. The model drifts off the demonstrated manifold into states the expert never visited, and once it is off-manifold it has no idea what to do, because nothing in the training data taught it.

The recent NVIDIA survey (Karkus et al.) catalogs five concrete failure modes that fall out of this gap: covariate shift, causal confusion, unmodeled interactivity, downstream control mismatch, and long-tail events. None of them are solved by adding more demonstrations. The first three get worse with scale, because more data without closed-loop feedback amplifies the very correlations that mislead the model. The last two are statistical features of the world, not the dataset, and no amount of expert demonstration changes the long tail.

There is a separate, harder problem that even closed-loop training cannot solve. A human excavator operator knows where the boundary is because they have an explicit mental model: load charts, stability triangles, exclusion zones, swing radius. They use that model to stay inside the boundary, and the demonstrations record the resulting trajectories. A VLA trained on those trajectories sees only the inside, never the boundary, and certainly not the formal description of the boundary. A Control Barrier Function knows it because we wrote it down. The Vision-Language Model evaluator knows it because we trained it on counterfactual unsafe scenarios where the boundary was crossed. Either way, the safety primitive carries information that the demonstrations never had, and we need architecture to bring that information into the loop at inference time.

## Is there a clean way to combine a black-box controller with a formal safety certificate?

The previous section established why a learned policy alone cannot be the whole answer. The failure modes are baked into the training paradigm, and no amount of demonstration data closes the gap. The architectural response is to wrap the learned proposer in a verifier that holds information the demonstrations could not provide. That answers the single-agent version of the question. It does not yet answer the multi-agent version, which is where construction sites and warehouses actually live.

An excavator on a real worksite is not navigating a static obstacle field. How do we account for uncertainty coming from other agents in the workspace, e.g.:

- Other heavy machinery running different policies (some autonomous, some teleoperated, some human-driven)
- Workers walking through the site whose intent we cannot model precisely
- Conveyor belts, dump trucks, and other material moving automation with their own deterministic but non-trivial schedules

What the literature tells us to do:

**Option 1: Predictive obstacle inflation.** Treat the other agent as having a reachable set that grows with time. The barrier function is now over a worst-case bound on where the other robot could be. Tradeoff: most conservative approach, but gets out of hand fast in dense traffic when reachable sets overlap.

**Option 2: Probabilistic CBFs.** Replace the deterministic safety condition with probabilistic guarantees and propagate uncertainty about the other agent's trajectory through the constraint. Tradeoff: you give up "always safe" and accept "safe with probability x."

**Option 3: Biased MPPI, i.e., propose then verify.** Other agents' predicted trajectories shape the cost function, the sampling distribution, or both. Concretely, before the path integral step, you compute candidate sequences over the horizon for the following controllers, then sample noisy rollouts around a mixture of these candidates rather than around a single nominal:

- Goal-attractor controller (a simple controller that points at the goal)
- Repulsion controller (one that pushes away from each predicted obstacle)
- CBF that respects the current predicted scene

E.g., if the dump truck is predicted to come from your right, the repulsion candidate is already steering you slightly left, and the cloud of samples MPPI generates is centered on a sensible "go left" trajectory rather than a generic "keep going straight" one.

It's conceivable that the first two options are too conservative to work in reality, and will result in the controller freezing up anytime another agent enters its workspace, which can create deadlocks or slow down the system.

### Propose then verify seems like a clear winner

The cleanest experimental evidence for this architecture comes from the Herengracht, a narrow historic canal in Amsterdam where Trevisan and Alonso-Mora ran four autonomous vessels through fifty randomized navigation tasks. The setup forces cooperative interaction at two narrow bridge sections where only one boat can pass at a time. Each vessel ran a learning-based trajectory predictor for the other three, plus a Biased-MPPI planner that drew samples from a mixture of ancillary controllers including a braking maneuver and a goal-attractor.

The interesting result is the failure mode of the baseline. Classic interaction-aware MPPI plans each vessel's trajectory assuming the others stay stationary, so when two boats approach the same bridge from opposite sides, both confidently plan to cross first. The sampling distribution is centered on "keep going forward," and there are no samples in the cloud that yield, because the previous-step nominal wasn't a yielding trajectory. The vessels deadlock or collide. Biased-MPPI fixes this by always keeping braking and yielding candidates in the mixture, regardless of what the previous step's nominal was.

This is the structural payoff of coupled prediction with a smart proposal distribution. The planner doesn't need a discrete decision layer above it that says "we're now in yield mode." The mode switch falls out of the importance weighting because the proposal already contained the right candidate trajectory. The CBF backstop catches the rare cases where the predictor was too confident about the other vessel's path.

For a Vision-Language-Action model in the same architectural slot, the math is identical. Replace the goal-attractor candidate with the VLA's preferred action, and the rest of the machinery still applies.

## Drawing inspiration from the self-driving multi-agent path planning problem

### Regulatory standards and certifications needed to deploy in production

ISO 17757 was finalized in 2019 and reflects pre-foundation-model thinking about autonomous machinery. Its guidance for "software" is largely deterministic-controller-shaped. Learned policies do not fit that mold. ISO 22100-5, which is a technical report addressing how machine learning affects machinery safety, also does not cover VLAs.

This is the practical reason the architecture in this post matters. A pure end-to-end VLA driving an excavator is currently outside the boundary of any applicable safety standard, but wrapping it in the architecture specified by MPPI w/ CBFs, where the model proposes actions and a safety filter projects them onto a verifiable safe set, returns the system to the "designed to act within specific limits" category that ISO/TR 22100-5 covers and ISO 17757 can certify against.

### Industry approaches from Tesla, Wayve, Nvidia, etc.

Wayve's AV2.0 explicitly replaces the modular sense-plan-act architecture with a single neural network, and Tesla is doing something similar. The pure end-to-end approach pursued by Wayve and Tesla is harder to certify because there is no decomposable safety argument.

The formal-verification literature has converged on the view that black-box neural systems require either runtime monitors with small trusted bases or new analysis frameworks that have not yet matured.

Three recent papers from NVIDIA's Autonomous Vehicle Research Group, taken together, make the case for the Propose-then-Verify architecture from three angles: why it is necessary in the first place, why sampling-based planning is the practical instantiation, and how the safety primitive generalizes beyond Control Barrier Functions.

The starting point is the most recent of the three. *Beyond Behavior Cloning in Autonomous Driving: A Survey of Closed-Loop Training Techniques* identifies the open-loop to closed-loop gap as the central problem in training end-to-end driving policies: a policy trained open-loop on independent expert demonstrations must operate in a closed-loop world where its own actions shape its future observations (Karkus et al.). The concrete failure modes the authors enumerate are the same failure modes a verifier in the Propose-then-Verify architecture is positioned to catch at deployment time. The survey's contribution is methodology for closing the open-loop to closed-loop gap at training time, organized along three axes: how ego actions are generated, how the environment response is generated, and what the training objective is. Read together with the 2023 *Interactive Joint Planning for Autonomous Vehicles* (Chen et al.), the picture sharpens.

The complexity of the learned predictor rules out gradient-based MPC, leaving Propose-then-Verify as the practical option. Biased-MPPI is one specific algorithm inside this category (Trevisan and Alonso-Mora). The Pavone group's contribution across the two NVIDIA papers is the broader argument that the category itself is forced.

The third paper generalizes the verifier in the architecture. *SafeVL: Driving Safety Evaluation via Meticulous Reasoning in Vision Language Models* fine-tunes a Vision-Language Model on a synthesized counterfactual dataset to act as a safety filter on top of UniAD, a conventional end-to-end driving policy (Ma et al.). UniAD proposes a trajectory, SafeVL evaluates it through a four-step chain-of-thought reasoning trace covering scene understanding, critical object detection, behavior prediction, and safety analysis, and the system iteratively resamples up to three times if the trajectory is flagged unsafe.

On the NeuroNCAP closed-loop benchmark, the architecture reduced average collision rate from 60.4% to 52.5%, an 8% absolute improvement. The structural takeaway matters more than the number: the verifier in Propose-then-Verify does not have to be a Control Barrier Function.

### Two roads diverged in a yellow wood…

While it's pretty clear that the current regulatory framework says any system that wants to be certifiable under ISO 17757 needs a decomposable safety argument which pure end-to-end VLAs cannot provide, Wayve and Tesla are betting against.

Their thesis is that a sufficiently large foundation model trained on enough data eventually does not need an explicit safety architecture. That bet may pay off in road vehicles, where the regulatory pathway is itself in flux. One could argue that it is difficult to make the same bet for an excavator on a construction site, where the rules of engagement are less clear and the cost of being wrong is arguably more catastrophic.

Thus, Propose-then-Verify is the option that is certifiable today, supported by industrial research, and flexible enough to host learned policies that go beyond what any hand-coded controller could express.

## Conclusion: So is it possible?

Propose-then-Verify is the certifiable architecture, sampling-based MPC is the proposer, the verifier is whatever safety primitive can encode the boundary you care about. Most of the open problems for Vision-Language-Action models in safety-critical settings are problems the research community has already framed.

It is worth calling out though that papers cited in this post are from less contact-rich domains where the safety primitive is a geometric constraint on a trajectory through free space. As a stark example, the barrier functions for warehouse manipulators, surgical robots, and humanoid contact tasks need to encode contact dynamics and force limits, not just a swept volume. The field has moved to a world where the controller is a transformer with learned dynamics. We now need to develop verifiers that can express constraints over learned representations, accept neural networks as components, and generalize across tasks the way the controller does.

Propose-then-Verify is the architecture that survives the transition. The verifier inside it is still under construction.

## References

Chen, Yuxiao, Sushant Veer, Peter Karkus, and Marco Pavone. "Interactive Joint Planning for Autonomous Vehicles." *arXiv*, 27 Oct. 2023, arxiv.org/abs/2310.18301.

Jackson, Daniel, Valerie Richmond, Mike Wang, Jeff Chow, Uriel Guajardo, Soonho Kong, Sergio Campos, Geoffrey Litt, and Nikos Arechiga. "Certified Control: An Architecture for Verifiable Safety of Autonomous Vehicles." *arXiv*, 13 Apr. 2021, arxiv.org/abs/2104.06178.

Karkus, Peter, Maximilian Igl, Yuxiao Chen, Kashyap Chitta, et al. "Beyond Behavior Cloning in Autonomous Driving: A Survey of Closed-Loop Training Techniques." NVIDIA Research, 2025.

Kou, Hongrui, Zhouhang Lyu, Ziyu Wang, Cheng Wang, and Yuxin Zhang. "UniSTPA: A Safety Analysis Framework for End-to-End Autonomous Driving." *arXiv*, 21 May 2025, arxiv.org/abs/2505.15005.

Ma, Yingzi, Yulong Cao, Wenhao Ding, Yuxiao Chen, et al. "SafeVL: Driving Safety Evaluation via Meticulous Reasoning in Vision Language Models." NVIDIA Research, Dec. 2025.

Parwana, Hardik, Taekyung Kim, Kehan Long, Bardh Hoxha, Hideki Okamoto, Georgios Fainekos, and Dimitra Panagou. "BR-MPPI: Barrier Rate Guided MPPI for Enforcing Multiple Inequality Constraints with Learned Signed Distance Field." *arXiv*, 9 June 2025, arxiv.org/abs/2506.07325.

Tao, Chuyuan, Hunmin Kim, Hyungjin Yoon, Naira Hovakimyan, and Petros Voulgaris. "Control Barrier Function Augmentation in Sampling-based Control Algorithm for Sample Efficiency." *arXiv*, 12 Nov. 2021, arxiv.org/abs/2111.06974.

Trevisan, Elia, and Javier Alonso-Mora. "Biased-MPPI: Informing Sampling-Based Model Predictive Control by Fusing Ancillary Controllers." *IEEE Robotics and Automation Letters*, vol. 9, no. 3, 2024, pp. 2604–2611, arxiv.org/abs/2401.09241.

Yin, Ji, Charles Dawson, Chuchu Fan, and Panagiotis Tsiotras. "Shield Model Predictive Path Integral: A Computationally Efficient Robust MPC Approach Using Control Barrier Functions." *IEEE Robotics and Automation Letters*, 2023, arxiv.org/abs/2302.11719. Presented at ICRA 2024.
