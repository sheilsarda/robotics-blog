---
title: "VLAs in Contact: The Need for Speed"
date: 2026-05-31
slug: vlas-in-contact
description: "Initiating coverage on three failure modes stopping VLAs from closing the contact loop."
---

# VLAs in Contact: The Need for Speed

*Initiating Coverage on Three Failure Modes Stopping VLAs From Closing the Contact Loop*

## Glossary of terms

### Dual-system architectures

**System 2 (S2):** the slow, deliberative layer. Reasons about goals by interpreting scenes, understanding language, and sequencing behaviors. Typically a vision-language model running at 5–10 Hz.

**System 1 (S1):** the fast, reactive layer. Translates perception and the latest S2 embedding into full-body joint targets at 100–200 Hz.

**System 0 (S0):** the lowest-level controller, handling balance, contact, and whole-body coordination at ~1 kHz. Sometimes hand-engineered (classical control), increasingly learned (e.g. Figure's Helix 02).

### Models and architectures

**Monolithic VLA:** a single model end-to-end, no hierarchical split. Examples: OpenVLA, RT-2, base π₀.

**Hierarchical VLA stack:** an explicit S2/S1 (and sometimes S0) split. Examples: Figure Helix, NVIDIA GR00T N1.

## The frequency gap

The frequency gap between VLAs and contact controllers is 100–1000× and structurally inherent to current architectures. The frequency ceiling of control loops based purely on VLAs is real and acknowledged by model companies. A monolithic VLA runs a forward pass on the current image and instruction, then emits a single action. "Chunking" is a technique that changes the output from one action to a sequence of 50 future actions for instance. A robot can execute those actions at a faster control rate while a different controller prepares the next chunk.

This looks like it solves the problem until one realizes that chunks are committed plans, decided before the model observes what happens during their execution. The closed-loop reaction rate (rate at which the system can respond to an unexpected force spike) remains the slow forward-pass rate. Secondly, force/torque signals carry information vision categorically cannot supply. So even if you somehow ran a VLA at 1 kHz, the input modality is wrong for the task.

Source: Li, Yao, et al. "FAVLA: A Force-Adaptive Fast-Slow VLA model for Contact-Rich Robotic Manipulation." *arXiv* preprint arXiv:2602.23648 (2026).

In the above paper, the authors argue contact-rich VLA control solutions should be bi-modal: semantic scene understanding should remain slow, while contact feedback and corrective control should be fast. Let's talk about solutions, trade offs, and potential alternatives to consider.

## The right architecture is domain-specific

How does one decide what's right for the use case?

**Is the dominant sensing modality something other than vision?** If yes, tactile or force-torque has to flow directly into the fast layer. This covers cube spinning, insertion, polishing, any in-hand work, anything occluded.

**Do the controlling physical parameters vary at deployment vs training?** If yes, you need aggressive domain randomization, or explicit online adaptation. This covers unknown material properties, unknown friction / gravity, novel objects, etc.

**Is the task safety-critical against an external standard?** If yes, the learned policy can propose but cannot enforce. You need a verified runtime-assurance wrapper.

We'll cover each domain individually, and describe potential implementation approaches, trade offs, and alternatives to consider.

## Category 1: Sensing-bound

The control part of the robotics stack generally closes the loop through sensors like Hall-effect encoders, force-torque sensors, tactile arrays, and load cells. The beauty of use-case-specific robots is that you get to build the automation, sensing modalities, and control policies around a single task. The robots I've worked on at Fulfil are a case in point. Encoders, load cells, and precise calibration are enough to do complex manipulation across 20,000+ SKUs (Stock Keeping Units, grocery terminology for individual products).

VLAs sit at the opposite end of the spectrum. They are trained to be generalist by default, with cameras as the primary sensing modality, and the path to deployment is: fine-tune on task demonstrations, evaluate against human operators, ship with teleoperated supervision until reliability is acceptable. The problem this creates for contact-rich work is structural rather than incidental. Vision is the wrong modality for measuring forces. Even with a perfectly positioned camera and zero occlusion, an RGB image cannot tell you that the gripper is about to slip, that the contact normal force has spiked, or that the object's weight differs from what the model assumed.

Three concrete failure modes follow. First, **hand-object occlusion.** When the manipulator is actually doing useful work, the manipulator itself blocks the camera's view of the contact patch. Second, **force-blind chunking.** A vision-only VLA emits an action chunk based on visual state at time T and then commits to it through time T plus several hundred milliseconds; any force event during that window is invisible until the next forward pass. Third, **modality mismatch.** Even if you bolt a force sensor onto the system, the standard VLA architecture pushes that signal through the slow vision-language brain before it can affect the action, which throws away the temporal advantage of force sensing in the first place.

Source: Zhang, Qi, Zheng. "Experiences from Benchmarking Vision-Language-Action Models for Robotic Manipulation." *arXiv* 2511.11298, 2025. Empirical comparison of ACT, OpenVLA-OFT, RDT-1B, π0 on ALOHA Mobile platform.

### A potential solution: Tactile images

A tactile image is a 2D grid where each pixel encodes a contact-related measurement at a specific spatial location on the sensor surface. The field calls each cell a taxel (tactile pixel). The resulting tensor has the same Height × Width × Channels shape as an RGB image, which allows us to reuse a Vision Transformer.

How the image gets created can vary. Optical tactile image sensors use a camera looking at the back of a soft transparent elastomer pad. The camera takes images of the elastomer deformation as it pushes against the object, like from the inside of a fingertip looking outward. Because tactile images aren't real images, we don't get the same cross-sensor portability that one expects from cameras. Also, perhaps this goes without saying, but tactile events happen at millisecond scales (> 1 kHz), whereas cameras tend to run at 24 or 60 FPS.

Source: Hao, Peng, et al. "TLA: Tactile-Language-Action Model for Contact-Rich Manipulation." *arXiv*, 11 Mar. 2025, arxiv.org/abs/2503.08548.

TLA demonstrates that VLM-style reasoning over tactile evidence is feasible at the planning timescale, but too slow for the control loop timescale. This works well for tasks (like the peg-in-hole demonstrated in the paper) where retries don't have any physical penalty. Each failed attempt can be lifted out and corrected without damaging anything, because the geometry is constrained and the forces involved are bounded. If instead the task was one of catching a falling object, for instance, the solution space gets constrained to designing a closed-loop tactile controller.

The same constraint applies to a wider class of tasks including: (i) surgical tissue manipulation has a force budget measured in newtons against soft tissue and no allowance for overshoot; (ii) in-hand reorientation of a rigid object involves slip dynamics at kHz timescales that vision-rate control cannot react to; (iii) grasping fragile objects like produce requires per-object force calibration that the model doesn't necessarily learn from demonstrations.

The gap I'm tracking in the research literature is a way to let a VLM's outputs be modulated by tactile feedback between planning cycles, specifically for the task class where the bandwidth pressures matter. The TLA, OmniVTLA, and ForceVLA papers preserve the VLM but treat tactile as an input token, not as a feedback signal that can change a committed action chunk mid-execution. Nobody on either side has demonstrated a VLM whose action chunks can be tactically modulated by a faster downstream layer that's reading tactile signals in real time. That is the architectural pattern Slow-Propose, Fast-Comply names, and it is the open problem that the next generation of contact-rich VLAs will have to solve.

## Category 2: Distribution-bound

This failure mode happens when the policy sees exactly the data it was designed to see, processes it correctly, and still issues a command that doesn't work. The reason is that the object in front of it might have properties the model never saw during training. The model has no way to know this from a single observation, and the action chunk it commits to is sized for the distribution it learned. I think of this as distribution-bound. You can have perfect tactile feedback and still fail, because tactile tells you the current contact state but not the parameters that govern how the object will respond to your next command.

The repeatability and determinism of traditional control methods (the status quo compared to VLAs) offer a pretty enticing proposition here, since at least that means they don't misbehave in out-of-distribution (OOD) scenarios. For instance, a PID loop tuned for a specific impedance profile is deterministic, and if the deployment falls outside the regime the gains were tuned for, the failure mode is easy to spot and reason about.

Learned policies don't give you this. A diffusion policy or a VLA confronted with an OOD object will confidently emit a plausible-looking action chunk that happens to be wrong, and there's no obvious telltale that distinguishes it from the action chunk it would have emitted in-distribution.

The key question in this category is: can models adapt online, estimate the missing parameters from a short interaction window, and do this without breaking the task in the process?

The formalism for thinking about this rigorously is the hidden-parameter Markov Decision Process (MDP). An MDP is a mathematical model specifying a state space, an action space, a transition function describing how the world evolves under actions, and a reward function describing what success looks like. A hidden-parameter MDP adds one wrinkle: the transition function depends on a set of physical parameters that are not directly observable.

Enter PrivilegedDreamer. It builds on Dreamer, which is a model-based actor-critic framework where the agent learns a world model from real experience and then trains both an actor (which proposes actions) and a critic (which estimates state values) inside imagined rollouts generated by the world model. PrivilegedDreamer extends this by conditioning the world model on the true physical parameters during simulation training, where those parameters are known, and then using a recurrent network to estimate the parameters from observation history at deployment. The actor-critic runs on top of the parameter estimate, which gives the policy both sample efficiency from imagined rollouts and parameter awareness from explicit estimation.

Source: Byrd, Morgan, et al. "PrivilegedDreamer: Explicit Imagination of Privileged Information for Rapid Adaptation of Learned Policies." 2025 IEEE International Conference on Robotics and Automation (ICRA), IEEE, 2025.

Domain randomization at training time is another mitigation for OOD errors. If the policy is trained across a wide enough parameter range that the deployment distribution is hopefully inside the convex hull of training.

Lastly, we have massive data scaling. The argument here is that distribution-bound failures shrink drastically once you've trained on enough data.

The meta question underlying this hunt to squash OOD errors is if learned policies can somehow realize when they're out of distribution, and respond appropriately. To that end, some threads to pull on:

**Ensemble disagreement.** Train multiple policies or world models in parallel, treat their disagreement as an uncertainty signal. When the ensemble agrees, you're in distribution. When it disagrees, you might not be. This is straightforward but expensive at inference, and the calibration is approximate.

**Conformal prediction.** Build a calibration set during training, use it to construct prediction intervals at deployment with formal coverage guarantees. If a new observation falls outside the calibrated region, you have a statistical signal that something has shifted.

**Density estimation / energy-based OOD detection.** Train a generative model of the input distribution, flag inputs that the model assigns low likelihood to.

**Failure-recovery systems with learned diagnosis.** This sidesteps the OOD question by treating it as a behavioral detection problem rather than a distributional one.

## Category 3: Assurance-bound

The failure mode is that the policy issues a command which would work in isolation but violates an external safety or correctness constraint that the system has committed to upholding.

For more on this problem and potential solutions, see [Is It Possible to Run a Vision-Language-Action Model in a Safety-Critical Loop?]({{ site.baseurl }}/blog/vlas-in-safety-critical-applications/).

## Conclusion

The three categories aren't independent. They stack. A surgical robot manipulating soft tissue is sensing-bound because the force budget requires tactile feedback in the fast loop, distribution-bound because every patient's tissue stiffness is different, and assurance-bound because the regulatory pathway has hard requirements that no learned component can self-certify.

The architectural answer turns out to be the same across all three. The slow layer (a VLM, a planner, a learned policy operating at language and scene timescales). The fast layer (impedance control, runtime safety filter). What hasn't been built is a system where the fast layer can override or modulate the slow layer's committed actions in real time, while the slow layer continues to provide strategic direction at chunk rates. That's the Slow-Propose, Fast-Comply pattern in its full form, and it remains an architectural sketch rather than a deployed system.
