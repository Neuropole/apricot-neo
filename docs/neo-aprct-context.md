Apricot 2.0 --- Autonomous Repository-Native GitHub Engineering Agent
0. Executive Summary
Apricot is evolving from a repository-aware AI code review tool into a
repository-native autonomous software engineering agent.
The end goal is not simply:
> "AI reviews my PR."
The goal is:
> **A GitHub-native AI engineer that understands an entire repository,
> investigates issues, plans work, implements changes, verifies them,
> opens and maintains PRs, and participates in the software-development
> workflow --- while retaining Apricot's core advantage of deep codebase
> knowledge.**
Apricot 2.0 should combine:
Agentic engineering workflows inspired by modern coding agents
and autonomous GitHub bots.
Deep repository awareness inspired by systems such as
Cubic/Greptile.
A repository knowledge/graph layer rather than relying only on
diff-based retrieval.
Model routing so cheap/local models handle inexpensive work and
stronger models handle difficult reasoning.
Evidence and verification so findings are backed by actual code
relationships, tests, and execution.
A web application + GitHub App/bot, rather than relying on
GitHub Actions as the primary product interface.
A dedicated GitHub bot identity/account that can be installed
into repositories and assigned work.
The project should remain open-source/self-hostable where practical.
---
1. Product Vision
Current Apricot
The existing Apricot concept is primarily a repository-aware AI
reviewer.
Conceptually:
``` text
PR / Diff
   ↓
Repository retrieval
   ↓
Relevant code context
   ↓
LLM
   ↓
Review findings
```
The important existing specialization is that Apricot does not want
to treat the diff as the entire world. It can use repository-level
context to understand changes.
That capability must be preserved.
Apricot 2.0
The new architecture turns repository knowledge into the foundation of a
broader agent.
``` text
Issue / PR / Comment / User Task
                ↓
             Planner
                ↓
       Repository Investigation
                ↓
        Repository Knowledge
                ↓
          Agentic Reasoning
                ↓
       Implement / Review / Test
                ↓
           Verification
                ↓
       GitHub action / response
```
The review system becomes one capability of the engineering agent,
not the entire product.
---
2. Product Identity
Apricot should eventually be positioned as:
> **A repository-native autonomous GitHub engineer that understands your
> codebase before it acts.**
Possible capabilities:
Understand a repository
Explain architecture
Investigate bugs
Analyze issues
Plan implementations
Implement issues
Create branches
Modify code
Run tests
Run linters/typecheckers
Self-review changes
Open PRs
Respond to review comments
Fix requested changes
Review existing PRs
Trace regressions
Investigate security issues
Learn repository conventions
Explain why code behaves a certain way
The central differentiator:
> **Apricot's agents operate on a connected model of the repository
> rather than treating files and PR diffs as isolated text.**
---
3. What Apricot Is NOT
Apricot should not simply become:
another ChatGPT wrapper
another generic coding CLI
another Copilot clone
a diff-only PR reviewer
a collection of independent LLM prompts
a GitHub Actions workflow with an LLM attached
a system that blindly launches many agents for every task
The product should have a clear identity:
Repository Brain + Agent Runtime + GitHub Engineering Workflow.
---
4. Reference Products / Inspiration
Apricot can learn from several categories without copying their
implementation.
Greptile-like direction
Important ideas:
GitHub-native product
Repository-aware code intelligence
PR review
Persistent repository context
Bot identity
Web application
Developer-facing workflow
Autonomous/agentic capabilities
Apricot should eventually provide a similar level of repository
integration while maintaining an open/self-hostable architecture.
Cubic-like direction
Important ideas:
Full repository context
Dependency tracing
Architecture awareness
Specialized analysis
Project-specific conventions
Reasoning beyond the changed lines
Investigation rather than superficial pattern matching
Apricot should take this further by making repository understanding the
foundation for implementation and autonomous engineering, not only
review.
Modern coding agents
Important ideas:
Tool use
File editing
Shell execution
Iterative reasoning
Test execution
Error-driven iteration
Git operations
Planning
Autonomous task completion
Apricot should combine these capabilities with its repository knowledge
layer.
---
5. Core Product Loop
The fundamental Apricot loop should become:
``` text
UNDERSTAND
    ↓
INVESTIGATE
    ↓
PLAN
    ↓
ACT
    ↓
TEST
    ↓
VERIFY
    ↓
REPORT / PR
    ↓
ITERATE
```
For example:
``` text
GitHub Issue:
"Users randomly get logged out."

        ↓

Apricot understands the issue.

        ↓

Find authentication subsystem.

        ↓

Trace:
middleware
→ session service
→ token refresh
→ database
→ client/API boundaries

        ↓

Inspect relevant tests.

        ↓

Inspect Git history.

        ↓

Generate hypotheses.

        ↓

Test hypotheses.

        ↓

Identify root cause.

        ↓

Create implementation plan.

        ↓

Modify code.

        ↓

Run targeted tests.

        ↓

Run broader test suite.

        ↓

Self-review.

        ↓

Create PR.

        ↓

Respond to feedback.

        ↓

Finish.
```
---
6. Repository Brain
The Repository Brain is the most important Apricot-specific component.
It should eventually combine several forms of repository knowledge.
6.1 File knowledge
Track:
paths
language
size
configuration
generated files
tests
documentation
ownership where available
6.2 Symbol knowledge
Track:
functions
classes
interfaces
types
methods
variables where useful
exports
declarations
6.3 Relationship knowledge
Track relationships such as:
``` text
imports
exports
calls
references
implements
extends
constructs
tests
configuration dependencies
API exposure
```
Example:
``` text
AuthController
      ↓ calls
AuthService
      ↓ calls
SessionRepository
      ↓ queries
Database
```
6.4 Semantic knowledge
Maintain semantic/vector retrieval for:
relevant code
documentation
architecture descriptions
issue context
historical explanations
Semantic retrieval remains useful, but it is one retrieval
mechanism, not the entire intelligence layer.
6.5 Git knowledge
Apricot should eventually understand:
``` text
git log
git show
git blame
git diff
commit history
changed files
historical behavior
```
This lets it answer:
> "Why is this unusual code here?"
instead of incorrectly assuming unusual code is bad.
6.6 Test knowledge
Map:
``` text
production code
      ↓
tests
```
and eventually:
``` text
function
→ related unit tests
→ integration tests
→ API tests
→ regression tests
```
6.7 Repository conventions
Derive patterns such as:
``` text
error handling
API response shape
naming
dependency injection
testing style
database access
logging
architecture patterns
configuration patterns
```
These should be learned from the repository rather than requiring the
user to manually document everything.
---
7. Repository Graph
A graph layer should eventually represent the repository as a connected
system.
Example:
``` text
                UserService
                    │
              calls │
                    ▼
                UserRepo
                    │
              queries│
                    ▼
                 Database

UserService
     ▲
     │ imported by
     │
AuthController
     ▲
     │ covered by
     │
auth.test.ts
```
This enables questions such as:
Who calls this function?
What depends on this class?
Which APIs expose this code?
Which tests cover this behavior?
What breaks if this symbol changes?
What implementations satisfy this interface?
What configuration controls this behavior?
Graph traversal should become a first-class agent tool.
---
8. Agent Runtime
The LLM should not directly "know" the repository.
It should interact with the repository through tools.
Conceptually:
``` text
                   Agent
                     │
                 Planner
                     │
             ┌───────┴────────┐
             │                │
         Reasoning          Tools
                              │
       ┌──────────────────────┼──────────────────────┐
       │          │           │          │           │
     Search      Read       Graph       Git        Execute
```
Core tools
Repository
``` text
list_files()
read_file()
search_code()
search_text()
find_symbol()
find_references()
find_callers()
find_importers()
trace_dependency()
```
Git
``` text
git_status()
git_diff()
git_log()
git_show()
git_blame()
git_branch()
git_create_branch()
git_commit()
```
Execution
``` text
run_command()
run_tests()
run_targeted_test()
run_linter()
run_typecheck()
run_build()
```
GitHub
Later:
``` text
get_issue()
comment_issue()
create_branch()
create_pull_request()
get_pull_request()
get_review_comments()
comment_pull_request()
request_review()
update_pull_request()
```
The agent should not have unrestricted access by default.
Use permission levels.
---
9. Planner
A central planner coordinates agent work.
Instead of:
``` text
PR → LLM → review
```
use:
``` text
Task
 ↓
Planner
 ↓
Investigation plan
 ↓
Tools / specialized agents
 ↓
Evidence
 ↓
Decision
```
Example:
``` text
Goal:
Determine whether this PR introduces a regression.

Plan:
1. Understand changed symbols.
2. Find direct callers.
3. Trace affected dependencies.
4. Inspect related tests.
5. Compare previous implementation.
6. Run targeted tests.
7. Evaluate findings.
```
The planner must be dynamic.
If new evidence appears:
``` text
Found 4 callers depending on old behavior.

→ investigate those callers
→ inspect their tests
→ run targeted tests
```
The plan can change during execution.
---
10. Specialized Agents
Specialized agents should exist behind the planner.
Possible agents:
``` text
Bug Investigator
Regression Investigator
Implementation Agent
Security Investigator
Architecture Investigator
Test Investigator
Code Review Agent
Convention Investigator
```
Do NOT automatically invoke every agent.
The planner chooses what is relevant.
Example:
``` text
Authentication PR

→ Security Investigator
→ Regression Investigator
→ Test Investigator

No need for:
→ Duplication Investigator
```
---
11. Evidence Engine
Every important conclusion should be backed by evidence.
Bad:
``` text
This may break authentication.
```
Better:
``` text
Finding:
Nullable return contract was removed.

Changed:
src/auth/user.py:42

Affected:
src/api/auth.py:87
src/session.py:123

Evidence:
- auth.py explicitly handles None.
- session.py assumes the previous nullable contract.
- auth tests expect None for unknown users.

Verification:
Targeted tests reproduce the failure.
```
Apricot should distinguish:
``` text
Observation
Hypothesis
Evidence
Verification
Conclusion
Confidence
```
This reduces hallucinated reviews.
---
12. Verification Loop
The agent should not trust its own first answer.
Use:
``` text
Hypothesis
    ↓
Investigation
    ↓
Implementation / Test
    ↓
Execution
    ↓
Result
    ↓
Re-evaluate
```
For code changes:
``` text
edit
 ↓
test
 ↓
failure?
 ├── yes → inspect → fix → test
 └── no  → continue
```
For review findings:
``` text
candidate finding
 ↓
trace affected code
 ↓
inspect tests
 ↓
run targeted test
 ↓
confirm / reject
```
---
13. Model Strategy
Apricot should not depend on one model.
Use model routing.
``` text
                    Apricot
                       │
                  Model Router
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Local          Cheap          Strong
      Model          API            Model
```
Local model
Use for:
summaries
search planning
simple edits
repetitive coding
test output interpretation
cheap experimentation
Example:
``` text
Ollama
Qwen / other local coding model
```
Cheap cloud model
Use for:
normal agent work
medium complexity implementation
planning
repository investigation
Example:
``` text
Groq
GPT-OSS-class models
```
Strong/frontier model
Use selectively for:
difficult architecture
complicated debugging
security-sensitive reasoning
hard implementation
final judging
low-confidence investigations
The frontier model should not process the entire repository
unnecessarily.
Apricot should first distill relevant evidence.
---
14. Development-Time AI Workflow
During Apricot 2.0 development, the developer does NOT need to make
Apricot fully autonomous yet.
Recommended personal workflow:
``` text
Developer
   ↓
Architecture / task definition
   ↓
AI coding agent
   ↓
Local model when possible
   ↓
Strong model when necessary
   ↓
Tests
   ↓
Developer reviews diff
   ↓
Developer commits
```
Possible development tools:
``` text
VS Code
OpenCode CLI
Ollama
Local Qwen
Groq
Codex / Copilot when available
```
The local model is useful as a cheap coding worker.
The development agent harness should be separate from Apricot's eventual
production agent runtime.
---
15. Why OpenCode / Agent Harnesses Matter
A local model alone is:
``` text
Prompt
 ↓
Text
```
An agent harness provides:
``` text
Prompt
 ↓
Model
 ↓
Tool call
 ↓
Repository
 ↓
Tool result
 ↓
Model
 ↓
Edit
 ↓
Test
 ↓
Error
 ↓
Model
 ↓
Fix
```
This turns a small local coding model into a practical worker.
However:
> A harness does not magically make a 3B model reason like a frontier
> model.
It provides tools, context, execution and iteration.
Therefore Apricot should eventually implement its own specialized agent
runtime rather than depending entirely on a third-party coding CLI.
---
16. GitHub-Native Product
This is a major change from a GitHub Actions-centric design.
Do NOT make GitHub Actions the primary product.
GitHub Actions can still be used for CI/testing where appropriate, but
the core Apricot product should be a service/web application connected
to GitHub.
Target architecture:
``` text
Developer
    │
    ▼
Apricot Web App
    │
    ▼
GitHub App
    │
    ├── Issues
    ├── PRs
    ├── Comments
    ├── Repositories
    └── Webhooks
    │
    ▼
Apricot Agent Runtime
```
The bot should have a dedicated identity.
Example conceptual identity:
``` text
Apricot
@apricot-ai
```
or:
``` text
Apricot Bot
```
The exact GitHub username/account can be decided later.
The important requirement is:
> Apricot should appear as a real GitHub participant rather than merely
> as a GitHub Actions workflow.
---
17. GitHub App
The production integration should eventually be a GitHub App.
The app should receive events such as:
``` text
installation
issue opened
issue assigned
issue comment
PR opened
PR updated
PR review
PR comment
push
```
Then Apricot decides whether action is necessary.
Example:
``` text
Issue #142 assigned to Apricot
        ↓
Webhook
        ↓
Apricot backend
        ↓
Create agent task
        ↓
Repository Brain
        ↓
Investigation
        ↓
Implementation
        ↓
PR
```
---
18. Autonomous Issue Workflow
The target workflow:
``` text
Issue
  ↓
Understand issue
  ↓
Inspect repository
  ↓
Identify relevant architecture
  ↓
Investigate root cause
  ↓
Create plan
  ↓
Create branch
  ↓
Implement
  ↓
Run tests
  ↓
Self-review
  ↓
Commit
  ↓
Open PR
  ↓
Wait for feedback
  ↓
Read review comments
  ↓
Implement requested changes
  ↓
Retest
  ↓
Update PR
```
The developer can intervene at any point.
---
19. Human Control
Autonomy should be configurable.
Possible levels:
``` text
Level 0 — Observe
    Read repository only.

Level 1 — Investigate
    Analyze issues and report findings.

Level 2 — Propose
    Create implementation plan and proposed diff.

Level 3 — Implement
    Modify files and run tests.

Level 4 — PR
    Create branch and PR.

Level 5 — Autonomous
    Handle assigned issues and review feedback.
```
Repository owners should choose the level.
---
20. Web Application
A website is required because Apricot is becoming a hosted GitHub
product.
Initial dashboard:
``` text
Dashboard
 ├── Repositories
 ├── Active Tasks
 ├── Issues
 ├── Pull Requests
 ├── Agent Runs
 ├── Findings
 └── Settings
```
For an agent run:
``` text
Task #142

Status:
Investigating

Plan:
✓ Understand auth architecture
✓ Trace session refresh
→ Inspect token rotation
○ Implement fix
○ Run tests
○ Open PR
```
Users should be able to inspect:
agent reasoning summary
tools used
files inspected
changes made
tests run
evidence
final result
Do NOT expose hidden chain-of-thought. Show concise action/evidence
traces, not private internal reasoning.
---
21. Agent Run State
Every autonomous task should have durable state.
Conceptually:
``` text
Task
 ├── repository
 ├── issue / PR
 ├── current branch
 ├── plan
 ├── status
 ├── tool history
 ├── evidence
 ├── files changed
 ├── tests
 └── final result
```
Possible states:
``` text
queued
planning
investigating
implementing
testing
reviewing
waiting_for_feedback
completed
failed
cancelled
```
This is essential for long-running GitHub workflows.
---
22. Backend Architecture
Target:
``` text
                 Web App
                    │
                    ▼
              API / Backend
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   GitHub App   Task Queue   Auth/DB
       │            │
       └──────┬─────┘
              ▼
        Agent Orchestrator
              │
       ┌──────┼───────────┐
       ▼      ▼           ▼
   Planner  Tools    Model Router
       │      │           │
       └──────┼───────────┘
              ▼
       Repository Brain
```
---
23. Task Queue
Long-running agent work should not depend on one HTTP request.
Use a job/task model.
``` text
GitHub webhook
      ↓
Create task
      ↓
Queue
      ↓
Worker
      ↓
Agent runtime
      ↓
Persist state
```
This enables:
retries
cancellation
concurrency limits
resumable tasks
multiple repositories
multiple agents
---
24. Repository Ingestion Pipeline
When a repository is installed:
``` text
GitHub repository
       ↓
Clone / fetch
       ↓
File discovery
       ↓
Language detection
       ↓
Parsing
       ↓
Symbol extraction
       ↓
Relationship extraction
       ↓
Test mapping
       ↓
Git history indexing
       ↓
Semantic indexing
       ↓
Repository Brain
```
Incremental updates should eventually process only changed portions.
Do not re-index an entire large repository for every commit.
---
25. Storage
Logical storage requirements:
``` text
PostgreSQL
    ↓
metadata
tasks
repositories
agent runs
users
GitHub installations
settings

Vector store
    ↓
semantic repository knowledge

Object storage
    ↓
optional artifacts / logs / snapshots

Repository graph
    ↓
symbols + relationships
```
The exact technologies can be selected later.
For early development, keep infrastructure minimal.
---
26. Repository Graph Implementation Strategy
Do not start by building a massive universal compiler.
Start with:
``` text
Phase 1:
file → symbol → import relationships

Phase 2:
function → function calls
class → inheritance
symbol → references

Phase 3:
symbol → tests
API → handler
configuration → code

Phase 4:
cross-language / deeper semantic relationships
```
Use language-specific parsers/tree-sitter-style infrastructure where
practical.
---
27. Semantic Retrieval
Keep the existing semantic retrieval system.
But change its role.
Old:
``` text
LLM
 ↓
semantic search
 ↓
context
```
New:
``` text
Agent
 ├── semantic_search()
 ├── symbol_search()
 ├── graph traversal
 ├── references
 ├── tests
 └── Git history
```
Semantic search becomes one tool among many.
---
28. Context Management
Full repository knowledge does NOT mean sending the entire repository to
the model.
Instead:
``` text
Task
 ↓
Planner
 ↓
Relevant subsystem
 ↓
Graph traversal
 ↓
Relevant files/symbols
 ↓
Semantic retrieval
 ↓
Context compression
 ↓
LLM
```
The model should receive the minimum sufficient evidence.
This reduces:
token usage
latency
hallucination
cost
---
29. Model Router
A future model router can decide:
``` text
task complexity
repository size
required reasoning
confidence
budget
model availability
```
Example:
``` text
Simple:
Local Qwen

Medium:
Groq GPT-OSS

Hard:
Strong API model

Critical:
Strong model + independent judge
```
The router should be provider-agnostic.
Potential providers:
``` text
Ollama
Groq
OpenAI
Anthropic
OpenRouter
other OpenAI-compatible providers
```
---
30. Review Architecture
Review should become:
``` text
PR
 ↓
Changed symbols
 ↓
Impact analysis
 ↓
Affected dependencies
 ↓
Tests
 ↓
History
 ↓
Specialized investigators
 ↓
Evidence
 ↓
Verification
 ↓
Findings
```
Review findings should include:
``` text
severity
confidence
file
line
description
evidence
impact
suggested fix
verification status
```
Avoid noisy comments.
Apricot should prefer:
> fewer, high-confidence findings
over:
> hundreds of speculative comments.
---
31. Self-Review
Before opening a PR, Apricot should review its own changes.
``` text
Implementation
      ↓
Diff
      ↓
Repository-aware review
      ↓
Tests
      ↓
Potential regressions
      ↓
Fix
      ↓
Final PR
```
This is important for autonomous coding.
---
32. Review Feedback Loop
After a PR is created:
``` text
Reviewer comment
      ↓
GitHub webhook
      ↓
Apricot understands comment
      ↓
Locate affected code
      ↓
Determine whether change is valid
      ↓
Modify
      ↓
Test
      ↓
Update PR
      ↓
Reply with evidence
```
Apricot should not blindly accept every reviewer comment.
It should reason about the request.
---
33. Security Model
Autonomous code execution is dangerous.
Sandbox agent execution where possible.
Principles:
least privilege GitHub permissions
repository-specific access
scoped tokens
no arbitrary secrets in model context
command allow/deny policies
execution sandbox
network restrictions where possible
audit logs
human approval for sensitive operations
never expose secrets to LLM prompts unnecessarily
Never let "autonomous" mean "unrestricted".
---
34. Cost Strategy
The main cost is model inference.
Do not use frontier models for everything.
Target:
``` text
             100% of work
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   cheap/local          strong model
      ~80-95%             ~5-20%
```
The actual ratio will be measured.
Use local models for cheap work.
Use Groq/cheap cloud inference for normal agent operations.
Use frontier models only when complexity or confidence demands it.
---
35. Development Infrastructure
During Apricot 2.0 development:
``` text
VS Code
Git
GitHub
Ollama
OpenCode
Local Qwen
Groq
Optional Codex/Copilot
```
The developer remains responsible for:
issue selection
architecture decisions
final code review
commits
PRs
product decisions
AI coding agents handle implementation labor.
---
36. Phased Roadmap
Phase 0 --- Baseline and cleanup
Goal:
Understand and stabilize current Apricot.
Tasks:
map current architecture
identify existing indexing/retrieval components
identify existing agent/LLM flow
identify current GitHub integration
establish tests
document current APIs
create Apricot 2.0 branch/workflow
Deliverable:
A stable baseline.
---
Phase 1 --- Agent Runtime
Goal:
Turn Apricot into a real tool-using agent.
Implement:
agent loop
tool registry
tool execution
filesystem tools
shell/test tools
Git tools
context management
model abstraction
Target:
``` text
Prompt
 ↓
Agent
 ↓
Tool
 ↓
Result
 ↓
Agent
```
Deliverable:
Local Apricot coding agent.
---
Phase 2 --- Repository Brain
Goal:
Make repository knowledge first-class.
Implement:
file index
symbol index
semantic retrieval
dependency relationships
references
call graph
test mapping
Git history
repository metadata
Deliverable:
Repository Brain API.
---
Phase 3 --- Planner
Goal:
Make the agent investigate rather than blindly edit.
Implement:
task decomposition
investigation planning
dynamic replanning
confidence
evidence tracking
context selection
Deliverable:
Repository-aware investigation agent.
---
Phase 4 --- Autonomous Implementation
Goal:
Allow Apricot to solve issues locally.
Workflow:
``` text
Task
 ↓
Investigate
 ↓
Plan
 ↓
Implement
 ↓
Test
 ↓
Fix
 ↓
Self-review
```
Deliverable:
Apricot can take an issue-like task and produce a validated local
change.
---
Phase 5 --- High-quality Review
Goal:
Upgrade the existing review functionality.
Implement:
impact analysis
regression analysis
security analysis
architecture analysis
convention analysis
evidence-based findings
self-review
confidence scoring
Deliverable:
Repository-native PR review.
---
Phase 6 --- GitHub App
Goal:
Turn Apricot into a real GitHub participant.
Implement:
GitHub App
installation flow
webhook handling
repository synchronization
issue ingestion
PR ingestion
comments
branch creation
PR creation
Deliverable:
Dedicated Apricot GitHub bot identity.
---
Phase 7 --- Web Application
Goal:
Make Apricot available as a product.
Implement:
landing page
authentication
GitHub installation
repository dashboard
agent task dashboard
task history
PR/task status
agent activity
settings
model/provider settings
Deliverable:
A usable Apricot web application.
---
Phase 8 --- Autonomous GitHub Engineer
Goal:
Complete the intended workflow.
``` text
Issue assigned
      ↓
Understand
      ↓
Investigate
      ↓
Plan
      ↓
Implement
      ↓
Test
      ↓
Self-review
      ↓
PR
      ↓
Review feedback
      ↓
Fix
      ↓
Retest
      ↓
Complete
```
Deliverable:
A GitHub-native autonomous engineering agent.
---
37. Future Advanced Capabilities
After the core system works:
Repository memory
Remember:
architectural decisions
recurring issues
conventions
previous investigations
important historical context
Continuous learning
Observe accepted/rejected findings.
Use this to improve:
review precision
project-specific conventions
prioritization
Multi-agent investigation
For difficult tasks:
``` text
Planner
 ├── Bug Investigator
 ├── Security Investigator
 ├── Architecture Investigator
 └── Test Investigator
```
Automatic issue triage
Apricot can:
classify issues
identify duplicates
estimate affected subsystem
suggest priority
assign itself when appropriate
Issue planning
Example:
``` text
Issue
 ↓
Repository analysis
 ↓
Affected components
 ↓
Implementation plan
 ↓
Estimated complexity
 ↓
Developer approval
```
Automatic bug investigation
A user can ask:
``` text
Why does X happen?
```
Apricot investigates the repository without immediately changing code.
---
38. Example User Experience
Issue assignment
``` text
Developer:

Assign #421 to Apricot.
```
Apricot:
``` text
Investigating #421.

Affected subsystem:
Authentication

Relevant components:
- AuthMiddleware
- SessionService
- TokenManager
- SessionRepository

I found 3 possible execution paths.

Next:
Trace token refresh behavior and related tests.
```
Then:
``` text
Root cause identified.

The refresh path can invalidate a session when two
requests rotate the same token concurrently.

I reproduced the behavior with the existing integration tests.
```
Then:
``` text
Plan:
1. Make token rotation atomic.
2. Preserve existing session contract.
3. Add concurrency regression test.
4. Run authentication test suite.
```
Then:
``` text
Implemented.

Tests:
42 passed
1 new regression test passed.

Opening PR #438.
```
This is the experience we are aiming for.
---
39. Success Criteria
Apricot 2.0 is successful when it can:
Repository understanding
correctly locate relevant code
trace dependencies
understand architecture
identify affected tests
use Git history when necessary
Agent behavior
plan tasks
use tools correctly
investigate before editing
dynamically replan
verify assumptions
Coding
make multi-file changes
run tests
fix failures
produce clean diffs
Review
identify real bugs
provide evidence
avoid speculative noise
understand project conventions
GitHub
operate as a dedicated bot
receive issues/PR events
work on assigned issues
open PRs
respond to feedback
Product
web dashboard
repository installation
agent run visibility
configurable model providers
configurable autonomy
---
40. Core Design Principles
Principle 1 --- Repository first
The repository is the primary context.
Principle 2 --- Tools over hallucination
If the agent can inspect or execute something, it should.
Principle 3 --- Evidence over confidence
A claim should be supported by repository evidence.
Principle 4 --- Verify before reporting
Run tests or perform additional investigation when possible.
Principle 5 --- Model-agnostic
Apricot should not depend on one model provider.
Principle 6 --- Cheap by default
Use the cheapest capable model.
Principle 7 --- Strong models for hard reasoning
Escalate selectively.
Principle 8 --- Human control
Autonomy must be configurable.
Principle 9 --- GitHub-native
Apricot should be a real GitHub participant, not just a CI script.
Principle 10 --- Open architecture
Providers, models, storage and execution infrastructure should be
replaceable.
---
41. Initial Technical Direction
A reasonable target stack is:
``` text
Frontend:
React / TypeScript

Backend:
Python or TypeScript

Agent runtime:
Custom Apricot runtime

LLM abstraction:
Provider-independent interface

Local inference:
Ollama

Cloud inference:
Groq + other providers

Repository intelligence:
AST / symbol parser
semantic index
repository graph

Database:
PostgreSQL

Queue:
Redis / Postgres-backed queue / equivalent

GitHub:
GitHub App + webhooks

Execution:
Sandboxed workers

Deployment:
Cloud/container-based workers

CI:
GitHub Actions only where useful for verification,
NOT as the primary Apricot product runtime.
```
The exact stack is not locked yet. Architecture should be finalized
after inspecting the current repository.
---
42. First Implementation Order
Do NOT immediately build the website or GitHub bot.
The recommended build order is:
``` text
1. Understand current Apricot
        ↓
2. Agent Runtime
        ↓
3. Repository Brain
        ↓
4. Planner
        ↓
5. Tooling + verification
        ↓
6. Autonomous local issue solving
        ↓
7. High-quality repository-aware review
        ↓
8. GitHub App
        ↓
9. Web application
        ↓
10. Autonomous GitHub workflow
```
This ensures the core intelligence exists before building the product
shell.
---
43. Immediate Next Session
The next development session should begin by inspecting the actual
Apricot repository.
Do NOT assume the existing architecture.
First determine:
``` text
- current directory structure
- current agent implementation
- current LLM abstraction
- current indexing pipeline
- current retrieval pipeline
- current review workflow
- current GitHub integration
- current test system
- current configuration
```
Then produce:
``` text
CURRENT ARCHITECTURE
        ↓
GAPS
        ↓
TARGET ARCHITECTURE
        ↓
MIGRATION PLAN
        ↓
PHASE 1 IMPLEMENTATION
```
The first coding milestone should be a small, testable Agent
Runtime, not the complete autonomous GitHub system.
---
44. Final Vision
The final Apricot should feel like:
``` text
                     APRICOT
                Autonomous Engineer
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      Repository       Planner        GitHub
         Brain           │             Bot
          │              │              │
          └──────────────┼──────────────┘
                         │
                    Agent Runtime
                         │
              ┌──────────┼──────────┐
              │          │          │
             Read       Edit       Execute
              │          │          │
              └──────────┼──────────┘
                         │
                     Verify
                         │
                 ┌───────┴───────┐
                 │               │
                PR            Report
```
The core promise:
> **Apricot doesn't just see your code. It builds a working
> understanding of your repository and uses that understanding to act
> like an engineer.**
The long-term loop is:
``` text
UNDERSTAND
→ INVESTIGATE
→ PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ VERIFY
→ SHIP
→ LEARN
```
And the defining advantage remains:
> **Full-codebase knowledge is not a feature attached to the agent. It
> is the foundation on which the agent operates.**