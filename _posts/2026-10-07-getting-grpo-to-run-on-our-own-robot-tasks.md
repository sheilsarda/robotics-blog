---
title: "Getting GRPO to run on our own robot tasks"
date: 2026-10-07
slug: getting-grpo-to-run-on-our-own-robot-tasks
---

On October 2, Qi reported the first reinforcement learning run at Moonlake: GRPO on a drawer-opening task, starting from a model fine-tuned on demonstrations. A 0-or-1 success reward taught it nothing. A reward on how far the drawer opened rose steadily and produced one successful rollout after two epochs. That one result is the thread through this post: what RL needs from us before it can run on our own Isaac Lab Arena tasks, and why the reward is the part that decides whether it learns anything.

This post follows [the survey of how labs train manipulation policies]({{ site.baseurl }}/blog/six-ways-labs-train-manipulation-policies/), which places what we do on that map. The short version: we train policies three ways today, all with supervised fine-tuning (SFT) on demonstrations. Nick and Jing Yi train Pi0.5 by behavior cloning on demonstrations that scripted teachers generate in Arena. Xiaoyuan fine-tunes Qwen3.8-27B to call robot tools from teleoperated YAM demonstrations, using Miles, an open-source RL framework we have used only for SFT so far. Qi fine-tunes Qwen on GPT-6 Astra's successful rollouts. None of these has run RL on our own tasks yet.

## What RL needs from us

RL on our own Isaac tasks needs three pieces that SFT did not:

- an action interface that the training data and the simulator share; this is especially important when doing SFT warm-start to teach the policy which tools to use
- a way to start a group of attempts from the same scene (requirement comes from GRPO)
- rewards that measure progress, which a coding model can write from each task's success check; this is based on my experience trying to do RL on tabletop manipulation tasks, but your mileage may vary

## Five steps to RL on our own tasks

1. Agree on one action interface. A bunch of harnesses out there (Guava, Inspect Robots, CaP-X) all have some version of an interface that agents can use to control the robot + observe progress.

   1.1 Actions should include moving TCP, and no-op at a minimum; other primitives like cooperative arm movements (rigid mode) would be a plus. The robot only acts while a tool call executes, so settling and falling need a no-op call of their own. Guava's harness study shows the cost of stopping at the minimum: object-referenced tools like grasp and align reached 88.6% where direct 6-DoF end-effector tools reached 73.3% with the same GPT-5.4.

   1.2 Levers to pull include: how far the robot may move per call. Inspect Robots caps each call at 10 s of motion; our env_runtime adds per-call Cartesian bounds on top, 5 cm and 20° for the Isaac Lab tasks and 20 cm and 45° for Arena.

   1.3 How to drive the robot, either one tool call per turn, or from a persistent interpreter such as a Python session, so the agent can chain tool calls, build control loops, and fetch camera images only when it chooses to look. Qi's switch to a Python session cut image tokens to a sixth.

   1.4 Whether anything persists between episodes. RPG's skill library grows from 15 to 38 entries across practice rounds and SimEX keeps `toolbox.py` and `skill.md` while discarding each task's program, where Qi's Python session keeps nothing once an episode ends. Both papers also expose inverse kinematics and reachability as queries the agent can ask before moving; `robot_tools.v1` only reports `ik_failure` after a rejected call.

2. Write a Miles generate function against env_service. It leases a session, runs the multi-turn loop on Miles' SGLang, appends each tool result and its camera frames as a turn without gradient, saves token ids and log-probs, and then asks env_service for the reward. The env_service client is still a blocking HTTP client, and nothing releases a leased simulator slot when Miles cancels a rollout, so the client has to become asynchronous and an abort hook has to release every live session. Qi has already built both for RoboDojo: his worker pool leases a simulator per episode over the hosts' HTTPS gateways, releases it in a `finally` block, retries an infrastructure failure on another worker with the same seed, and marks the sample aborted after three failures instead of scoring it zero. Porting that pool to env_service's lease, finish and delete endpoints is the work here.

3. Start with rejection sampling. Run the student model, keep its successful rollouts, and run SFT on them. This step needs no log-probs and tests the whole loop, and its rollouts cost simulator time rather than API dollars.

   3.1 For context, the warm-start data has a price, and it is a different cost from this step. GPT-6 Astra acts as the agent in RoboCasa365 episodes, choosing a tool call each turn from the camera frames, and Qi keeps the episodes that pass the success check as SFT data, at about $50 per kept trajectory. That price is why the team is moving to cheaper warm-start sources: teleop data rewritten as agent transcripts in the same tool-call format, and rollouts from Qwen3.8 max, whose logits (raw next-token scores) also allow distillation into the smaller model. Rewritten teleop data brings its own problems. It has long runs of digits the small model cannot predict, and its distribution differs from GPT-6's, which makes the two sources hard to mix.
4. Give each task a progress reward. A coding model writes it from the task's success check, and we screen it on recorded episodes before any training run.
5. Switch to GRPO. A progress reward gives each group a mix of scores even while full successes are rare. Drop groups whose rewards are all equal, drop infrastructure failures instead of scoring them 0, and use asynchronous training, because episodes take minutes. Qi's drawer run is the first evidence for this step: starting from the SFT model, GRPO with a binary reward did not learn, and a reward on how far the drawer opened rose and reached one success after two epochs.

## Progress rewards give GRPO something to compare

GRPO learns from differences inside a group. When the model almost never succeeds, a 0-or-1 reward scores every attempt in the group 0, the differences vanish, and the update does nothing. That is what happened on Qi's drawer.

A progress reward separates attempts that all failed. Say one attempt opened the drawer a few centimeters and another opened it most of the way. Both score 0 under the binary reward, but the progress reward ranks the second above the first, and GRPO makes whatever the second attempt did more likely. Over many groups the attempts open the drawer further, until some cross the success threshold. Qi's run reached its first success after two epochs.

Xiaoyuan's latest results point the same way. On a bottles-and-bins task in simulation, Qwen3.8-27B made no meaningful movements until SFT on 202 Astra rollouts, after which it succeeded on some trials. A day later, Xiaoyuan reported that RL can run directly on Qwen3.8 Flash with a more fine-grained reward, without any SFT data. SFT lifted the 27B model off zero, and the finer reward did the same job for Flash.

Our recorded Ethernet attempts show the same contrast in numbers. Jing Yi's scripted policy made 100 recorded attempts in one scene at plugging an Ethernet cable and a barrel-jack charger into a network switch. The task's 0-or-1 success scores 97 of them 0. A progress reward built from the same success check gives all but one of them partial credit, spread from 0 to 1 with a median of 0.48.

Partial credit carries a risk: a policy can learn to collect it without finishing. The Ethernet reward caps near misses at 0.9, so only a finished insertion earns the full reward.

## A coding model can write the progress rewards

Each success check thresholds a quantity the simulator measures: how far the drawer joint has opened, or how deep and how tilted the plug sits. Turning a threshold into a distance from it is mechanical, and a coding model with the task code and the simulator state can do it. [Eureka](https://arxiv.org/abs/2310.12931) showed this in 2023: GPT-4 wrote reward code for 29 environments across 10 robot morphologies, refined it with training feedback, and beat expert human rewards on 83% of the tasks, with a 52% average normalized improvement. [VGRS](https://arxiv.org/abs/2406.05881) is the 2026 version: an LLM writes the reward code, and when learning stalls a frozen VLM reads the failed rollouts and the LLM densifies the reward, a diagnosis step our pipeline does not have yet. [LEACL](https://arxiv.org/abs/2607.23515) takes the opposite route, keeping the reward sparse and having the LLM write the curriculum, and beats human-designed dense rewards on five LIBERO tasks.

We wrote the Ethernet reward this way. A coding model read the task's success check, which requires the barrel plug at least 8.5 mm deep and tilted no more than 4°, and wrote approach, align, insert and seat terms for each connector. When we scored the reward on the 100 recorded attempts, we found that the success check never tests how far the plug sits off the socket axis, so it passed chargers held off-axis in 28 attempts. The reward now requires the barrel tip within 1 mm of the axis before it counts as seated. We have not trained with it yet.

We propose the same pipeline for each task:

1. A coding model, such as GPT-6 Astra, writes a candidate progress reward from the task's success check.
2. We score each candidate on recorded episodes before any RL. Our minted episodes come labeled accepted or failed. A good reward rises along accepted episodes, stays low on failed ones, and gives no credit for known false passes.
3. We run short GRPO only on candidates that pass the screen.

The screen in step 2 costs CPU time rather than GPU-hours. The progress reward is for training only, and the binary success check stays the evaluation score. In simulation the reward reads exact state. A vision-language model judging camera frames could estimate progress too, but it is slower and noisier and would struggle with millimeter offsets, so we would save it for real-robot data, where no simulator state exists. [VLAC](https://arxiv.org/abs/2509.15937) and [WCM](https://arxiv.org/abs/2607.29613) are that case: VLM critics scoring progress from camera frames for real-world VLA RL, with WCM reporting seven real tasks on OpenVLA-OFT and π0.5.

## Miles already has the hooks RL needs

[Miles](https://github.com/radixark/miles) is an RL post-training framework from RadixArk, forked from Zhipu's [slime](https://github.com/THUDM/slime). RadixArk shipped version 0.1.1 on September 26, 2026. We forked it on September 24.

An environment can plug into Miles at three layers, each giving more control. An agent function talks to an OpenAI-style chat endpoint while Miles records the exact tokens and log-probs, but it handles text only. A generate function hands you the token sequence, the loss mask and the images. A rollout function adds control over batching and the data source. We need the generate function, because our robots observe the world through camera frames.

Outside robotics, teams training agents with RL report the same recipe working on long multi-turn tasks. [SWE-RL](https://arxiv.org/abs/2502.18449) reached 41.0% on SWE-bench Verified, and SkyRL took a 32B agent from 24.4% to 39.4% ([2511.16108](https://arxiv.org/abs/2511.16108)). [RAGEN](https://arxiv.org/abs/2504.20073) names the main failure: reward variance collapses and training stalls. [Endless Terminals](https://arxiv.org/abs/2601.16443) warns that big gains on generated tasks (10.7% to 53.3%) can shrink to almost nothing on a human-curated benchmark (1.1% to 6.7%).

### How it works

Miles splits the work into two halves and coordinates them with Ray, a framework for running Python across many machines. SGLang, a fast inference server, generates the rollouts behind a load balancer called the Miles Router.

![Ray coordinates two halves. The Miles Router spreads prompts across SGLang engines, which return scored rollouts. The trainer, Megatron-LM or FSDP2, updates the weights and pushes them back to SGLang, either on shared GPUs or over NCCL broadcast, RDMA or a shared disk. With LoRA, only the adapters move.]({{ site.baseurl }}/assets/posts/getting-grpo-to-run-on-our-own-robot-tasks/miles-training-step.png)

Miles supports GRPO, PPO and other policy-gradient methods such as GSPO and REINFORCE++, along with tricks from DAPO: wider clipping, and dropping groups whose rewards are all equal. It can also distill on-policy from a teacher model.

For long, multi-turn episodes, an asynchronous mode keeps generating while training consumes finished groups, and it corrects for stale samples with importance sampling.

The table compares Miles with the alternatives.

| Framework | Origin | Rollout engine | Vision-language RL | Why it matters to us |
| --- | --- | --- | --- | --- |
| Miles | RadixArk (slime fork) | SGLang | Yes, via custom generate | Our Qwen3.8-27B SFT already runs in it; day-0 Qwen3.8 support |
| slime | Zhipu / Tsinghua | SGLang | Limited | Upstream of Miles; GLM-series training |
| verl | ByteDance | vLLM, SGLang | Qwen-VL | Most widely used; agent-loop API |
| SkyRL | Berkeley / Anyscale | vLLM, SGLang | Added 2026 | Strong multi-turn agent RL results |
| AReaL | Ant Research | SGLang, vLLM | Qwen2.5/3-VL | Async-first design |
| NeMo-RL | NVIDIA | vLLM | Audio-visual GRPO | NVIDIA stack |
| OpenRLHF / TRL | Community / HF | vLLM | Partial | Simpler, less suited to long episodes |

### How we use it

Our fork adds what SFT needed. A data loader renders each example through the Qwen processor, checks that the prompt is an exact prefix of the full sequence, and puts gradient on the final assistant turn alone. A launcher trains Qwen3.8-27B with LoRA (rank 64) or full fine-tuning, defaulting to batch 64 on 2-way tensor parallelism. Two fixes make FlashAttention 4 work on GB300 machines: one for a backward-pass bug on the vision tower, one for a recompile on every call. The fork can also move a LoRA run onto more GPUs mid-training, and it adds held-out validation and an image-ablation check.

Tool-call SFT on RGB-D images works, and offline it beats the base model. Its held-out loss is 0.944 against the base model's 1.055, it chose the correct tool in 64 of 64 cases, and inverse kinematics, the solver that turns a target hand pose into joint angles, accepted 31 of 31 of its predicted chunks against 16 of 31 for the base model.

Two results temper that. The predicted motion is a median 6% of the reference, so the model predicts standing still most of the time. Blanking the images leaves the action loss almost unchanged, so the model may not be looking at them. We have not run it closed-loop in a simulator yet, and SGLang has not served it.

Guava's fix for a model that learned small, correct moves is recovery data without a human: 714 of its 2,268 trajectories branch from a saved simulator state with an injected missed grasp or dropped object and keep the recovery, lifting success from 79.3% to 87.1%.

## Jev as a fast teacher on privileged state

TypeSafe AI released [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) in early access on September 15, 2026. Jev takes text, with an emphasis on structured program state, and answers with typed values whose possible outputs are defined in advance, each with a calibrated confidence. TypeSafe trains it with a method it calls Reinforcement Learning for Calibrated Decisions and reports 70 to 500 ms per call, $0.042 per million input tokens and free output. Jev does not read images yet. TypeSafe's demo plays Doom at 10 queries a second from game state written as text.

Jev cannot do the two jobs this plan depends on. We cannot train it, because it is a closed model and RL in Miles needs the weights and their log-probs. It cannot run our tool-calling policy either, because that policy acts on camera frames. Its calibrated confidences do not replace those log-probs: importance sampling needs probabilities from the model being trained.

Jev could act on privileged state in simulation: the exact pose of every object, which the simulator has and a camera-based robot does not. We can write the scene as text and let Jev choose each tool call from a fixed set of typed options. If it succeeds often enough, we can keep its successful rollouts as demonstrations, as we keep our scripted teachers' rollouts today, and distill them into the camera-based Qwen policy with SFT. Jev would then be a third data source, next to rewritten teleop data and Qwen3.8 max rollouts. It would not shorten episodes much, since the 5 to 7 s per command in our estimate is the simulator executing each command. [RPG](https://arxiv.org/abs/2610.02204) is the published precedent: a copy of the agent that sees simulator state runs the same skills from the same starts, and removing it drops five-round success from 78.2% to 50.9%, though RPG uses it for failure diagnosis rather than demonstrations.

## Risks and open questions

- Camera frames may not fit in the context window. Three cameras at about 256 tokens per image over 60 turns add up to about 46k image tokens per episode. Qi's switch to a Python session, where the agent asks for images only when it needs them, cut image tokens to a sixth, which would bring this estimate to about 8k. Keeping every frame breaks memory, and dropping old frames breaks the single-sequence sample RL needs. One option is one training sample per turn, each carrying the episode reward; we have not checked Miles' group normalization for this case.
- Data costs money. Qi puts one successful GPT-6 rollout at about $50, close to the cost of building a small environment, and names data scarcity as the biggest bottleneck. With a fixed budget, the team has to choose which data to generate first: better teleop rewrites, Qwen3.8 max rollouts, or fewer tool calls per episode through the robot API. If Xiaoyuan's finding on Qwen3.8 Flash holds, part of that budget moves from SFT data to reward design and RL compute. RL4VLA found that skipping the SFT warm-up roughly doubled the environment steps RL needed, so we should measure the trade: RL on Flash from scratch against Flash after a small SFT run, compared on simulator hours to reach the same success rate. [Finetuning with Sampling](https://arxiv.org/abs/2610.02140) suggests a third option for the mixing problem: move each source's traces toward the student's own outputs before SFT, so teleop rewrites and GPT-6 rollouts stop pulling in different directions.
- Throughput may be low. At 5 to 7 s per command and about 70 calls, one episode takes about 10 minutes, or about 24 episodes per simulator GPU-hour. One GRPO step of 64 prompts times 8 rollouts would take about 20 simulator GPU-hours plus inference GPUs. We estimated these numbers and have not measured them. Running many episodes per Isaac process, short bursts of cloud GPUs on Modal, and fewer, longer tool calls all help.
- We have not served our model in SGLang. Serving multimodal Qwen3.8-27B there, and syncing LoRA weights into it, is untested.
- RL needs trainer, inference and simulator GPUs at the same time, and SFT already runs into the 4-GPU limit.

Pi0.5 offers a second route. In batched Arena it already has a fast worker, at 38.9 environment steps per second per GPU and about $0.07 per 90 s episode. Pi0.5 generates actions with flow matching, though, and RL for it needs a method built for flow-matching policies, such as πRL. We have nothing like that yet. Our Astra rollouts could feed either route: as SFT data for Qwen, which is what we do today, or as the practice episodes a coding agent mines to revise the tool library Qwen will later call.

Qi's drawer run showed a progress reward moving a fine-tuned model where a binary reward could not. Next, we need a closed-loop success rate for our own tool-calling model on our own tasks, and progress rewards for those tasks that hold up on recorded episodes.

## Appendix: Glossary of terms

Policy maps what the robot sees, such as camera images, joint angles and an instruction, to what it does next. Each method below adjusts the policy's weights in a different way.

Supervised fine-tuning (SFT), also called behavior cloning, shows the model a recorded demonstration and trains it to predict the demonstrator's next action. The loss measures how far its prediction lands from the recorded action. SFT needs good demonstrations and can only be as good as they are.

Reinforcement learning (RL) lets the model attempt the task itself. Each attempt is a rollout. A reward scores the rollout, and the update nudges the weights so high-scoring behavior becomes more likely. RL needs no demonstrations, but it needs some successes to learn from. The simplest reward is sparse and binary: 1 if the task succeeded at the end, 0 otherwise. It is simple and hard to game, but it says nothing about which of 200 actions mattered. Researchers call that problem credit assignment. A shaped reward gives partial credit for progress instead, such as how far a drawer opened.

PPO (proximal policy optimization) is the classic RL update. It trains a second network, the critic, to estimate how good each state is, and it clips each update so the policy cannot change too much at once.

GRPO (group relative policy optimization) drops the critic. It runs several rollouts from the same start and scores each one against the group's average. If every rollout in a group gets the same reward, the group teaches nothing, so a near-zero success rate stalls GRPO.

Rejection-sampling fine-tuning (RFT) sits between SFT and RL. You run many attempts, keep the successes, and run SFT on those.

Distillation trains a small or general model to copy a stronger one, such as a teacher that can read the simulator's exact state.

LoRA (low-rank adaptation) trains small add-on matrices in place of all the weights, which costs much less.

On-policy data comes from the current weights.

Off-policy, or stale, data comes from older weights and needs a correction such as importance sampling.

## Sources

Frameworks: [radixark/miles](https://github.com/radixark/miles) · [Miles intro (LMSYS, Nov 2025)](https://www.lmsys.org/blog/2025-11-19-miles) · [Miles v0.1 (LMSYS, Aug 2026)](https://www.lmsys.org/blog/2026-08-18-miles-v0-1) · [THUDM/slime](https://github.com/THUDM/slime) · [Anyscale survey of open-source RL libraries](https://anyscale.com/blog/open-source-rl-libraries-for-llms) · [verl agent loop](https://verl.readthedocs.io/en/latest/advance/agent_loop.html) · [NeMo-RL algorithms](https://docs.nvidia.com/nemo/rl/0.7.0/about/algorithms/index.html)

Papers: linked inline. [The survey post]({{ site.baseurl }}/blog/six-ways-labs-train-manipulation-policies/) carries the full reading list and the literature table.
