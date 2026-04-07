# Product Requirements Document (PRD): Support Ticket Environment for OpenEnv

## 1. Introduction and Objectives
The **Support Ticket Environment** aims to test Large Language Models (LLMs) and agentic frameworks in a highly realistic, consequence-driven enterprise setting. Customer support resolution requires strict adherence to internal policies, information verification, and multi-step reasoning before taking terminal actions (e.g., refunds or escalations). 

**Objective**: Provide an OpenEnv-compliant simulation where an agent assumes the role of a support professional. The environment acts as an adversarial and deterministic evaluator to cleanly quantify an agent's ability to gather state, read contextual rules, and execute appropriate API actions.

## 2. Real-World Utility
Most AI evaluations focus on static benchmarks (MMLU) or gamified environments (Minecraft). However, the most immediate commercial application of agentic AI is customer support automation. 
* **The Problem**: Companies lose millions to unchecked LLM agents hallucinating policies, issuing improper refunds, or frustrating high-tier enterprise clients.
* **The Solution**: This environment models the actual complexity of a ticketing system. It enforces that agents must securely verify `UserData`, correctly attribute `IssueType` to a `Policy`, and avoid taking destructive actions (like rejecting an enterprise client abruptly) under pressure or when faced with confusing queries.

## 3. Environment Architecture
- **State Boundaries**: Each task begins with a newly opened ticket. The episode terminates either when the agent explicitly uses a terminal action (`close_ticket`, `escalate`) or after reaching the hard threshold of $N=10$ steps.
- **Action Constraints**: Intermediate actions (`fetch_user_data`, `check_policy`) do not alter the external ticket state but provide critical context. Terminal actions irreversibly mutate the state and trigger evaluation.
- **Grading and Reward Shaping**: 
   - Graders are strictly deterministic.
   - Fractional rewards are yielded for necessary intermediate contextualization steps (promoting chain-of-thought grounding).
   - Sharp penalties are applied for protocol violations (e.g., escalating a simple refund directly to billing Tier 2).

## 4. Required Agent Capabilities
To succeed on hard tasks, an agent must demonstrate:
- **State Management**: Remembering the constraints of the `policy` retrieved earlier in the episode.
- **Self-Correction**: Adapting if `fetch_user_data` returns constraints (e.g., the user is not a premium member).
- **Nuanced Execution**: Apologizing organically when generating the `reply_to_customer` response during a high-stakes failure ticket.
