# Secret Rotation & History Purge Guide

This project previously contained real Azure secrets in a local `.env`. Follow these steps BEFORE pushing publicly.

## 1. Rotate Exposed Secrets
Rotate any value that ever appeared in your working copy or commit history.
- Azure OpenAI: Create a new key in Azure Portal > Azure OpenAI resource > Keys. Disable the old key.
- Application Insights: Regenerate the instrumentation key **only if** it was committed; otherwise keep current and treat as sensitive.
- Azure Search / Other services: Regenerate access keys.

## 2. Remove Secrets from Git History (If Committed)
If the real key was committed at any point:
### Option A: `git filter-repo` (Recommended)
```pwsh
pip install git-filter-repo
git filter-repo --invert-paths --path .env --path .env.bak
```
Add additional `--path` entries for any file that contained secrets.

### Option B: BFG Repo-Cleaner
```pwsh
java -jar bfg.jar --delete-files .env
# Then
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

After rewriting history, force push (ONLY if repository not yet widely cloned):
```pwsh
git push --force-with-lease origin main
```

## 3. Validate No Secrets Remain
Run a local scan (example patterns + entropy):
```pwsh
Select-String -Path (Get-ChildItem -Recurse -File) -Pattern '(AZURE_OPENAI_API_KEY=|InstrumentationKey=|CLIENT_SECRET=|BEGIN RSA PRIVATE KEY)'
```
(Optional) Integrate a stronger tool like `detect-secrets` or `git-secrets`.

## 4. Use `.env.template` Going Forward
- Keep real `.env` untracked.
- Copy `./.env.template` to `.env` and fill real values locally.
- Never commit `.env`.

## 5. Implement Pre-Commit Secret Scan (Optional)
Example with `detect-secrets`:
```pwsh
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```
Add this to a pre-commit hook:
```pwsh
# .git/hooks/pre-commit
python -m detect_secrets pre-commit --baseline .secrets.baseline || exit 1
```

## 6. CI Safeguards
- Require PR secret scan.
- Block merges containing new high-entropy strings resembling keys.

## 7. Incident Response Checklist
1. Identify leaked secret scope.
2. Rotate secret.
3. Invalidate old key.
4. Purge history if public exposure.
5. Notify stakeholders (security / platform team).
6. Add detection rule to prevent recurrence.

## 8. Verification
Before publishing, confirm:
- `git ls-files` does NOT list `.env`.
- `.env` absent from commit history: `git log -p | Select-String '.env'` returns nothing.
- New keys functional in local dev.

## 9. Principle of Least Privilege
Prefer service principals or managed identity with minimal required roles over broad API keys.

---
Maintain this guide as processes evolve. Update when new services or secret types are added.
