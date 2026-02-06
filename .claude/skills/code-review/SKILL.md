---
name: code-review
description: Performs structured code review analyzing quality, security, performance, and maintainability. Use when reviewing PRs, auditing code, or before merging changes.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Code Review

Perform a structured code review on the target files or changes. Analyze for quality, security, performance, and maintainability.

## Review Dimensions

### 1. Correctness
- Does the code do what it's supposed to?
- Are edge cases handled?
- Are error conditions properly managed?

### 2. Security
- No hardcoded secrets or credentials
- Input validation at boundaries
- No injection vulnerabilities (SQL, command, XSS)
- Proper authentication/authorization checks

### 3. Performance
- No N+1 queries or unnecessary loops
- Efficient data structures and algorithms
- Proper use of caching where appropriate
- No memory leaks or resource exhaustion risks

### 4. Maintainability
- Clear naming conventions
- Appropriate abstraction level
- No unnecessary complexity
- Follows project coding standards (see CLAUDE.md)

### 5. Testing
- Are new features covered by tests?
- Are edge cases tested?
- Do tests follow existing patterns?

## Process

1. Read the target files or `git diff` output
2. Analyze each dimension above
3. Categorize findings by severity
4. Provide actionable recommendations with code examples

## Output Format

```markdown
## Code Review: [scope]

### Summary
[1-2 sentence overview]

### Findings

#### Critical
- [ ] [Finding with file:line reference]

#### Warnings
- [ ] [Finding with file:line reference]

#### Suggestions
- [ ] [Finding with file:line reference]

### Verdict
[APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION]
```

## Usage

```bash
# Review specific files
/code-review src/auth/login.py src/auth/session.py

# Review recent changes
/code-review $(git diff --name-only HEAD~1)

# Review staged changes
/code-review --staged
```