# GitHub Actions AUR Repo: Process Design

## Overview

Build AUR packages via GitHub Actions, publish to S3. Three Arch machines consume the repo via `pacman -Syu` — none of them build packages.

## Repo Structure

```
.
├── .github/
│   └── workflows/
│       ├── build.yml          # Build and publish on push to master
│       ├── check-updates.yml  # Scheduled AUR update check
│       └── full-rebuild.yml   # Scheduled full rebuild
├── packages/
│   ├── google-chrome/
│   │   ├── PKGBUILD
│   │   └── .SRCINFO
│   ├── spotify/
│   │   ├── PKGBUILD
│   │   └── .SRCINFO
│   └── ...
├── scripts/
│   ├── check-aur-updates.sh   # Compare local vs AUR versions
│   ├── build-package.sh       # Build a single package in clean chroot
│   └── sync-repo.sh           # repo-add + aws s3 sync
└── repo/                      # (gitignored) local repo DB during CI builds
```

## Inter-Package Dependencies

Some packages in this repo depend on other packages in this repo. All builds must respect this ordering.

**Known dependency chains:**
- `levmar` depends on `f2c`
- `libfprint-2-tod1-xps9300-bin` depends on `libfprint-tod`
- `perl-http-server-simple-authen` depends on `perl-authen-simple`
- `fusioninventory-agent` depends on: `perl-http-server-simple-authen`, `perl-io-capture`, `perl-proc-daemon`, `perl-xml-treepp`, `perl-universal-require` (and transitively on `perl-authen-simple`)

**Build ordering approach:**
1. Parse `depends` and `makedepends` from each package's PKGBUILD or `.SRCINFO`
2. Cross-reference against the list of packages in this repo to identify internal dependencies
3. Topological sort to determine build order
4. Build in order; each built package is added to a local repo (`repo-add`) so that subsequent packages can resolve it as a dependency during their build
5. If a dependency fails to build, skip all packages that depend on it (and report them as skipped)

The build container must be configured so that the local repo (containing already-built packages from this repo) is available as a pacman repo during the build. This way, when building `levmar`, the previously-built `f2c` is installable via pacman.

## VCS Packages (-git)

4 packages track upstream git repos rather than AUR version numbers:
- `lego-git`
- `sbupdate-git`
- `hotshots-git`
- `network-ups-tools-git`

These won't be caught by AUR version checks (AUR version stays the same; the upstream git repo changes). They should be included in the weekly full rebuild, which will pick up any upstream changes via `makepkg`'s `pkgver()` function.

## Workflows

### 1. Build on Push (build.yml)

**Trigger:** Push to `master`

**Steps:**
1. Determine which `packages/*/PKGBUILD` files changed in the push (via `git diff`)
2. Compute build order for changed packages (topological sort based on inter-package dependencies). If a changed package is a dependency of another package in the repo, also rebuild the dependent (even if it didn't change) to be safe
3. Pull existing repo database and packages from S3
4. For each package in build order, build in an Arch Docker container. After each successful build, `repo-add` it to the local repo so subsequent builds can depend on it
5. On build failure: log the error, open a GitHub issue, skip dependent packages, continue building independent packages. The workflow should exit with a failure status if any package failed
6. `aws s3 sync` the updated packages + database to S3

**Notes:**
- Only rebuilds packages that actually changed (plus their dependents), keeping CI time minimal
- This is the primary build path after merging update PRs

### 2. AUR Update Check (check-updates.yml)

**Trigger:** Scheduled (daily, e.g. 06:00 UTC)

**Steps:**
1. For each package in `packages/`, parse `.SRCINFO` for current version
2. Query AUR RPC API (`https://aur.archlinux.org/rpc/v5/info?arg[]=pkg1&arg[]=pkg2`) for latest versions
3. For each package with a newer AUR version:
   a. Clone the updated PKGBUILD from AUR
   b. Commit to a branch `aur-updates/<date>`
   c. Open a PR with the list of updated packages
4. If no updates found, do nothing

**PR format:**
```
Title: AUR updates 2026-03-28

Body:
## Updated packages
- google-chrome: 130.0.1 → 131.0.0
- spotify: 1.2.30 → 1.2.31

## Review checklist
- [ ] Check for maintainer changes
- [ ] Review PKGBUILD diffs for unexpected changes
```

**Notes:**
- Single daily PR with all updates batched together, not one PR per package
- Merging the PR triggers the build workflow (workflow 1)
- Gives you a chance to review PKGBUILD changes before they build (security)

### 3. Full Rebuild (full-rebuild.yml)

**Trigger:** Weekly schedule (e.g. Sunday 04:00 UTC) + manual dispatch

**Steps:**
1. Pull existing repo database from S3
2. Compute full build order (topological sort of all packages)
3. Build all packages in order in a clean Arch container; after each build, `repo-add` to local repo
4. On build failure: log the error, open a GitHub issue, skip dependent packages, continue with independent packages
5. `aws s3 sync` to S3, removing any old package versions (`--delete` or explicit cleanup)

**Notes:**
- Catches library-triggered rebuilds (new glibc, openssl, python, etc.) since the container always has the latest Arch packages
- Also rebuilds VCS packages (`*-git`), picking up upstream changes
- Weekly cadence means at most ~7 days of staleness after an Arch library update

---

## Library Rebuild Strategy: Options

When upstream Arch packages update (new glibc, openssl, python, Qt, etc.), some AUR packages may need rebuilding even though their PKGBUILDs haven't changed. On a local machine, `rebuild-detector` handles this by inspecting installed binaries with `ldd`. In CI, we need a different approach.

### Option A: Scheduled Full Rebuild (Simple)

Rebuild all ~80 packages on a fixed schedule (e.g. weekly).

- **Pros:** Dead simple. Catches everything. No dependency tracking logic.
- **Cons:** Wastes CI time rebuilding packages that don't need it. With ~80 packages, a full rebuild might take 30-90 minutes depending on package complexity.
- **CI cost:** Free for public repos (unlimited Actions minutes). ~4-8 hours/month of compute.

### Option B: Detect Arch Repo Changes, Then Full Rebuild

Monitor Arch repos for updates to a curated list of "trigger" packages (glibc, openssl, python, qt5-base, qt6-base, electron, etc.). When any trigger package updates, run a full rebuild.

- **Implementation:** A scheduled workflow checks current versions of trigger packages (via `pacman -Sy` in the container or the Arch Linux API) against a cached version list from the last build. If any changed, trigger a full rebuild.
- **Pros:** Only rebuilds when actually needed. Reduces unnecessary CI runs.
- **Cons:** Requires maintaining a trigger package list. May miss indirect dependencies not in the list. More complex logic.

### Option C: Per-Package Dependency Tracking

For each package, record its build-time dependency versions in an artifact. On each scheduled run, compare current Arch repo versions against recorded versions. Only rebuild packages whose dependencies changed.

- **Implementation:** After building, save `pacman -Q` output for each package's build chroot. On next run, diff against current versions. Rebuild only packages with changed deps.
- **Pros:** Most efficient. Only rebuilds what's needed. Targeted.
- **Cons:** Most complex to implement. Requires storing and comparing per-package dependency snapshots. Edge cases around transitive dependencies.

### Option D: Hybrid — Weekly Full Rebuild + Trigger-Based Rebuild

Combine options A and B: run a full rebuild weekly as a safety net, but also trigger rebuilds when known critical packages (glibc, python, openssl) update.

- **Pros:** Simple weekly cadence catches everything. Trigger-based rebuilds catch critical changes faster (within a day instead of up to a week).
- **Cons:** Slightly more CI usage than pure trigger-based. Still requires a trigger list.

### Option E: Don't Rebuild Proactively — Let Users Report Breakage

Skip automated library rebuilds entirely. If a package breaks due to a library update, notice it when `pacman -Syu` fails or a program crashes, then manually trigger a rebuild.

- **Pros:** Zero CI overhead for rebuilds. Zero complexity.
- **Cons:** Packages can be broken for days before you notice. Broken packages may block `pacman -Syu` entirely if there are dependency conflicts. Not great when all 3 machines need to stay in sync.

---

## Resolved Decisions

- **Package signing:** Not required
- **Build failures:** Continue building independent packages, skip dependents, open a GitHub issue, fail the workflow
- **VCS packages:** Rebuilt during weekly full rebuild (catches upstream git changes)
- **Library rebuilds:** Weekly full rebuild (Option A/D hybrid — simple, catches everything, free CI minutes on public repo)

## Open Questions

1. **S3 bucket structure:** Keep current structure (`current/`) or change?
2. **Package removal:** What's the process for dropping a package? Delete the directory and push — should the workflow detect removed packages and clean them from S3 + repo DB?
3. **Migration path:** How to transition? Options: (a) do one full build in CI to populate S3 from scratch, (b) keep existing S3 packages and let CI builds gradually replace them, (c) do a final local build, sync to S3, then switch to CI going forward
4. **Docker base image:** Use an existing Arch Docker image (e.g. `archlinux:base-devel`) or build a custom one with pre-installed tooling?
5. **S3 credentials:** How to provide AWS credentials to GitHub Actions? Options: OIDC federation (no long-lived keys), or IAM user access keys as GitHub secrets
6. **Repo database format:** Currently `jantman.db.tar.gz`. Keep this name or change?
7. **Concurrency:** Should packages without inter-dependencies be built in parallel (matrix strategy) for speed, or sequentially for simplicity?
