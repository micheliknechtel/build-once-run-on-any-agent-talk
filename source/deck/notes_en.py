N={
1:"""[1:00] Opening.
Hello everyone. This session was created by Andrea Griffiths from GitHub and Shishir Tewari from Procore for GitHub Universe 2026. Today, I'm presenting it to you.
For the next 40 minutes, remember one single idea: you write the know-how once, and any agent can use it.""",
2:"""[1:30] The problem. Ask for a show of hands, wait 3 seconds.
Raise your hand if, this week, you re-explained the same task to an agent… Keep it up if what you were explaining isn't written down anywhere.
That's the problem: context disappears when you close the chat window, and sometimes it only lives in one person's head. For us, that's "Nicolas": the person you call on Friday night when everything breaks.""",
3:"""[3:00] The Procore case (Shishir).
Let's take Procore, a software company for the construction industry. There, every data pipeline follows the same 7 steps: sources, metrics, schema, code, backfill, tests, deployment. And yet, before skills, each one was built from scratch.
The hard part isn't the steps, it's the judgment: the right level of detail, the right name, the joins that duplicate rows, what must never reach the warehouse without review.
Here's a simple duplication example: I join tickets with their comments, then I count the tickets. A ticket with 5 comments counts 5 times. No error, but the result is wrong, and only an expert sees it.
Before skills, Procore had only four of these experts, and everything went through them. With skills, they still define the rules, but they are no longer the only ones applying them.""",
4:"""[2:00] What is a skill?
A skill is just a folder that the agent can find and load. The main file is SKILL.md.
The agent loads it step by step. First, it only reads the name and the description, which costs almost nothing. If the request matches, it reads the instructions. And the extra files, like references or scripts, only if it needs them. That way, the context stays light.
The key point is the description: it's what triggers the skill. If it's badly written, the skill will never be used.""",
5:"""[2:30] The verifier loop.

Andrea wrote several verification skills, like proof-review. Today, I'll show you the Proof Agent. Its job: verify code written by an agent. Because we find Procore's problem again: if the same expert always reviews, everything goes through them. So Andrea had the idea of writing the reviewer's knowledge into a skill, and giving it to the Proof Agent.

The principle is simple: you don't ask a student to grade their own exam. Same for an agent. That's why we have the Proof Agent, which verifies.

On the left, the inputs: the original request, the changed files and the diff. But never the opinion of the agent that wrote the code about its own work.

In the middle, the Proof Agent, running in a GitHub Action.

On the right, the verdict: PASS, FAIL or PARTIAL, always with the file and the line as evidence.

If it's not good, we fix it and verify again. We loop, as shown in the diagram at the bottom.

Note: it only reads the diff, it doesn't run the code.

Let me show you this for real.""",
6:"""[4:00] DEMO 1: Proof Agent.
Tabs: proof-agent SKILL.md + https://github.com/AndreaGriffiths11/teamxray/pull/75
1. Frontmatter name + description: "Two lines decide when the skill loads."
2. When to Verify section (3+ files, *auth*, *secret*, Dockerfile, .env): "Only where the risk is real."
3. "Do NOT share the worker's self-assessment": "This line is the whole idea."
4. PR #75, Proof Agent comments. FAIL: ci-cd.yml around line 119, shell injection via a release tag. "File, line, reason. A human could easily have missed it."
5. PARTIAL: lines 42-43, npm test replaced by vitest. "Not wrong, but it may drop tests. PARTIAL: a human must decide."
6. History: PARTIAL, FAIL, PARTIAL, PARTIAL, PASS. "Fix, re-verify."
7. block-on-fail: false: "Here it was advisory. The merge decision stays in your branch rules, not in the model."
Closing line: skills support engineers' accountability for the release, they don't replace it.
Backup: video proof-agent-narrated.mp4 (3:43).""",
7:"""[3:00] Design standards.

The Proof Agent is a skill for a single task: verifying. But a job is a chain of tasks. At Procore, creating a metric means finding the tables, naming, coding, testing and deploying. And all that knowledge lives in the heads of a few experts.

So Shishir's team created dataforge: four skills that work together. None of them knows the data: all the business context is in a single file, the manifest.

On the slide, there are three rules, and each one maps to a skill.

One: forge-init discovers, it doesn't guess. It reads the existing code to understand how tables are built and named. If it can't find something, it writes "unsupported".

Two: forge-dbx is the only one that talks to the database. An agent can write SQL, but forge-dbx gives it the company's rules: no raw customer data, zones in order, and no guessing. It's the highway code. As a bonus, switching databases, DuckDB or Databricks, is one line in the manifest.

Three: forge-lint guides before, then checks after. The team's rules are loaded before the agent writes the code, not only at the end.

And the fourth one, forge-builder, is the conductor: it makes the three work together, from the issue to the PR.

The proof that it works: Procore published these skills as open source, without changing anything. In the demo, I'll use them for another business, customer support. Only the manifest changes.""",
8:"""In one sentence: skills are reusable. You write the rules once and they work for another business, without rewriting anything.

What the demo proves, in 2 points:
1. Reusable. Procore wrote these 4 skills for its business, construction. Here, I use them as-is for another business, customer support. Only the manifest changes.
2. From a vague ticket to finished work. A human writes a vague request ("count the incidents"). The agent, guided by the skills, does the whole job of a data engineer: explore, design, create the tables, test, deploy, open a PR. It follows the company's rules and a human keeps the final decision.

The analogy: the skills are a chef's recipe book, and the manifest is the kitchen. You change kitchens, the recipe stays the same, and the dish is still good.

TRANSITION
"That was in Copilot CLI. Now, let's take the same skills and open them in another agent: Copilot in VS Code.\"""",
9:"""[4:00] DEMO 3: the same skills, another agent (Copilot in VS Code)

CONCLUSION
"What did we just see?
One. Skills are portable: the same folder runs in Copilot CLI and in VS Code, without rewriting anything.
Two. The human stays in control: permissions are not decided by the skill, they are decided by the tool. I refused the pull request, and it was not created.
Three. Switching engines costs one line: duckdb becomes databricks, and no skill, phase or hook changes.
So: you write the know-how once, and it works on any agent. Build once, run on any agent."

TRANSITION
"But how is this technically possible? Each agent expects its skills in a different format. Let's see how you write skills only once, for all agents.\"""",
10:"""[1:30] One source, three packages.

"Each agent wants its own format. Claude Code, Cursor and Copilot don't read the same files.
So you write the skills only once, in plain Markdown, in skills/SKILL.md. A script generates the three packages, one for each agent.
And on every change, CI checks that the three copies are identical to the source. Nobody edits them by hand, so they never drift.
This is exactly the folder we used in the demo.
So the skill travels. But does everything travel? No.\"""",
11:"""[1:30] What is portable, what the tool provides.

"On the left, what is portable and moves from one agent to another: the procedure, meaning the SKILL.md, the scripts, the references and the assets.
On the right, what doesn't move: it's provided by the tool the skill runs in, for example VS Code, Copilot CLI or Claude Code. The model, the tools, the permissions and the credentials come from it.
You saw it in the demo: VS Code asked me for permission for the pull request, not the skill. The skill knows how to query databricks, but access is granted by VS Code.
One last question: should everything become a skill?\"""",
12:"""[1:30] Skill or app?

"No. A skill is bounded, reusable know-how: a checklist, a release, a migration, a metrics pipeline.
As soon as you need a stable interface, shared state, an audit trail, a long-running process or a rule enforced outside the model, build an application.
For example, a release checklist is a skill. An audited deployment approval for compliance is an application, or CI.
So, concretely, where do you start on Monday?\"""",
13:"""[1:30] Three things for Monday.
One: put the business context in a single file, a manifest.
Two: give each skill a single execution path.
Three: instructions guide generation, checks enforce it. It's tests and policy rules that block the merge or the deployment, not the model's good intentions.""",
14:"""[1:00] Your homework.
Pick one task you keep explaining. Write down what it needs, where it stops, and what the reviewer sees.
Ask the colleague who always gets interrupted, your "Nicolas". Version it, run it in your client, improve it.""",
15:"""[0:30] Thank you.
Everything is at gh.io/skills26: the slides, the two demos and the recordings. Thanks to Andrea Griffiths and Shishir Tewari for this content (CC BY 4.0 license).""",
16:"""Feedback.
Please share your feedback by scanning the QR code: it helps us improve the session. Over to your questions.""",
}
