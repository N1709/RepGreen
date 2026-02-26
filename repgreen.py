#!/usr/bin/env python3
"""
RepGreen - GitHub Contribution Graph Manager
"""

import subprocess
import sys
import os
import json
import random
import time
from datetime import datetime, timedelta

# ── Install dependencies ───────────────────────────────────────────────────────
def install_deps():
    for dep in ["requests"]:
        try:
            __import__(dep)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep, "-q"])

install_deps()
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Robust HTTP session with retry ────────────────────────────────────────────
def make_session():
    s = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s

SESSION = make_session()

def api_get(url, token):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    for attempt in range(3):
        try:
            r = SESSION.get(url, headers=headers, timeout=15)
            return r
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

# ── ANSI Colors ────────────────────────────────────────────────────────────────
R  = "\033[0m"
B  = "\033[1m"
G  = "\033[38;5;35m"
W  = "\033[97m"
GR = "\033[90m"
CY = "\033[38;5;39m"
YL = "\033[38;5;220m"
RD = "\033[38;5;196m"

def clear():
    os.system("clear" if os.name == "posix" else "cls")

def banner():
    clear()
    print(f"""
{G}{B}  ██████╗ ███████╗██████╗  ██████╗ ██████╗ ███████╗███████╗███╗   ██╗
  ██╔══██╗██╔════╝██╔══██╗██╔════╝ ██╔══██╗██╔════╝██╔════╝████╗  ██║
  ██████╔╝█████╗  ██████╔╝██║  ███╗██████╔╝█████╗  █████╗  ██╔██╗ ██║
  ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
  ██║  ██║███████╗██║     ╚██████╔╝██║  ██║███████╗███████╗██║ ╚████║
  ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝{R}
{GR}  GitHub Contribution Graph Manager                          v2.7.0{R}
{GR}  ─────────────────────────────────────────────────────────────────{R}
""")

def line(char="─", color=GR):
    print(f"{color}{char * 65}{R}")

def prompt(text):
    return input(f"{CY}  > {W}{text}: {R}").strip()

def info(text):
    print(f"{GR}  {text}{R}")

def success(text):
    print(f"{G}  {text}{R}")

def error(text):
    print(f"{RD}  {text}{R}")

def warn(text):
    print(f"{YL}  {text}{R}")

def section(title):
    print(f"\n{B}{W}  {title}{R}")
    line()

def menu_item(num, text, desc=""):
    d = f"{GR}  {desc}{R}" if desc else ""
    print(f"  {CY}{num}{GR} |{R} {W}{text}{R}{d}")

# ── GitHub API ─────────────────────────────────────────────────────────────────
def validate_token(token):
    try:
        r = api_get("https://api.github.com/user", token)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def get_repos(token):
    repos, page = [], 1
    while True:
        try:
            r = api_get(
                f"https://api.github.com/user/repos?per_page=100&page={page}&affiliation=owner",
                token
            )
            data = r.json()
            if not data or not isinstance(data, list):
                break
            repos.extend(data)
            page += 1
        except Exception:
            break
    return repos

def get_join_year(user_data):
    created_at = user_data.get("created_at", "")
    if created_at:
        return datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").year
    return None

# ── Date Generation ────────────────────────────────────────────────────────────
MONTHS = {
    1:"January", 2:"February", 3:"March", 4:"April",
    5:"May", 6:"June", 7:"July", 8:"August",
    9:"September", 10:"October", 11:"November", 12:"December"
}
DAYS = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}

def generate_dates(mode, year, min_c, max_c, bulan=None, hari=None, skip_pct=15, force_full=False):
    today = datetime.now().date()
    dates = []

    def add_day(d):
        # Use noon (12:00:00) so UTC offset never shifts to wrong day
        dt = datetime(d.year, d.month, d.day, 12, 0, 0)
        count = random.randint(min_c, max_c)
        for _ in range(count):
            dates.append(dt)

    start = datetime(year, 1, 1).date()
    end   = datetime(year, 12, 31).date()

    # Only cap at today if NOT force_full mode
    if not force_full and end > today:
        end = today

    current = start
    while current <= end:
        if mode == "full":
            add_day(current)
        elif mode == "month" and current.month == bulan:
            if random.randint(1, 100) > skip_pct:
                add_day(current)
        elif mode == "day" and current.weekday() == hari:
            add_day(current)
        current += timedelta(days=1)

    return dates

# ── Git Operations ─────────────────────────────────────────────────────────────
def run(cmd, cwd=None, env=None):
    # env passed in = complete override
    if env is None:
        e = {**os.environ, "LANG": "C", "LC_ALL": "C"}
    else:
        e = {**env, "LANG": "C", "LC_ALL": "C"}
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=e)


def resolve_branch(work_dir):
    """
    Detect existing branch. If none found, ask user to create one.
    Returns branch name string or None on cancel.
    """
    # 1. Try current branch
    branch = run(["git", "-C", work_dir, "branch", "--show-current"]).stdout.strip()

    # 2. Try all local branches
    if not branch or branch == "HEAD":
        branches_raw = run(["git", "-C", work_dir, "branch"]).stdout.strip()
        branches = [b.strip().lstrip("* ").strip() for b in branches_raw.splitlines() if b.strip()]
        if len(branches) == 1:
            branch = branches[0]
        elif len(branches) > 1:
            section("SELECT BRANCH")
            info("Multiple branches detected:")
            for i, b in enumerate(branches):
                menu_item(i + 1, b)
            print()
            choice = prompt("Select branch number")
            try:
                branch = branches[int(choice) - 1]
            except (ValueError, IndexError):
                error("Invalid selection.")
                return None

    # 3. No branch at all — repo is empty or fresh clone with no commits
    if not branch or branch == "HEAD":
        section("NO BRANCH DETECTED")
        warn("This repository has no branch yet.")
        print()
        menu_item(1, "Create branch  main")
        menu_item(2, "Create branch  master")
        menu_item(3, "Create custom branch")
        menu_item(0, "Cancel")
        print()
        choice = prompt("Select option")
        if choice == "1":
            branch = "main"
        elif choice == "2":
            branch = "master"
        elif choice == "3":
            branch = prompt("Enter branch name")
            if not branch:
                error("Branch name cannot be empty.")
                return None
        else:
            warn("Cancelled.")
            return None

        # Init repo and create the branch
        run(["git", "-C", work_dir, "init"])
        run(["git", "-C", work_dir, "checkout", "-b", branch])
        success(f"Branch '{branch}' created.")

    return branch

def make_commits(repo_url, token, username, dates, repo_data=None, work_dir="/tmp/repgreen_work"):
    """
    Reset the repo clean (delete+recreate via API if repo_data is available),
    then git init locally, make all commits, push --force.
    Don't clone the old repo—so the old history isn't included at all.
    """
    if repo_data:
        section("RESETTING REPOSITORY")
        info("Deleting and recreating repo to ensure clean history...")

        owner       = repo_data["owner"]["login"]
        repo_name   = repo_data["name"]
        private     = repo_data["private"]
        description = repo_data.get("description") or ""

        ok = api_delete_repo(token, owner, repo_name)
        if not ok:
            warn("Failed to delete repo via API — skipping reset, pushing anyway (old history may remain).")
            warn("Make sure your token has 'delete_repo' scope for a full clean.")
        else:
            success("Old repo deleted.")
            info("Waiting for GitHub to process...")
            time.sleep(4)
            new_repo = api_create_repo(token, repo_name, private=private, description=description)
            if new_repo:
                success(f"Repo '{repo_name}' recreated — fresh and clean.")
            else:
                error("Failed to recreate repo. Process aborted.")
                return False

    if os.path.exists(work_dir):
        run(["rm", "-rf", work_dir])
    os.makedirs(work_dir)

    run(["git", "-C", work_dir, "init"])
    run(["git", "-C", work_dir, "config", "user.name", username])
    run(["git", "-C", work_dir, "config", "user.email", f"{username}@users.noreply.github.com"])

    data_file = os.path.join(work_dir, "data.json")
    total = len(dates)

    section("CREATING COMMITS")
    info(f"Total commits to create: {total}")
    print()

    failed = 0
    for i, d in enumerate(dates):
        date_str = d.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        with open(data_file, "w") as f:
            json.dump({"date": date_str, "i": i}, f)

        run(["git", "-C", work_dir, "add", "data.json"])
        e = {**os.environ,
             "GIT_AUTHOR_DATE":    date_str,
             "GIT_COMMITTER_DATE": date_str,
             "LANG": "C", "LC_ALL": "C"}
        r_commit = subprocess.run(
            ["git", "-C", work_dir, "commit", "-m", date_str],
            capture_output=True, text=True, env=e
        )
        if r_commit.returncode != 0:
            failed += 1

        pct = int((i + 1) / total * 50)
        bar = f"{G}{chr(9608) * pct}{GR}{chr(9617) * (50 - pct)}{R}"
        print(f"\r  [{bar}] {W}{i+1}/{total}{R}  {GR}{d.strftime('%Y-%m-%d')}{R}", end="", flush=True)

    if failed > 0:
        warn(f"\n{failed} commits failed — check git config.")

    print()

    section("PUSHING")
    branch = "main"
    run(["git", "-C", work_dir, "branch", "-M", branch])
    info(f"Branch: {branch}")

    auth_url = repo_url.replace("https://", f"https://{username}:{token}@")
    run(["git", "-C", work_dir, "remote", "add", "origin", auth_url])

    result = run(["git", "-C", work_dir, "push", "origin", branch, "--force"])

    if result.returncode == 0:
        success("Push successful!")
        return True
    else:
        error(f"Push failed: {result.stderr.strip()}")
        return False

def api_delete_repo(token, owner, repo_name):
    """Delete a GitHub repository via API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = SESSION.delete(
            f"https://api.github.com/repos/{owner}/{repo_name}",
            headers=headers, timeout=15
        )
        return r.status_code == 204
    except Exception as e:
        error(f"API error: {e}")
        return False

def api_create_repo(token, repo_name, private=True, description=""):
    """Recreate a GitHub repository via API."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    payload = {
        "name": repo_name,
        "private": private,
        "description": description,
        "auto_init": False
    }
    try:
        r = SESSION.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=payload,
            timeout=15
        )
        if r.status_code == 201:
            return r.json()
        else:
            error(f"Create repo failed ({r.status_code}): {r.json().get('message','')}")
            return None
    except Exception as e:
        error(f"API error: {e}")
        return None

def clear_commits(repo_data, token, username):
    """
    Nuclear clear: delete the repo entirely via GitHub API,
    then recreate it fresh with the same name/visibility.
    Requires token scope: repo + delete_repo
    """
    repo_name   = repo_data["name"]
    owner       = repo_data["owner"]["login"]
    private     = repo_data["private"]
    description = repo_data.get("description") or ""
    clone_url   = repo_data["clone_url"]

    section("DELETING REPOSITORY")
    info(f"Deleting  : {owner}/{repo_name}")
    warn("Permanently deleting all commits, branches, and history...")
    print()

    ok = api_delete_repo(token, owner, repo_name)
    if not ok:
        error("Failed to delete repository via API.")
        error("Make sure your token has 'delete_repo' scope enabled.")
        return False

    success("Repository deleted.")
    info("Waiting for GitHub to process deletion...")
    time.sleep(4)

    section("RECREATING REPOSITORY")
    info(f"Recreating: {owner}/{repo_name}  ({'private' if private else 'public'})")

    new_repo = api_create_repo(token, repo_name, private=private, description=description)
    if not new_repo:
        error("Failed to recreate repository.")
        return False

    success(f"Repository '{repo_name}' recreated — completely clean.")
    return clone_url

# ── Repo Selection ─────────────────────────────────────────────────────────────
def select_repo(token, return_data=False):
    """
    Select a repository.
    If return_data=True, returns (clone_url, repo_data_dict) for clear operations.
    Otherwise returns clone_url string only.
    """
    info("Fetching repositories...")
    repos = get_repos(token)

    if not repos:
        error("No repositories found.")
        return (None, None) if return_data else None

    section("SELECT REPOSITORY")
    for i, r in enumerate(repos):
        visibility = "private" if r["private"] else "public "
        print(f"  {CY}{i+1:>3}{GR} |{R} {GR}[{visibility}]{R} {W}{r['full_name']}{R}")

    if not return_data:
        menu_item(0, "Enter URL manually")
    print()

    choice = prompt("Select repository number")

    if not return_data and choice == "0":
        url = prompt("Repository URL (https://github.com/...)")
        url = url if url.endswith(".git") else url + ".git"
        return url

    try:
        idx = int(choice) - 1
        repo = repos[idx]
        if return_data:
            return repo["clone_url"], repo
        return repo["clone_url"]
    except (ValueError, IndexError):
        error("Invalid selection.")
        return (None, None) if return_data else None


# ── GitHub Actions Schedule ────────────────────────────────────────────────────

# ── GitHub Actions Schedule ────────────────────────────────────────────────────

# Complete world timezone database grouped by region
TIMEZONE_DB = {
    "Asia": [
        ("AFT",  "UTC+4:30",  4.5,  "Afghanistan — Kabul"),
        ("ALMT", "UTC+6",     6,    "Kazakhstan — Almaty"),
        ("AMST", "UTC+5",     5,    "Uzbekistan — Samarkand"),
        ("ANAST","UTC+12",    12,   "Russia — Anadyr"),
        ("AQTT", "UTC+5",     5,    "Kazakhstan — Aqtau"),
        ("AZST", "UTC+4",     4,    "Azerbaijan — Baku"),
        ("BNT",  "UTC+8",     8,    "Brunei — Bandar Seri Begawan"),
        ("BTT",  "UTC+6",     6,    "Bhutan — Thimphu"),
        ("CCT",  "UTC+6:30",  6.5,  "Myanmar — Yangon"),
        ("CST",  "UTC+8",     8,    "China — Beijing, Shanghai"),
        ("HKT",  "UTC+8",     8,    "Hong Kong"),
        ("ICT",  "UTC+7",     7,    "Thailand — Bangkok"),
        ("IDT",  "UTC+3",     3,    "Israel — Jerusalem"),
        ("IRDT", "UTC+4:30",  4.5,  "Iran — Tehran"),
        ("IST",  "UTC+5:30",  5.5,  "India — New Delhi, Mumbai"),
        ("JST",  "UTC+9",     9,    "Japan — Tokyo, Osaka"),
        ("KGT",  "UTC+6",     6,    "Kyrgyzstan — Bishkek"),
        ("KST",  "UTC+9",     9,    "South Korea — Seoul"),
        ("KRAT", "UTC+7",     7,    "Russia — Krasnoyarsk"),
        ("LKT",  "UTC+5:30",  5.5,  "Sri Lanka — Colombo"),
        ("MMT",  "UTC+6:30",  6.5,  "Myanmar — Naypyidaw"),
        ("MSD",  "UTC+3",     3,    "Russia — Moscow"),
        ("MSK",  "UTC+3",     3,    "Russia — Moscow, Saint Petersburg"),
        ("MVT",  "UTC+5",     5,    "Maldives — Male"),
        ("MYT",  "UTC+8",     8,    "Malaysia — Kuala Lumpur"),
        ("NPT",  "UTC+5:45",  5.75, "Nepal — Kathmandu"),
        ("NOVT", "UTC+7",     7,    "Russia — Novosibirsk"),
        ("OMST", "UTC+6",     6,    "Russia — Omsk"),
        ("ORAT", "UTC+5",     5,    "Kazakhstan — Oral"),
        ("PETT", "UTC+12",    12,   "Russia — Petropavlovsk-Kamchatsky"),
        ("PHT",  "UTC+8",     8,    "Philippines — Manila"),
        ("PKT",  "UTC+5",     5,    "Pakistan — Karachi, Islamabad"),
        ("QYZT", "UTC+6",     6,    "Kazakhstan — Qyzylorda"),
        ("SAKT", "UTC+11",    11,   "Russia — Sakhalin"),
        ("SGT",  "UTC+8",     8,    "Singapore"),
        ("SRT",  "UTC+3",     3,    "Syria — Damascus"),
        ("TJT",  "UTC+5",     5,    "Tajikistan — Dushanbe"),
        ("TLT",  "UTC+9",     9,    "Timor-Leste — Dili"),
        ("TMT",  "UTC+5",     5,    "Turkmenistan — Ashgabat"),
        ("TRT",  "UTC+3",     3,    "Turkey — Istanbul, Ankara"),
        ("ULAT", "UTC+8",     8,    "Mongolia — Ulaanbaatar"),
        ("UZT",  "UTC+5",     5,    "Uzbekistan — Tashkent"),
        ("VLAT", "UTC+10",    10,   "Russia — Vladivostok"),
        ("WIB",  "UTC+7",     7,    "Indonesia — Jakarta, Surabaya, Medan"),
        ("WIT",  "UTC+9",     9,    "Indonesia — Jayapura"),
        ("WITA", "UTC+8",     8,    "Indonesia — Makassar, Bali, Lombok"),
        ("YAKT", "UTC+9",     9,    "Russia — Yakutsk"),
        ("YEKT", "UTC+5",     5,    "Russia — Yekaterinburg"),
    ],
    "Middle East": [
        ("AMT",  "UTC+4",     4,    "Armenia — Yerevan"),
        ("AST",  "UTC+3",     3,    "Saudi Arabia — Riyadh"),
        ("EAT",  "UTC+3",     3,    "Ethiopia, Kenya, Uganda"),
        ("GET",  "UTC+4",     4,    "Georgia — Tbilisi"),
        ("GST",  "UTC+4",     4,    "UAE — Dubai, Abu Dhabi"),
        ("IDT",  "UTC+3",     3,    "Israel — Tel Aviv"),
        ("IRDT", "UTC+4:30",  4.5,  "Iran — Tehran (DST)"),
        ("IRST", "UTC+3:30",  3.5,  "Iran — Tehran (Standard)"),
        ("KWT",  "UTC+3",     3,    "Kuwait — Kuwait City"),
        ("MMT",  "UTC+3",     3,    "Yemen — Sana'a"),
        ("OMST", "UTC+4",     4,    "Oman — Muscat"),
        ("PKT",  "UTC+5",     5,    "Pakistan — Lahore"),
        ("QAT",  "UTC+3",     3,    "Qatar — Doha"),
        ("TRT",  "UTC+3",     3,    "Turkey — Istanbul"),
    ],
    "Europe": [
        ("AZOT", "UTC-1",    -1,    "Portugal — Azores"),
        ("WET",  "UTC+0",    0,     "Portugal — Lisbon, Iceland — Reykjavik"),
        ("GMT",  "UTC+0",    0,     "UK — London (Standard)"),
        ("BST",  "UTC+1",    1,     "UK — London (Summer)"),
        ("CET",  "UTC+1",    1,     "France, Germany, Italy, Spain — Central Europe"),
        ("CEST", "UTC+2",    2,     "Central Europe — Summer Time"),
        ("EET",  "UTC+2",    2,     "Greece, Romania, Bulgaria, Ukraine"),
        ("EEST", "UTC+3",    3,     "Eastern Europe — Summer Time"),
        ("FET",  "UTC+3",    3,     "Belarus — Minsk"),
        ("MSK",  "UTC+3",    3,     "Russia — Moscow, Saint Petersburg"),
        ("TRT",  "UTC+3",    3,     "Turkey — Istanbul"),
        ("SAMT", "UTC+4",    4,     "Russia — Samara"),
        ("GET",  "UTC+4",    4,     "Georgia — Tbilisi"),
        ("AZST", "UTC+4",    4,     "Azerbaijan — Baku"),
        ("YEKT", "UTC+5",    5,     "Russia — Yekaterinburg"),
    ],
    "Africa": [
        ("CVT",  "UTC-1",   -1,    "Cape Verde — Praia"),
        ("GMT",  "UTC+0",    0,    "Ghana, Senegal, Ivory Coast — West Africa"),
        ("WAT",  "UTC+1",    1,    "Nigeria, Cameroon, Angola — West Africa"),
        ("CAT",  "UTC+2",    2,    "South Africa, Zimbabwe, Zambia"),
        ("EAT",  "UTC+3",    3,    "Kenya, Tanzania, Ethiopia, Uganda"),
        ("SAST", "UTC+2",    2,    "South Africa — Johannesburg, Cape Town"),
        ("EET",  "UTC+2",    2,    "Egypt — Cairo"),
        ("CET",  "UTC+1",    1,    "Algeria, Tunisia, Libya"),
        ("IOT",  "UTC+3",    3,    "British Indian Ocean Territory"),
        ("MUT",  "UTC+4",    4,    "Mauritius — Port Louis"),
        ("RET",  "UTC+4",    4,    "Réunion — Saint-Denis"),
        ("SCT",  "UTC+4",    4,    "Seychelles — Victoria"),
    ],
    "Americas": [
        ("NT",   "UTC-3:30",-3.5,  "Canada — Newfoundland"),
        ("AST",  "UTC-4",   -4,    "Canada — Halifax, Atlantic"),
        ("EST",  "UTC-5",   -5,    "USA — New York, Miami, Toronto"),
        ("CST",  "UTC-6",   -6,    "USA — Chicago, Houston, Dallas"),
        ("MST",  "UTC-7",   -7,    "USA — Denver, Phoenix"),
        ("PST",  "UTC-8",   -8,    "USA — Los Angeles, Seattle, Vancouver"),
        ("AKST", "UTC-9",   -9,    "USA — Alaska, Anchorage"),
        ("HST",  "UTC-10", -10,    "USA — Hawaii, Honolulu"),
        ("BRT",  "UTC-3",   -3,    "Brazil — Brasilia, Rio, São Paulo"),
        ("AMT",  "UTC-4",   -4,    "Brazil — Manaus, Amazon"),
        ("ART",  "UTC-3",   -3,    "Argentina — Buenos Aires"),
        ("CLT",  "UTC-4",   -4,    "Chile — Santiago"),
        ("COT",  "UTC-5",   -5,    "Colombia — Bogotá"),
        ("ECT",  "UTC-5",   -5,    "Ecuador — Quito"),
        ("PET",  "UTC-5",   -5,    "Peru — Lima"),
        ("VET",  "UTC-4",   -4,    "Venezuela — Caracas"),
        ("BOT",  "UTC-4",   -4,    "Bolivia — La Paz"),
        ("PYT",  "UTC-4",   -4,    "Paraguay — Asuncion"),
        ("UYT",  "UTC-3",   -3,    "Uruguay — Montevideo"),
        ("GYT",  "UTC-4",   -4,    "Guyana — Georgetown"),
        ("SRT",  "UTC-3",   -3,    "Suriname — Paramaribo"),
        ("FKST", "UTC-3",   -3,    "Falkland Islands"),
        ("GFT",  "UTC-3",   -3,    "French Guiana — Cayenne"),
        ("AST",  "UTC-4",   -4,    "Puerto Rico, US Virgin Islands"),
        ("EST",  "UTC-5",   -5,    "Mexico — Mexico City"),
        ("CST",  "UTC-6",   -6,    "Mexico — Guadalajara"),
        ("MST",  "UTC-7",   -7,    "Mexico — Chihuahua, Mazatlan"),
    ],
    "Pacific / Oceania": [
        ("AEST", "UTC+10",  10,    "Australia — Sydney, Melbourne, Brisbane"),
        ("AEDT", "UTC+11",  11,    "Australia — Sydney (Summer)"),
        ("ACST", "UTC+9:30",9.5,   "Australia — Adelaide, Darwin"),
        ("ACDT", "UTC+10:30",10.5, "Australia — Adelaide (Summer)"),
        ("AWST", "UTC+8",    8,    "Australia — Perth"),
        ("NZST", "UTC+12",  12,    "New Zealand — Auckland, Wellington"),
        ("NZDT", "UTC+13",  13,    "New Zealand (Summer)"),
        ("FJT",  "UTC+12",  12,    "Fiji — Suva"),
        ("PGT",  "UTC+10",  10,    "Papua New Guinea — Port Moresby"),
        ("SBT",  "UTC+11",  11,    "Solomon Islands — Honiara"),
        ("VUT",  "UTC+11",  11,    "Vanuatu — Port Vila"),
        ("NCT",  "UTC+11",  11,    "New Caledonia — Noumea"),
        ("WST",  "UTC+13",  13,    "Samoa — Apia"),
        ("TOT",  "UTC+13",  13,    "Tonga — Nukualofa"),
        ("CHAST","UTC+12:45",12.75,"Chatham Islands"),
        ("HST",  "UTC-10", -10,    "Hawaii — Honolulu"),
        ("SST",  "UTC-11", -11,    "American Samoa — Pago Pago"),
        ("LINT", "UTC+14",  14,    "Kiribati — Line Islands"),
        ("PHOT", "UTC+13",  13,    "Kiribati — Phoenix Islands"),
        ("GILT", "UTC+12",  12,    "Kiribati — Gilbert Islands"),
        ("MHT",  "UTC+12",  12,    "Marshall Islands — Majuro"),
        ("PWT",  "UTC+9",    9,    "Palau — Ngerulmud"),
        ("FST",  "UTC+11",  11,    "Micronesia — Palikir"),
        ("PONT", "UTC+11",  11,    "Micronesia — Pohnpei"),
        ("CHUT", "UTC+10",  10,    "Micronesia — Chuuk"),
        ("NRT",  "UTC+12",  12,    "Nauru — Yaren"),
        ("TVT",  "UTC+12",  12,    "Tuvalu — Funafuti"),
        ("WFT",  "UTC+12",  12,    "Wallis and Futuna"),
        ("CKT",  "UTC-10", -10,    "Cook Islands — Avarua"),
        ("TKT",  "UTC+13",  13,    "Tokelau"),
        ("NFT",  "UTC+11",  11,    "Norfolk Island"),
        ("CCT",  "UTC+6:30",6.5,   "Cocos Islands"),
        ("CXT",  "UTC+7",    7,    "Christmas Island"),
    ],
    "UTC / Manual": [
        ("UTC-12","UTC-12",-12,   "Baker Island, Howland Island"),
        ("UTC-11","UTC-11",-11,   "American Samoa"),
        ("UTC-10","UTC-10",-10,   "Hawaii"),
        ("UTC-9", "UTC-9", -9,    "Alaska"),
        ("UTC-8", "UTC-8", -8,    "Pacific US"),
        ("UTC-7", "UTC-7", -7,    "Mountain US"),
        ("UTC-6", "UTC-6", -6,    "Central US"),
        ("UTC-5", "UTC-5", -5,    "Eastern US"),
        ("UTC-4", "UTC-4", -4,    "Atlantic"),
        ("UTC-3", "UTC-3", -3,    "Brazil, Argentina"),
        ("UTC-2", "UTC-2", -2,    "South Georgia"),
        ("UTC-1", "UTC-1", -1,    "Azores"),
        ("UTC+0", "UTC+0",  0,    "London, Reykjavik"),
        ("UTC+1", "UTC+1",  1,    "Central Europe"),
        ("UTC+2", "UTC+2",  2,    "Eastern Europe"),
        ("UTC+3", "UTC+3",  3,    "Moscow, East Africa"),
        ("UTC+4", "UTC+4",  4,    "Dubai, Baku"),
        ("UTC+5", "UTC+5",  5,    "Pakistan, Uzbekistan"),
        ("UTC+5:30","UTC+5:30",5.5,"India, Sri Lanka"),
        ("UTC+5:45","UTC+5:45",5.75,"Nepal"),
        ("UTC+6", "UTC+6",  6,    "Bangladesh, Bhutan"),
        ("UTC+6:30","UTC+6:30",6.5,"Myanmar"),
        ("UTC+7", "UTC+7",  7,    "Indonesia WIB, Thailand"),
        ("UTC+8", "UTC+8",  8,    "China, Singapore, Malaysia"),
        ("UTC+9", "UTC+9",  9,    "Japan, Korea"),
        ("UTC+9:30","UTC+9:30",9.5,"Australia Central"),
        ("UTC+10","UTC+10", 10,   "Australia East"),
        ("UTC+11","UTC+11", 11,   "Solomon Islands"),
        ("UTC+12","UTC+12", 12,   "New Zealand"),
        ("UTC+13","UTC+13", 13,   "Samoa, Tonga"),
        ("UTC+14","UTC+14", 14,   "Kiribati Line Islands"),
    ],
}

REGIONS = list(TIMEZONE_DB.keys())

def local_to_utc_hour(local_hour, tz_offset):
    return int((local_hour - tz_offset) % 24)

def select_timezone():
    """Two-step timezone selector: Region → Timezone. Returns (label, offset) or (None, None)."""
    while True:
        section("SELECT REGION")
        for i, region in enumerate(REGIONS):
            count = len(TIMEZONE_DB[region])
            menu_item(str(i + 1), region, f"  ({count} timezones)")
        menu_item("0", "Cancel")
        print()
        r_choice = prompt("Select region")
        if r_choice == "0":
            return None, None
        try:
            region = REGIONS[int(r_choice) - 1]
        except (ValueError, IndexError):
            error("Invalid selection.")
            continue

        # Show timezones in that region
        while True:
            section(f"SELECT TIMEZONE — {region}")
            tzlist = TIMEZONE_DB[region]
            for i, (abbr, utc_str, offset, desc) in enumerate(tzlist):
                menu_item(str(i + 1), f"{abbr:<6} {utc_str:<10} — {desc}")
            menu_item("0", "Back to regions")
            print()
            tz_choice = prompt("Select timezone")
            if tz_choice == "0":
                break
            try:
                abbr, utc_str, offset, desc = tzlist[int(tz_choice) - 1]
                label = f"{abbr} ({utc_str}) — {desc}"
                return label, offset
            except (ValueError, IndexError):
                error("Invalid selection.")
                continue

def push_workflow_file(token, username, repo_data, utc_hour, utc_min, min_c, max_c, local_hour, tz_short):
    import base64

    owner     = repo_data["owner"]["login"]
    repo_name = repo_data["name"]

    # Python script embedded as base64 to avoid YAML syntax issues
    python_script = r"""import os,sys,json,random,subprocess,time,requests,base64
from datetime import datetime,timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TOKEN=os.environ['GH_TOKEN']
MIN_C=int(os.environ.get('MIN_C',15))
MAX_C=int(os.environ.get('MAX_C',35))
REPO=os.environ.get('REPO_NAME','')

s=requests.Session()
retry=Retry(total=4,backoff_factor=1,status_forcelist=[429,500,502,503,504])
s.mount('https://',HTTPAdapter(max_retries=retry))
H={'Authorization':f'token {TOKEN}','Accept':'application/vnd.github.v3+json'}

user=s.get('https://api.github.com/user',headers=H,timeout=15).json()
username=user['login']
today=datetime.now()
ds=today.strftime('%Y-%m-%dT12:00:00+00:00')

print(f'Adding commits for today: {today.strftime("%Y-%m-%d")}')

# Clone existing repo
work='/tmp/rg'
subprocess.run(['rm','-rf',work])
auth_url=f'https://{username}:{TOKEN}@github.com/{username}/{REPO}.git'
r=subprocess.run(['git','clone',auth_url,work],capture_output=True,text=True)
if r.returncode!=0:
    # Repo empty, just init
    os.makedirs(work,exist_ok=True)
    subprocess.run(['git','-C',work,'init'])
    subprocess.run(['git','-C',work,'remote','add','origin',auth_url])

subprocess.run(['git','-C',work,'config','user.name',username])
subprocess.run(['git','-C',work,'config','user.email',f'{username}@users.noreply.github.com'])

# Commit only today's date N times
df=os.path.join(work,'data.json')
count=random.randint(MIN_C,MAX_C)
print(f'Creating {count} commits for {today.strftime("%Y-%m-%d")}...')
for i in range(count):
    open(df,'w').write(json.dumps({'d':ds,'i':i}))
    subprocess.run(['git','-C',work,'add','data.json'])
    e={**os.environ,'GIT_AUTHOR_DATE':ds,'GIT_COMMITTER_DATE':ds,'LANG':'C'}
    subprocess.run(['git','-C',work,'commit','-m',f'{ds}-{i}'],capture_output=True,env=e)

# Push
branch_check=subprocess.run(['git','-C',work,'branch','--show-current'],capture_output=True,text=True)
branch=branch_check.stdout.strip() or 'main'
subprocess.run(['git','-C',work,'branch','-M','main'])
r=subprocess.run(['git','-C',work,'push','origin','main'],capture_output=True,text=True)
if r.returncode==0:
    print(f'Done! {count} commits added for {today.strftime("%Y-%m-%d")}.')
else:
    # Try force push if first time
    r2=subprocess.run(['git','-C',work,'push','origin','main','--force'],capture_output=True,text=True)
    if r2.returncode==0:
        print(f'Done! {count} commits added for {today.strftime("%Y-%m-%d")}.')
    else:
        print('Push failed:',r2.stderr);sys.exit(1)
"""

    py_b64 = base64.b64encode(python_script.encode()).decode()

    def build_wf(wf_content_b64=""):
        return (
            "# RepGreen - Auto Contribution Graph Updater\n"
            f"# Runs daily at {local_hour:02d}:00 {tz_short}\n"
            "name: RepGreen Auto Update\n\n"
            "on:\n"
            "  schedule:\n"
            f"    - cron: '{utc_min} {utc_hour} * * *'\n"
            "  workflow_dispatch:\n\n"
            "jobs:\n"
            "  update-graph:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - name: Set up Python\n"
            "        uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.11'\n\n"
            "      - name: Install dependencies\n"
            "        run: pip install requests\n\n"
            "      - name: Run RepGreen\n"
            "        env:\n"
            "          GH_TOKEN: ${{ secrets.REPGREEN_TOKEN }}\n"
            "          REPO_NAME: ${{ github.event.repository.name }}\n"
            f"          MIN_C: '{min_c}'\n"
            f"          MAX_C: '{max_c}'\n"
            f"          PY_SCRIPT: '{py_b64}'\n"
            f"          WF_CONTENT: '{wf_content_b64}'\n"
            "        run: |\n"
            "          echo \"$PY_SCRIPT\" | base64 -d > /tmp/repgreen_run.py\n"
            "          python3 /tmp/repgreen_run.py\n"
        )

    # Build workflow, encode itself as WF_CONTENT so Python script can restore it after repo reset
    wf_draft    = build_wf("")
    wf_self_b64 = base64.b64encode(wf_draft.encode()).decode()
    wf          = build_wf(wf_self_b64)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    encoded = base64.b64encode(wf.encode()).decode()

    check = SESSION.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/contents/.github/workflows/repgreen.yml",
        headers=headers, timeout=10
    )
    payload = {"message": "Add RepGreen auto-update workflow", "content": encoded}
    if check.status_code == 200:
        payload["sha"] = check.json()["sha"]
        payload["message"] = "Update RepGreen workflow"

    r = SESSION.put(
        f"https://api.github.com/repos/{owner}/{repo_name}/contents/.github/workflows/repgreen.yml",
        headers=headers, json=payload, timeout=15
    )
    return r.status_code in (200, 201)

def menu_schedule(token, username):
    while True:
        banner()
        section("AUTO SCHEDULE  —  GitHub Actions")
        print(f"  {GR}Runs on GitHub servers every day — no computer needed, free forever.{R}")
        print()
        info("Mechanism : GitHub Actions (cron schedule)")
        info("Frequency : Every day at your chosen local time")
        info("Cost      : Free (GitHub Actions free tier)")
        print()
        menu_item(1, "Setup / Update GitHub Actions",  "  push workflow to repo")
        menu_item(2, "Remove GitHub Actions",          "  delete workflow from repo")
        menu_item(0, "Back to main menu")
        print()

        choice = prompt("Select option")

        if choice == "1":
            banner()

            repo_url, repo_data = select_repo(token, return_data=True)
            if not repo_url:
                continue

            owner     = repo_data["owner"]["login"]
            repo_name = repo_data["name"]

            # Select timezone — Region → Timezone (full world)
            info("Match your timezone with GitHub profile:")
            info("github.com/settings/appearance → Local time")
            print()
            tz_label, tz_offset = select_timezone()
            if tz_label is None:
                continue
            tz_short = tz_label.split("—")[0].strip()

            # Select hour
            section("SELECT SCHEDULE TIME")
            info(f"Timezone: {tz_label}")
            print()
            for h in [0, 6, 8, 9, 10, 12, 18, 20, 22]:
                menu_item(str(h), f"{h:02d}:00  local time")
            menu_item("c", "Custom hour")
            print()
            hour_input = prompt("Select hour or 'c' for custom")

            if hour_input.lower() == "c":
                try:
                    local_hour = int(prompt("Enter hour (0-23)"))
                    if not 0 <= local_hour <= 23:
                        raise ValueError
                except ValueError:
                    error("Invalid. Using 08:00.")
                    local_hour = 8
            else:
                try:
                    local_hour = int(hour_input)
                    if not 0 <= local_hour <= 23:
                        raise ValueError
                except ValueError:
                    error("Invalid. Using 08:00.")
                    local_hour = 8

            utc_hour = local_to_utc_hour(local_hour, tz_offset)

            # Commits per day
            section("COMMITS PER DAY")
            menu_item(1, "Default (min 15, max 35)")
            menu_item(2, "Light   (min 5,  max 10)")
            menu_item(3, "Medium  (min 20, max 30)")
            menu_item(4, "Heavy   (min 33, max 50)")
            menu_item(5, "Custom range")
            print()
            dc = prompt("Select option")
            if dc == "2":   min_c, max_c = 5, 10
            elif dc == "3": min_c, max_c = 20, 30
            elif dc == "4": min_c, max_c = 33, 50
            elif dc == "5":
                try:
                    min_c = int(prompt("Min commits per day"))
                    max_c = int(prompt("Max commits per day"))
                    if min_c < 1 or max_c < min_c:
                        warn("Invalid range. Using default.")
                        min_c, max_c = 15, 35
                except ValueError:
                    min_c, max_c = 15, 35
            else:
                min_c, max_c = 15, 35

            # Summary
            banner()
            section("SUMMARY")
            info(f"Repository  : {repo_data['full_name']}")
            info(f"Timezone    : {tz_label}")
            info(f"Schedule    : Every day at {local_hour:02d}:00 {tz_short}")
            info(f"UTC cron    : {utc_hour} * * * (= {local_hour:02d}:00 local)")
            info(f"Commits/day : {min_c} - {max_c}")
            print()
            confirm = prompt("Push workflow to repo? (y/n)")
            if confirm.lower() != "y":
                warn("Cancelled.")
                prompt("Press Enter to continue")
                continue

            section("PUSHING WORKFLOW")
            info("Uploading .github/workflows/repgreen.yml ...")
            ok = push_workflow_file(token, username, repo_data, utc_hour, 0, min_c, max_c, local_hour, tz_short)
            print()
            if ok:
                success("Workflow pushed successfully!")
                print()
                success(f"GitHub Actions will run every day at {local_hour:02d}:00 {tz_short}.")
                print()
                warn("REQUIRED — Add your token as GitHub Secret:")
                warn(f"  1. Go to  : https://github.com/{owner}/{repo_name}/settings/secrets/actions")
                warn(f"  2. Click  : 'New repository secret'")
                warn(f"  3. Name   : REPGREEN_TOKEN")
                warn(f"  4. Value  : your GitHub token (repo + delete_repo scope)")
                warn(f"  5. Click  : 'Add secret'")
                print()
                warn("To run manually right now:")
                warn(f"  https://github.com/{owner}/{repo_name}/actions")
                warn(f"  → RepGreen Auto Update → Run workflow")
            else:
                error("Failed to push workflow.")
                error("Make sure token has 'workflow' scope enabled.")
            print()
            prompt("Press Enter to continue")

        elif choice == "2":
            banner()
            repo_url, repo_data = select_repo(token, return_data=True)
            if not repo_url:
                continue
            owner     = repo_data["owner"]["login"]
            repo_name = repo_data["name"]

            section("REMOVE WORKFLOW")
            warn(f"Delete workflow from {owner}/{repo_name}?")
            confirm = prompt("Confirm (y/n)")
            if confirm.lower() != "y":
                warn("Cancelled.")
                prompt("Press Enter to continue")
                continue

            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            check = SESSION.get(
                f"https://api.github.com/repos/{owner}/{repo_name}/contents/.github/workflows/repgreen.yml",
                headers=headers, timeout=10
            )
            if check.status_code == 200:
                sha = check.json()["sha"]
                r = SESSION.delete(
                    f"https://api.github.com/repos/{owner}/{repo_name}/contents/.github/workflows/repgreen.yml",
                    headers=headers,
                    json={"message": "Remove RepGreen workflow", "sha": sha},
                    timeout=10
                )
                if r.status_code == 200:
                    success("Workflow removed.")
                else:
                    error("Failed to remove workflow.")
            else:
                warn("Workflow not found in repo.")
            print()
            prompt("Press Enter to continue")

        elif choice == "0":
            break


# ── Main Flow ──────────────────────────────────────────────────────────────────
def main():
    banner()

    # ── Token Input ──────────────────────────────────────────────────────────
    section("AUTHENTICATION")
    info("Generate token at: https://github.com/settings/tokens/new")
    info("Required scope  : repo + delete_repo")
    print()

    token = prompt("GitHub Personal Access Token")

    info("Validating token...")
    user = validate_token(token)
    if not user:
        error("Invalid token or connection failed. Please check and try again.")
        sys.exit(1)

    username  = user["login"]
    join_year = get_join_year(user)  # reuse already-fetched data, no extra API call
    success(f"Authenticated as  : {B}{username}{R}")
    if join_year:
        success(f"Account created in: {B}{join_year}{R}")

    # ── Main Menu ─────────────────────────────────────────────────────────────
    while True:
        banner()
        section("MAIN MENU")
        menu_item(1, "Fill contribution graph",  "  create commits to green up your profile")
        menu_item(2, "Clear contribution graph", "  wipe all commits from a repository")
        menu_item(3, "Auto Schedule",            "  auto-update graph every day")
        menu_item(4, "Exit")
        print()

        action = prompt("Select option")

        # ── FILL ─────────────────────────────────────────────────────────────
        if action == "1":
            banner()
            repo_url, repo_data = select_repo(token, return_data=True)
            if not repo_url:
                continue

            # Year
            section("SELECT YEAR")
            current_year = datetime.now().year
            if join_year:
                info(f"Account created in {join_year} — years shown from that point onward")
            print()
            year_range = list(range(current_year, (join_year or current_year - 5) - 1, -1))
            for i, y in enumerate(year_range):
                label = f"{y}  {GR}(account created){R}" if y == join_year else str(y)
                menu_item(i + 1, label)
            print()
            year_input = prompt("Select number or type year directly")
            try:
                val = int(year_input)
                if 1 <= val <= len(year_range):
                    year = year_range[val - 1]
                else:
                    year = val
            except ValueError:
                error("Invalid input.")
                continue

            if join_year and year < join_year:
                warn(f"Year {year} is before account creation ({join_year}). Graph may be empty.")
            elif year > current_year:
                warn(f"Year {year} is in the future. Only past/today dates will be committed.")

            # Mode
            banner()
            section("SELECT MODE")
            menu_item(1, "Full year",             "  fill ALL days Jan-Dec up to TODAY")
            menu_item(2, "Full year (force)",     "  fill Jan 1 to Dec 31 including FUTURE dates")
            menu_item(3, "Specific month",        "  fill only a chosen month")
            menu_item(4, "Specific weekday",      "  fill every occurrence of a weekday")
            print()
            mode_choice = prompt("Select mode")

            bulan, hari = None, None
            force_full  = False

            if mode_choice == "1":
                mode = "full"
            elif mode_choice == "2":
                mode       = "full"
                force_full = True
            elif mode_choice == "3":
                mode = "month"
                section("SELECT MONTH")
                for k, v in MONTHS.items():
                    menu_item(k, v)
                print()
                bulan = int(prompt("Month number (1-12)"))
            elif mode_choice == "4":
                mode = "day"
                section("SELECT WEEKDAY")
                for k, v in DAYS.items():
                    menu_item(k, v)
                print()
                hari = int(prompt("Weekday number (0=Monday, 6=Sunday)"))
            else:
                error("Invalid mode.")
                continue

            # Warn about future commits
            if force_full:
                print()
                warn("Force Full: commits will be dated into FUTURE dates (Mar-Dec etc).")
                warn("GitHub WILL display them immediately on your graph — full green!")
                print()

            # Gap percentage (only for month/day modes)
            if mode != "full":
                section("NATURAL GAPS")
                info("Percentage of days to leave empty (makes graph look natural)")
                info("Recommended: 10-25")
                skip_input = prompt("Skip percentage (default 15)")
                try:
                    skip_pct = int(skip_input) if skip_input else 15
                except ValueError:
                    skip_pct = 15
            else:
                skip_pct = 0  # Full mode = no gaps, semua hari diisi

            # Commits per day
            section("COMMITS PER DAY")
            menu_item(1, "Default (min 15, max 35)")
            menu_item(2, "Light   (min 5,  max 10)")
            menu_item(3, "Medium  (min 20, max 30)")
            menu_item(4, "Heavy   (min 33, max 50)")
            menu_item(5, "Custom range")
            print()
            density_choice = prompt("Select option")

            if density_choice == "2":
                min_c, max_c = 5, 10
            elif density_choice == "3":
                min_c, max_c = 20, 30
            elif density_choice == "4":
                min_c, max_c = 33, 50
            elif density_choice == "5":
                try:
                    min_c = int(prompt("Minimum commits per day"))
                    max_c = int(prompt("Maximum commits per day"))
                    if min_c < 1 or max_c < min_c:
                        warn("Invalid range. Using default.")
                        min_c, max_c = 15, 35
                except ValueError:
                    min_c, max_c = 15, 35
            else:
                min_c, max_c = 15, 35

            # Summary
            banner()
            section("SUMMARY")
            info(f"Repository : {repo_url}")
            info(f"Year       : {year}")
            info(f"Mode       : {mode}" + (" [FORCE FULL YEAR]" if force_full else "") + (f" / {MONTHS.get(bulan,'')}" if bulan else "") + (f" / {DAYS.get(hari,'')}" if hari is not None else ""))
            info(f"Skip days  : {skip_pct}%")
            info(f"Commits/day: {min_c} - {max_c}")
            print()

            confirm = prompt("Proceed? (y/n)")
            if confirm.lower() != "y":
                warn("Cancelled.")
                continue

            info("Generating dates...")
            dates = generate_dates(mode, year, min_c, max_c, bulan, hari, skip_pct, force_full=force_full)
            info(f"Total commits: {len(dates)}")

            result = make_commits(repo_url, token, username, dates, repo_data=repo_data)

            if result:
                print()
                section("DONE")
                success(f"Contribution graph updated for {year}.")
                warn("Note: Enable 'Private contributions' in your GitHub profile settings")
                warn("      if you used a private repository.")
                warn(f"      https://github.com/{username}?tab=overview")
            print()
            prompt("Press Enter to return to menu")

        # ── CLEAR ─────────────────────────────────────────────────────────────
        elif action == "2":
            banner()
            repo_url, repo_data = select_repo(token, return_data=True)
            if not repo_url or not repo_data:
                continue

            banner()
            section("CLEAR CONFIRMATION")
            warn("The following repository will be DELETED and RECREATED from scratch:")
            print(f"  {W}{repo_data['full_name']}{R}  {GR}({'private' if repo_data['private'] else 'public'}){R}")
            print()
            warn("Mechanism: DELETE repo via API → CREATE new repo (same name)")
            warn("This ensures all commits, branches, and history are completely wiped.")
            warn("MAKE SURE your token has scope: repo + delete_repo")
            print()
            confirm = prompt("Type 'DELETE' to confirm")

            if confirm != "DELETE":
                warn("Cancelled.")
                prompt("Press Enter to return to menu")
                continue

            result = clear_commits(repo_data, token, username)
            if result:
                section("DONE")
                success("The repository has been deleted and recreated — 100% clean.")
                warn("Repo is now empty. Ready to fill with Fill contribution graph.")
            print()
            prompt("Press Enter to return to menu")

        elif action == "3":
            menu_schedule(token, username)

        elif action == "4":
            banner()
            info("Goodbye.")
            print()
            sys.exit(0)

        else:
            error("Invalid option.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{GR}  Interrupted.{R}\n")
        sys.exit(0)
