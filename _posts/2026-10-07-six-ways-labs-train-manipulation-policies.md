---
title: "From demonstrations to reinforcement learning for robot policies"
date: 2026-10-07
slug: six-ways-labs-train-manipulation-policies
---

I went to IROS 2026 with Moonlake. Our demo ran code-as-policy on semi-repeatable tasks: the robot's program stayed fixed while SAM3 located the objects, so one script handled layouts we had not staged before. The workshops I sat in kept returning to one question: which parts of writing a task and a policy can a foundation model take over, and how much does that speed up reinforcement learning and supervised fine-tuning.

## Four themes from IROS 2026
- We can use LLMs and VLMs to formulate PDDL (Planning Domain Definition Language); used in TAMP (Task and Motion Planning)
- We can use VLMs to supervise VLA reinforcement learning (and even the reward functions can be auto-generated)
- We can use coding agents that are AITL (Agent In The Loop) to generate trajectories to behavior-clone / fine-tune VLAs with, in lieu of real teleoperation
- We can use a coding agent with vision (e.g., Astra) to do real2sim, system identification, scene understanding, task formulation, etc.

## Six ways labs train a manipulation policy

Robotics labs have converged on six ways to train a manipulation policy. I list them with the evidence I could check against each paper.

### Behavior cloning

#### From real-world demonstrations

Teleoperation, handheld grippers like [UMI](https://arxiv.org/abs/2402.10329), and human video. Physical Intelligence's [π0](https://arxiv.org/abs/2410.24164) and [π0.5](https://arxiv.org/abs/2504.16054) and NVIDIA's [GR00T N1](https://arxiv.org/abs/2503.14734) pretrain on broad data and fine-tune on curated teleop. AI2's [MolmoAct2](https://arxiv.org/abs/2605.02881) released 720 hours of bimanual teleop on YAM arms, the largest open bimanual dataset at the time. [Robot Utility Models](https://arxiv.org/abs/2409.05865) collected mobile-manipulation data with a handheld tool and reached 90% success on five tasks in unseen environments; the authors credit the data over the algorithm or the policy class. [mimic-one](https://arxiv.org/abs/2506.11916) ran glove and VR teleop on a 16-DoF hand and reports up to 93.3% out-of-distribution success. [CosmoH2G](https://arxiv.org/abs/2609.07498) paired a handheld gripper with human hand demos for 6,189 episodes over 1,254 objects. On the video side, [V-JEPA 2](https://arxiv.org/abs/2506.09985) pretrains on more than a million hours of internet video, then uses under 62 hours of unlabeled Droid robot video to plan pick-and-place on Franka arms in two labs it never trained in.

#### From synthetic demonstrations generated in simulation

Labs get them by multiplying a few human demos, by running scripted or privileged teachers, or by letting coding agents solve the task. NVIDIA's [MimicGen](https://arxiv.org/abs/2310.17596) turned about 200 human demos into more than 50,000 across 18 tasks by replaying object-relative segments into new scenes and keeping the ones that succeed. [Sim-and-Real Co-Training](https://arxiv.org/abs/2503.24361) builds digital cousins of the real task, multiplies dozens of demos a hundredfold with DexMimicGen, and co-trains with real data for +38% average real-world success. [FoldNet](https://arxiv.org/abs/2505.09109) synthesizes garment assets and folding demos from keypoints, trains on 15K trajectories, and reaches 75% real-world success, with a keypoint-based DAgger adding 25 points. [EmbodiedSWE](https://arxiv.org/abs/2609.27308) has coding agents solve long-horizon tasks in simulation, expands each verified solution into many trajectories, and fine-tunes a VLA that completes a long-horizon task on a real robot from that data alone. [Guava](https://arxiv.org/abs/2606.18363) does the same with GPT-5.4 as the agent: 2,268 MuJoCo trajectories, 714 of them recovery branches from injected failures, no real data, and 90.0% on a real Franka across nine tasks. Our scripted teachers in Isaac Lab Arena sit in this bucket.

### Reinforcement learning in simulation

Most start from an SFT checkpoint. [SimpleVLA-RL](https://arxiv.org/abs/2509.09674) runs GRPO with a binary reward and takes LIBERO from 48.9% to 96.9% with one demo per task, RoboTwin 2.0 from 38.3% to 68.8%, and a real Piper arm from 17.5% to 38.5%. [πRL](https://arxiv.org/abs/2510.25889) adapts PPO to flow-matching policies and takes π0.5 from 77.1% to 98.3% on LIBERO and from 40.1% to 90.9% on ManiSkill. [RIPT-VLA](https://arxiv.org/abs/2505.17016) takes a one-demo policy from 4% to 97% in 15 iterations. [RL4VLA](https://arxiv.org/abs/2505.19789) found PPO beat GRPO and DPO, and that skipping the SFT warm-up cost about twice the environment steps. Guava's GRPO lifted its distilled 4B agent from 63.3% to 90.0% on a shell game. 

#### Skipping the SFT start

[A diffusion policy trained from scratch with RL](https://arxiv.org/abs/2607.10892) learns multi-task block pushing from sparse reward with a reverse curriculum and transfers zero-shot to a real setup.

#### Automating the work around the RL loop

Three papers hand pieces of it to a language model. [LEACL](https://arxiv.org/abs/2607.23515) has an LLM write the curriculum and beats human-designed dense rewards on five LIBERO tasks using sparse reward. [VGRS](https://arxiv.org/abs/2406.05881) has an LLM write reward code and a VLM diagnose failed rollouts, then deploys a small policy with neither model in the loop. [HARBOR](https://arxiv.org/abs/2606.08610) hands environment setup, reward design and tuning to coding agents across 16 tasks.

### Distilling a frontier model's rollouts into a smaller model

The student is either a tool-calling agent or a VLA. [Guava](https://arxiv.org/abs/2606.18363) distills GPT-5.4 into Qwen3.5-4B through a shared tool interface and lands within 3.3 points of the teacher in simulation and on the real robot, at 7.1x lower model-call latency and a third of the tokens per episode. [EmbodiedSWE](https://arxiv.org/abs/2609.27308) distills coding-agent solutions into a VLA. [CaP-X](https://arxiv.org/abs/2603.22435) derives a training-free agent, CaP-Agent0, that reaches human-level reliability on several tasks, and its CaP-RL variant applies RL with verifiable rewards to Qwen2.5-Coder-7B, taking Cube Lift from 25% to 80%. [Show-Harness](https://arxiv.org/abs/2609.10522) adapts small open-source VLMs to its semantic action interface in a few GPU-hours. We do this with GPT-6 Astra.

### Reinforcement learning on the real robot

Physical Intelligence's [π*0.6 with RECAP](https://arxiv.org/abs/2511.14759) runs offline RL with human corrections and more than doubles throughput on laundry, box assembly and espresso. [ConRFT](https://arxiv.org/abs/2502.05450) reaches 96.3% over eight real tasks after 45 to 90 minutes of online training with human interventions. [Real-Time EXPO-FT](https://arxiv.org/abs/2609.18207) has a small online-RL policy edit a large VLA's action chunks and goes from 42% to 97% with 10 minutes of data. [ENPIRE](https://arxiv.org/abs/2606.19980) cuts the human down to initial guidance: coding agents reset the scene, run the policy, verify the outcome with reward code they wrote over camera, height and force readings, and revise the training code, reaching 99% on pin-box organizing, zip-tie fastening and tool use. [VLAC](https://arxiv.org/abs/2509.15937) and [WCM](https://arxiv.org/abs/2607.29613) replace the hand-written reward with a VLM critic that scores progress from camera frames; WCM reports results on seven real tasks with OpenVLA-OFT and π0.5.

### Generative models as data engines

Xiaomi's [U0](https://arxiv.org/abs/2607.11643) edits and generates multi-view robot scenes and raises π0.5's out-of-distribution success from 36.9% to 63.2% on real tasks, and [Physically-based Lighting Generation](https://arxiv.org/abs/2508.01442) relights real demos through inverse rendering for a 38.75% gain under six unseen lighting conditions.

### Improving the skill library and prompt instead of the weights

[RPG](https://arxiv.org/abs/2610.02204) runs Gemini 3.8 Flash as an agent that composes skills from a shared library, mines real ABC episodes to build practice tasks in MuJoCo, and over 15 rounds revises the library from 15 to 38 entries and rewrites the system prompt, taking 22 simulated tasks from 28.6% to 95.0% and then 30 of 30 real trials on a YAM after a common calibration. [SimEX](https://arxiv.org/abs/2609.38982) has a coding agent write a program per trial against an editable toolbox and improves only the toolbox, first through open-ended simulated experiments and then with 10 minutes of robot time per task, for 26 of 30 real successes. [Harness VLA](https://arxiv.org/abs/2607.08448) and [RoboHarness](https://arxiv.org/abs/2603.24060) do the same around a frozen VLA. The learned behavior lives in code and prompts, so it survives a model upgrade: SimEX rose from 67% to 82% when GPT-5.5 was swapped for GPT-6 Astra under the same pipeline. A learning step costs a coding-agent call and simulator time rather than trainer GPUs, and you can read the result. The ceiling is the one Guava names: the policy stays bounded by the tools exposed to it, and the per-step reasoning loop limits reactivity. [SIA](https://arxiv.org/abs/2605.27276) finds that updating both harness and weights beats either alone on its three benchmarks.

## Toward RL on our own tasks

The next post takes the reinforcement learning direction further for tabletop manipulation, no locomotion: the steps involved, and where coding agents can replace hand-written rewards and environments.

A potential recipe for RL would have the following components:

- an action interface that the training data and the simulator share; this is especially important when doing SFT warm-start to teach the policy which tools to use
- a way to start a group of attempts from the same scene (requirement comes from GRPO)
- rewards that measure progress, which a coding model can write from each task's success check; this is based on my experience trying to do RL on tabletop manipulation tasks, but your mileage may vary

## The published recipe: SFT first, then RL

Hypothesis: Machine-generated demonstrations help most when mixed with real data. [Sim-and-Real Co-Training](https://arxiv.org/abs/2503.24361) reports +38% average real-world success from adding simulated data.

![Figure 2 of Sim-and-Real Co-Training: real teleop demos, digital-cousin simulation demos multiplied with DexMimicGen, and prior simulation data are mixed by a sampling ratio alpha and co-trained into one policy that is deployed on the real robot.]({{ site.baseurl }}/assets/posts/six-ways-labs-train-manipulation-policies/cotraining-fig2.png)

*Figure 2 of Maddukuri, Jiang, Chen, Nasiriany et al., [Sim-and-Real Co-Training: A Simple Recipe for Vision-Based Robotic Manipulation](https://arxiv.org/abs/2503.24361) (2025), reproduced from the authors' arXiv source. Dozens of real teleop demos (1x) are mixed with digital-cousin simulation demos multiplied by DexMimicGen (100x) and task-agnostic prior simulation data (1000x). Each training batch draws a fraction α from simulation, and the co-trained policy is deployed directly on the real robot.*

### Literature review:

These seven papers add RL on top of a VLA:

| Paper | Algorithm | Result |
| --- | --- | --- |
| [SimpleVLA-RL](https://arxiv.org/abs/2509.09674) (ICLR 2026) | GRPO, binary reward | LIBERO with one demo per task: 48.9% to 96.9%. RoboTwin 2.0: 38.3% to 68.8%. Real Piper arm: 17.5% to 38.5% |
| [πRL](https://arxiv.org/abs/2510.25889) (2025) | PPO for flow-matching models | π0.5 on LIBERO: 77.1% to 98.3%. ManiSkill: 40.1% to 90.9% |
| [RL4VLA](https://arxiv.org/abs/2505.19789) (NeurIPS 2025) | PPO beat GRPO and DPO | Same in-distribution success as SFT; much better under new positions and disturbances |
| [RIPT-VLA](https://arxiv.org/abs/2505.17016) (2025) | Leave-one-out baseline, dynamic sampling | Strong SFT start: 96.7% to 97.5%. One demo: 4% to 97% in 15 iterations |
| [π\*0.6 / RECAP](https://arxiv.org/abs/2511.14759) (2025) | Offline RL on real robots with human corrections | More than 2x throughput on laundry, box assembly and espresso |
| [ConRFT](https://arxiv.org/abs/2502.05450) (RSS 2025) | Real-robot RL with interventions | 96.3% over 8 real tasks after 45 to 90 minutes online |
| [Real-Time EXPO-FT](https://arxiv.org/abs/2609.18207) (Sept 2026) | Small online-RL policy edits a large VLA's action chunks | Real robot 42% to 97% with 10 minutes of data |

A separate line of work has language models write robot code. [Code as Policies](https://arxiv.org/abs/2209.07753) and [VoxPoser](https://arxiv.org/abs/2307.05973) established the idea by prompting off-the-shelf models, and [EmbodiedBench](https://arxiv.org/abs/2502.09560) found frontier models weak at low-level manipulation, with a best average of 28.9%. [CaP-X](https://arxiv.org/abs/2603.22435) (ICML 2026) is the one paper that RL-trains a code-writing model for robots. GRPO on Qwen2.5-Coder-7B, writing code against APIs that read the simulator's exact state, took Cube Lift from 25% to 80% and Spill Wipe from 30% to 93% in simulation.

The gap between simulation and reality stays small because the policy transfers as code over APIs.

Almost all of these papers run SFT before RL. [SFT Memorizes, RL Generalizes](https://arxiv.org/abs/2501.17161) found that RL generalizes better, but the model still needs SFT first to fix its output format. [Finetuning with Sampling](https://arxiv.org/abs/2610.02140), from Aayush Karan, Sitan Chen and Yilun Du and accepted at NeurIPS 2026, suggests part of SFT's weakness comes from the data. Their sampling method rewrites expert traces to look more like what the model being trained would generate, and plain SFT on the result rivals on-policy methods, often generalizing better and forgetting less. 

Rejection-sampling fine-tuning is the cheap first step: [Yuan et al.](https://arxiv.org/abs/2308.01825) took GSM8K from 35.9% to 49.3% with it. In [DeepSeek-R1](https://arxiv.org/abs/2501.12948), distilling a strong model into a 32B model beat training the 32B model with RL, 72.6% against 47.0% on AIME. 

[Schulman's blog post](https://thinkingmachines.ai/blog/lora/) at Thinking Machines reports that LoRA matches full fine-tuning for RL even at rank 1; the post has not gone through peer review.

A vision-language-action model (VLA) is a pretrained vision-language model adapted to output robot actions. For VLAs, the fine-tuning recipe matters as much as the base model: [OpenVLA-OFT](https://arxiv.org/abs/2502.19645) took LIBERO, a simulated manipulation benchmark, from 76.5% to 97.1% by changing the decoding, action chunking and loss. [π0](https://arxiv.org/abs/2410.24164), [π0.5](https://arxiv.org/abs/2504.16054), [GR00T N1](https://arxiv.org/abs/2503.14734) and [MolmoAct2](https://arxiv.org/abs/2605.02881) all pretrain on broad data, then fine-tune on curated teleoperation data. MolmoAct2 used 720 hours of bimanual teleop on YAM arms, for instance.

[The next post]({{ site.baseurl }}/blog/getting-grpo-to-run-on-our-own-robot-tasks/) covers getting this recipe running on our own tasks: one action interface, seeded starts for GRPO, progress rewards a coding model writes from each success check, and the Miles plumbing underneath.

## Appendix: Glossary of terms

Policy maps what the robot sees, such as camera images, joint angles and an instruction, to what it does next. Each method below adjusts the policy's weights in a different way.

Supervised fine-tuning (SFT), also called behavior cloning, shows the model a recorded demonstration and trains it to predict the demonstrator's next action. The loss measures how far its prediction lands from the recorded action. SFT needs good demonstrations and can only be as good as they are.

Reinforcement learning (RL) lets the model attempt the task itself. Each attempt is a rollout. A reward scores the rollout, and the update nudges the weights so high-scoring behavior becomes more likely. RL needs no demonstrations, but it needs some successes to learn from. The simplest reward is sparse and binary: 1 if the task succeeded at the end, 0 otherwise. It is simple and hard to game, but it says nothing about which of 200 actions mattered. Researchers call that problem credit assignment. A shaped reward gives partial credit for progress instead, such as how far a drawer opened.

Distillation trains a small or general model to copy a stronger one, such as a teacher that can read the simulator's exact state.

## Sources

Papers: we surveyed 46, all on arXiv, and link the ones we cite inline. Also [LoRA Without Regret](https://thinkingmachines.ai/blog/lora/) (Thinking Machines blog).
