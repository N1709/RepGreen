<div align="center">

# RepGreen

<img width="757" height="180" alt="gambar" src="https://github.com/user-attachments/assets/cc219692-81f5-42eb-bbe5-bffb95afdff7" />

<br/>
<br/>

<a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.7+-FFD43B?style=flat-square&logo=python&logoColor=blue&labelColor=306998" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub_Actions-Powered-white?style=flat-square&logo=githubactions&logoColor=white&labelColor=000000" /></a>
<a href="#"><img src="https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square&labelColor=1a1a1a" /></a>
<a href="#"><img src="https://img.shields.io/badge/Contribution_Graph-100%25_Green-16a34a?style=flat-square&logo=github&logoColor=white&labelColor=14532d" /></a>
<a href="#"><img src="https://img.shields.io/badge/Schedule-Daily_Auto-6366f1?style=flat-square&logo=clockify&logoColor=white&labelColor=1e1b4b" /></a>
<a href="#"><img src="https://img.shields.io/badge/Made_With-Boredom-ef4444?style=flat-square&logo=htmx&logoColor=white&labelColor=450a0a" /></a>

<br/>
<br/>

> A GitHub Contribution Graph Manager — fill, automate, and manage your GitHub graph with ease.

<br/>

![GitHub last commit](https://img.shields.io/github/last-commit/N1709/msm6125-kernel-6.18?style=flat-square&color=22c55e&labelColor=1a1a1a)
![GitHub repo size](https://img.shields.io/github/repo-size/N1709/msm6125-kernel-6.18?style=flat-square&color=6366f1&labelColor=1a1a1a)
![GitHub stars](https://img.shields.io/github/stars/N1709/msm6125-kernel-6.18?style=flat-square&color=f59e0b&labelColor=1a1a1a)

</div>

---

<div align="center">

## What is RepGreen?

RepGreen is a Python-based CLI tool that lets you take full control of your GitHub contribution graph.
Whether you want to fill it up, clear it out, or automate daily updates — RepGreen has you covered.

</div>

---

<div align="center">

## Features

| | Feature | Description |
|---|---|---|
| 🟩 | **Fill Graph** | Commit to any year, month, or weekday pattern |
| 🗑️ | **Clear Graph** | Wipe all history via repo delete and recreate |
| ⚡ | **GitHub Actions** | Auto-add one square daily, no server needed |
| 🌍 | **170+ Timezones** | Schedule at your exact local time |
| 🎛️ | **Commit Density** | Light, Medium, Heavy, or fully Custom |
| 🔒 | **Token Secure** | Token entered manually, never stored in code |

</div>

---

<div align="center">

## Getting Started

</div>

**1. Install**

```bash
git clone https://github.com/N1709/msm6125-kernel-6.18.git
cd msm6125-kernel-6.18
python3 repgreen.py
```

**2. Generate Token**

Go to [github.com/settings/tokens/new](https://github.com/settings/tokens/new) and enable:

```
repo          (full control)
delete_repo   (for clear and reset)
workflow      (for GitHub Actions setup)
```

**3. Run and Follow the Menu**

```
MAIN MENU
  1 | Fill contribution graph     create commits to green up your profile
  2 | Clear contribution graph    wipe all commits from a repository
  3 | Auto Schedule               auto-update graph every day
  4 | Exit
```

---

<div align="center">

## Auto Schedule — GitHub Actions

</div>

RepGreen can push a workflow directly to your repo that runs every single day at your chosen local time — powered entirely by GitHub's own servers, completely free.

**Setup:**
1. Select **Menu 3 — Auto Schedule — Setup GitHub Actions**
2. Choose your repo, timezone, and time
3. Add a GitHub Secret named `REPGREEN_TOKEN` with your token value
4. Done — one green square every day, forever

---

<div align="center">

## Fill Modes

| Mode | Description |
|------|-------------|
| Full year | Jan 1 to today |
| Full year (force) | Jan 1 to Dec 31 including future |
| Specific month | One chosen month only |
| Specific weekday | Every Monday, Friday, etc. |

</div>

---

<div align="center">

## Disclaimer

This is just for fun. And please stay an honest developer. **Use responsibly**

<br/>
<br/>

---

*This was made purely out of boredom. I had nothing else to do.*

</div>
