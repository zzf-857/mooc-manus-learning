# Agent Instructions for MoocManus

This is a personal learning project for transitioning from Unity development to Python and Agent development. The goal is not only to make the code work, but to help the project owner understand the design, Python concepts, backend services, and Agent engineering ideas behind the code.

## Most Important Rule

When the user asks you to read, review, summarize, or explain existing code, do not directly modify code just because you found an error, non-standard pattern, missing content, or possible improvement.

You must first respond in text and explain:

- What you found.
- Why it is a problem or risk.
- Which file and line are involved, when possible.
- What you recommend changing.
- What knowledge point the user should learn from it.

Only modify code after the user gives explicit written permission, such as:

- "可以修改"
- "帮我改"
- "按你的建议修"
- "开始改代码"
- "apply the fix"

## Scope of the Rule

This rule applies to source code, tests, configuration, dependency files, scripts, and project behavior.

Documentation may be updated when the user explicitly asks for documentation work, learning notes, summaries, or project instructions.

## Learning Documentation

Maintain the long-term learning document at:

```text
docs/LEARNING.md
```

After each meaningful development stage, update it with:

- Current stage summary.
- Changed files and their responsibilities.
- Execution flow.
- Mermaid architecture diagrams, expanded to match newly added code.
- Python / FastAPI / backend knowledge points.
- Agent development knowledge points.
- Unity development analogies.
- Current issues and next-step suggestions.
- Security and secret-leakage checks.

## Security Rules

Never commit or expose secrets. Always pay attention to:

- `.env`
- API keys
- access tokens
- passwords
- database connection strings
- cloud service credentials
- private personal information

Use `.env.example` for safe examples. Keep real `.env` files ignored by Git.

Before any commit or push, inspect the staged changes and warn the user if there is any sensitive information risk.

## Git and GitHub CLI Rules

Only commit or push when the user explicitly asks for it.

Before committing, summarize:

- Files changed.
- What the commit will contain.
- Any security risk.
- Suggested commit message.

Before pushing, confirm:

- Remote repository is configured.
- Current branch is correct.
- No secrets are staged or committed.

## Tutoring & Collaboration Mode (带学协作模式)

When the user requests tutoring and code completion, follow this workflow:

1. **Screenshot-Driven Completion (截图驱动补全)**: The user will send screenshots of the teacher's IDE. Analyze the screenshot, explain the code logic using **Unity analogies (Unity 概念类比)**, and list the proposed changes.
2. **Reference Source Code (参考老师源码)**: If there are inconsistencies or if the user has made mistakes, refer to the teacher's official source code directory to inspect correct implementations:
   `F:\youtubeUp\素材\Agent\MCP+A2A 从0到1构建类Manus多Agent全栈应用\源码\imooc-mas\mooc-manus`
3. **No Over-Engineering (禁止过度编写)**: Unless a missing dependency or critical logic block threatens application correctness, do NOT write additional code. Focus strictly on completing and explaining the code captured in the user's screenshot.

