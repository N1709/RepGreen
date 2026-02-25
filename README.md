# RepGreen

<div align="center">
  <img width="757" height="180" alt="gambar" src="https://github.com/user-attachments/assets/cc219692-81f5-42eb-bbe5-bffb95afdff7" />
</div>

RepGreen is a GitHub Contribution Graph Manager that helps you fill, manage, and automate your GitHub contribution graph.

---

## Features

- **Fill Contribution Graph** — Create commits to green up your GitHub profile
  - Full year mode (up to today)
  - Full year force mode (including future dates)
  - Specific month
  - Specific weekday
- **Clear Contribution Graph** — Completely wipe a repository's history via delete and recreate
- **Auto Schedule (GitHub Actions)** — Automatically add one green square every day using GitHub Actions, no server needed, free forever
- **World Timezone Support** — 170+ timezones across 7 regions for accurate schedule timing
- **Commits per Day Control** — Light, Medium, Heavy, or Custom range

---

## Requirements

- Python 3.7+
- `requests` library (auto-installed)
- GitHub Personal Access Token with scopes:
  - `repo` (full control)
  - `delete_repo` (for clear and reset)
  - `workflow` (for GitHub Actions setup)

---

## Usage

```bash
python3 repgreen.py
```

Follow the interactive menu:

```
MAIN MENU
  1 | Fill contribution graph     create commits to green up your profile
  2 | Clear contribution graph    wipe all commits from a repository
  3 | Auto Schedule               auto-update graph every day
  4 | Exit
```

---

## Auto Schedule (GitHub Actions)

RepGreen can set up a GitHub Actions workflow that automatically adds one green square to your graph every day — completely free, no computer needs to be on.

Setup steps:

1. Run RepGreen and select Menu 3 — Auto Schedule — Setup GitHub Actions
2. Select your repo, timezone, and preferred time
3. RepGreen will push `.github/workflows/repgreen.yml` to your repo
4. Add your token as a GitHub Secret:
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
   - Name: `REPGREEN_TOKEN`
   - Value: your GitHub token
5. Done. One new green square added every day automatically.

---

## Token Setup

Generate your token at: [github.com/settings/tokens/new](https://github.com/settings/tokens/new)

Required scopes: `repo`, `delete_repo`, `workflow`

---

## Modes

| Mode | Description |
|------|-------------|
| Full year | Fill all days from Jan 1 to today |
| Full year (force) | Fill all days Jan 1 to Dec 31 including future dates |
| Specific month | Fill only a chosen month |
| Specific weekday | Fill every occurrence of a chosen weekday |

---

## Disclaimer

This tool is for educational and personal use only. Use responsibly.

---

*This was made purely out of boredom. I had nothing else to do.*
