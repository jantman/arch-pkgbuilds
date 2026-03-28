# Arch Package Repo Overhaul: Options Analysis

Current setup: custom `rebuild.py` + `aurget.sh` scripts that clone AUR PKGBUILDs, build locally, manage a repo database via `repo-add`, and sync to S3 via `update_sync.sh`. ~80 packages.

## Top 10 Options

### 1. aurutils + rebuild-detector (Recommended for local builds)

- **URL:** https://github.com/aurutils/aurutils
- **Type:** Local CLI toolset (modular shell scripts)
- **How it works:** Collection of scripts (`aur sync`, `aur build`, `aur fetch`, etc.) that manage AUR packages through a local pacman repo. Builds in clean chroot via `makechrootpkg`. `aur sync --upgrades` checks for AUR updates. Pair with `rebuild-detector` (`checkrebuild`) to detect packages needing rebuilds after shared library or interpreter updates.
- **Puppet integration:** Excellent. Fully CLI/scriptable. Puppet manages: package list file, `pacman.conf` repo entry, build chroot setup, systemd timer units for scheduled rebuilds. The `puppet-pacman` module can manage custom repo entries.
- **Status:** Very actively maintained. v20.5.8 (Feb 2026). 1,000+ stars, 4,384 commits.
- **Pros:**
  - Most mature and well-documented tool in this space
  - Modular Unix philosophy; each script does one thing
  - Clean chroot builds by default
  - Extremely automation-friendly
  - Active community (#aurutils on Libera Chat)
- **Cons:**
  - Requires manual setup of local repo, `pacman.conf`, and build chroot
  - No built-in scheduler (add your own cron/systemd timer)
  - Learning curve with multiple sub-commands
  - Needs `rebuild-detector` as a companion for library-triggered rebuilds

### 2. aurto

- **URL:** https://github.com/alexheretic/aurto
- **Type:** Local service (wrapper around aurutils)
- **How it works:** Simplified interface (`aurto add/remove`) with built-in automatic updates. Creates and manages its own `aurto` pacman repo. Auto-updates hourly, rebuilds VCS packages daily, auto-removes packages with untrusted maintainers.
- **Puppet integration:** Moderate. Puppet can manage installation, enable/start systemd timers, manage trust list. Opinionated about repo name (`aurto`) and config structure.
- **Status:** Actively maintained. v0.14.5 (March 2026). 159 stars.
- **Pros:**
  - Nearly turnkey setup
  - Built-in hourly auto-updates and daily VCS rebuilds
  - Maintainer trust system
  - Clean chroot builds
  - Docker support for non-Arch build hosts
- **Cons:**
  - Less flexible than raw aurutils (opinionated defaults)
  - Harder to customize repo name/location for existing S3 sync workflow
  - Smaller community

### 3. paru with LocalRepo

- **URL:** https://github.com/Morganamilo/paru
- **Type:** Local CLI (AUR helper with local repo feature)
- **How it works:** Full AUR helper (yay successor) with a `LocalRepo` feature since v2.0. Configure a local repo in `pacman.conf` and `paru.conf`; paru builds into that repo. `paru -Sua --noconfirm` upgrades all AUR packages.
- **Puppet integration:** Moderate. Manage `paru.conf`, `pacman.conf`, and timer units via Puppet. Needs `--noconfirm` and other flags for non-interactive use.
- **Status:** Very actively maintained. v2.1.0 (July 2025). 8,500+ stars. Rust.
- **Pros:**
  - Minimal extra config if you already use paru
  - Most popular AUR helper; huge community
  - Supports custom PKGBUILD repos with priority over AUR
- **Cons:**
  - LocalRepo is a secondary feature, less documented for repo management
  - Interactive by default; needs flags for automation
  - No clean chroot by default (extra flags required)
  - No built-in dependency-rebuild detection

### 4. LizardByte/pacman-repo pattern (GitHub Actions + Releases)

- **URL:** https://github.com/LizardByte/pacman-repo
- **Type:** GitHub Actions CI with GitHub Releases hosting
- **How it works:** PKGBUILDs in repo directories. GitHub Actions workflow rebuilds all packages daily on a schedule, publishes to GitHub Releases (stable + beta channels). Users point `pacman.conf` at the release download URL.
- **Puppet integration:** Client-side only (manage `pacman.conf` entry and GPG key). Build pipeline is entirely in GitHub Actions.
- **Status:** Active. 88 stars. MIT license.
- **Pros:**
  - No server infrastructure needed
  - Daily automated rebuilds
  - GitHub Releases CDN is fast and pacman-friendly
  - Good template to fork and customize
  - Free for public repos (unlimited Actions minutes)
- **Cons:**
  - Daily rebuilds of all packages consume CI minutes (2,000 min/month free for private repos)
  - No selective AUR update detection (rebuilds everything)
  - GitHub Releases storage limits
  - Replaces S3 hosting with GitHub hosting (migration effort)

### 5. Custom GitHub Actions workflow (DIY with kopp/build-aur-packages)

- **URL:** https://github.com/kopp/build-aur-packages (reusable Action)
- **Type:** GitHub Actions building block
- **How it works:** A reusable GitHub Action that builds AUR packages in a Docker container with aurutils. Creates a package database. You add your own publishing step (upload to GitHub Releases, S3, etc.).
- **Puppet integration:** Client-side only. Could keep existing S3 sync by adding an upload step.
- **Status:** Modest adoption. 9 stars, 42 commits.
- **Pros:**
  - Uses aurutils under the hood
  - Flexible; you control the publishing step
  - Could publish to your existing S3 bucket, preserving current `pacman.conf` on all machines
  - Can schedule with cron triggers
- **Cons:**
  - Building block, not a complete solution
  - Modest community; uncertain long-term maintenance
  - Requires manual dependency declaration for missing deps
  - Need to build the workflow around it yourself

### 6. Chaotic-AUR Template / Infrastructure

- **URL:** https://github.com/chaotic-aur/pkgbuilds (template repo)
- **Builder:** https://gitlab.com/garuda-linux/tools/chaotic-manager
- **Type:** CI + Redis + Docker build infrastructure
- **How it works:** Full build infrastructure used by Chaotic-AUR (serves thousands of users). GitHub/GitLab CI for triggers, Redis queue for scheduling, Docker containers for builds. Adding a PKGBUILD folder and committing triggers automatic builds. Handles dependency trees automatically.
- **Puppet integration:** Complex. Infrastructure involves Redis, Docker, CI runners. Puppet could manage server components but significant architectural overhead.
- **Status:** Actively maintained by Garuda Linux team. Battle-tested at scale.
- **Pros:**
  - Proven at massive scale
  - Fully automated pipeline with dependency resolution
  - Designed to be forked as a template
  - Can auto-pull PKGBUILDs from AUR
- **Cons:**
  - Massive overkill for ~80 personal packages
  - Requires dedicated infrastructure (Redis, Docker, CI runners)
  - Complex setup; sparse documentation for personal use
  - Steep learning curve

### 7. arch-repo-manager (Martchus)

- **URL:** https://github.com/Martchus/arch-repo-manager
- **Type:** Local daemon with HTTP API and web UI
- **How it works:** C++ toolkit with a daemon providing an HTTP API and web UI for managing custom repos. Supports building from local PKGBUILDs or AUR. Has AUR update checking and dependency resolution. Builds triggered via web UI or API.
- **Puppet integration:** Possible via HTTP API, but experimental and complex to deploy.
- **Status:** Active development. 25 stars, 564 commits. Author warns: "no security review."
- **Pros:**
  - Web UI with live build log streaming
  - HTTP API for programmatic access
  - AUR update detection and dependency resolution
- **Cons:**
  - Experimental; not production-ready
  - Heavy C++ dependencies (Boost, LMDB, liburing)
  - No regular releases; no security audit
  - Small community

### 8. djpohly/PKGBUILD pattern (GitHub Actions, simpler)

- **URL:** https://github.com/djpohly/PKGBUILD
- **Type:** GitHub Actions + GitHub Releases
- **How it works:** Simpler variant of option 4. Builds on push, uploads to a GitHub Release named "repository". Good minimal template.
- **Puppet integration:** Client-side only.
- **Status:** Active personal project. Good fork template.
- **Pros:**
  - Simplest GitHub Actions approach
  - Easy to understand and fork
  - Free hosting via GitHub Releases
- **Cons:**
  - Builds on push only (no scheduled rebuilds without adding cron)
  - No AUR update detection
  - Manual package signing setup
  - GitHub storage limits

### 9. GitHub Pages hosting + local builds

- **Reference:** https://www.sainnhe.dev/post/create-personal-arch-linux-package-repository/
- **Type:** Hybrid (local builds, GitHub Pages hosting)
- **How it works:** Build and sign packages locally with `makepkg --sign`, add to repo with `repo-add --verify --sign`, push repo directory to GitHub, enable GitHub Pages. Replaces S3 with free GitHub Pages hosting.
- **Puppet integration:** Client-side (manage `pacman.conf` and GPG key import). Build side stays local/manual.
- **Pros:**
  - Free hosting
  - Simple concept
  - Could keep existing build scripts, just change the sync target
- **Cons:**
  - Git repo bloats quickly with binary packages (~1 GB soft limit)
  - No automation for builds or update checking
  - Essentially just swapping S3 for a worse hosting option

### 10. DIY: makechrootpkg + repo-add + systemd timers (modernized current approach)

- **Reference:** https://www.joram.io/blog/custom-arch-linux-package-repository/
- **Type:** Local, using only standard Arch tools
- **How it works:** Modernize your existing `rebuild.py` approach: use `makechrootpkg` for clean chroot builds, `repo-add` for repo management, add `rebuild-detector` for library-triggered rebuilds, add systemd timers for scheduled runs, keep S3 sync. Essentially refactoring your current scripts rather than replacing them.
- **Puppet integration:** Excellent. Everything is files, scripts, and systemd units.
- **Pros:**
  - Minimal change from current workflow
  - No new tools to learn
  - Full control over every aspect
  - Keep existing S3 hosting
- **Cons:**
  - Maintains custom code (your scripts)
  - No community support for your custom tooling
  - Miss out on features that aurutils provides (dependency resolution, AUR interaction, etc.)

---

## Comparison Matrix

| # | Option | Auto Updates | Auto Rebuilds | Puppet | Complexity | Infra Change | Maintained |
|---|--------|-------------|---------------|--------|------------|-------------|------------|
| 1 | aurutils + rebuild-detector | Via timer | Via rebuild-detector | Excellent | Medium | Minimal | Very active |
| 2 | aurto | Built-in hourly | Built-in | Moderate | Low | Minimal | Active |
| 3 | paru LocalRepo | Via timer | Manual | Moderate | Low | Minimal | Very active |
| 4 | LizardByte pattern | Daily schedule | Daily | Client only | Low | Replace S3 | Active |
| 5 | DIY GH Actions + kopp | Schedulable | Schedulable | Client only | Medium | Optional | Modest |
| 6 | Chaotic-AUR template | Automatic | Automatic | Complex | Very High | Full replace | Active |
| 7 | arch-repo-manager | Detection only | Manual (API) | Low | High | Minimal | Experimental |
| 8 | djpohly pattern | On push | Schedulable | Client only | Low | Replace S3 | Template |
| 9 | GitHub Pages + local | None | None | Client only | Low | Replace S3 | N/A |
| 10 | Modernize current scripts | Via timer | Via rebuild-detector | Excellent | Medium | None | Self-maintained |

## Key Constraints

- **Hosting:** S3 must remain the repo host (rules out GitHub Releases/Pages-only approaches without an S3 upload step)
- **Fleet:** 3 x amd64 Arch machines kept in perfect sync (same packages)
- **Resources:** One machine is memory/CPU constrained, making per-machine AUR builds painful or infeasible

These constraints strongly favor a **build-once, install-everywhere** model: packages are built on one capable machine (or in CI), published to S3, and all 3 machines install from the shared repo via `pacman -Syu`. This is already how the current setup works and should be preserved.

## Recommendation

### Best overall: aurutils + rebuild-detector on a dedicated build machine (option 1)

Run aurutils on your most capable machine. `aur sync --upgrades` checks AUR for updates, builds in a clean chroot, and adds to the local repo. Pair with `rebuild-detector` to catch library-triggered rebuilds. Keep your existing S3 sync (`update_sync.sh` or equivalent). All 3 machines point `pacman.conf` at the S3 repo and just run `pacman -Syu` — the constrained machine never builds anything.

Puppet manages: the `pacman.conf` repo entry on all 3 machines, the aurutils package list and systemd timer on the build machine, and the S3 sync script/credentials.

This is the most natural evolution of your current workflow — replacing custom scripts with community-maintained tooling while keeping S3 hosting and the build-once model intact.

### Runner-up: GitHub Actions + S3 upload (option 5, customized)

Build a GitHub Actions workflow (using `kopp/build-aur-packages` or a custom Arch Docker container) that builds all packages on push or a daily schedule, then uploads to your S3 bucket via `aws s3 sync`. No machine builds anything — builds happen on GitHub runners for free (public repos get unlimited minutes).

This fully offloads builds from all 3 machines and removes the need for a "build machine" entirely. The tradeoff is that debugging build failures happens in CI logs rather than locally, and you lose the ability to do quick ad-hoc test builds.

### If you want turnkey: aurto on the build machine (option 2)

Same build-once model as option 1 but with less setup. aurto handles hourly AUR update checks and VCS rebuilds automatically. The main gap is that aurto manages its own repo structure, so you'd need a wrapper to sync its repo directory to S3 rather than using aurto's built-in local repo directly.

### Options to deprioritize

- **paru LocalRepo (3):** Designed for single-machine use; no built-in story for syncing to a shared repo
- **Chaotic-AUR (6):** Massive infrastructure overkill for 3 machines
- **arch-repo-manager (7):** Experimental; not production-ready
- **GitHub Pages/Releases-only (8, 9):** Don't use S3
- **Modernize scripts (10):** Viable but maintains custom code burden when aurutils already solves the same problems
