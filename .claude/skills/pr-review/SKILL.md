---
name: pr-review
description: Reviews pull requests by analyzing diffs, commits, and comments. Use when reviewing a PR before merge or when asked to check PR quality.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Pull Request Review

Review a pull request thoroughly by analyzing diffs, commit history, and existing comments.

## Process

1. **Gather context** -- fetch PR diff, commits, and description
2. **Analyze changes** -- review every modified file
3. **Check quality** -- apply review dimensions
4. **Report findings** -- structured output with actionable items

## Review Dimensions

### Functional Correctness
- Does the code implement what the PR description claims?
- Are edge cases handled?
- Do changes break existing behavior?

### Code Quality
- Follows project coding standards (see CLAUDE.md)
- No dead code, unused imports, or debug artifacts
- Appropriate abstraction level
- Clear naming

### Testing
- New features have corresponding tests
- Edge cases are covered
- Tests follow existing patterns

### Security
- No hardcoded secrets in the diff
- Input validation at boundaries
- No new vulnerabilities introduced

### Documentation
- Complex logic is explained
- Public APIs are documented
- README updated if needed

## Data Gathering Commands

```bash
# PR overview
gh pr view $PR_NUMBER

# PR diff
gh pr diff $PR_NUMBER

# PR commits
gh pr view $PR_NUMBER --json commits

# PR comments
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments

# Changed files list
gh pr diff $PR_NUMBER --name-only
```

## Output Format

```markdown
## PR Review: #[number] - [title]

### Summary
[1-2 sentence overview of what this PR does]

### Changes Analyzed
- [file1.py] -- [what changed]
- [file2.py] -- [what changed]

### Findings

#### Must Fix
- [ ] [Critical finding with file:line]

#### Should Fix
- [ ] [Important finding with file:line]

#### Consider
- [ ] [Suggestion with file:line]

### Verdict
[APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION]
```

## Usage

```bash
# Review PR by number
/pr-review 42

# Review PR by URL
/pr-review https://github.com/org/repo/pull/42
```