# 📦 GIT SUBMODULE SETUP

> **Purpose**: This guide explains how to use the `AGENCY/4_TEMPLATES` (or the entire `AGENCY` structure) as a Git Submodule across multiple repositories to maintain consistency.

## 1. 📂 Why Use Submodules?
*   **Consistency**: Ensure all repositories use the exact same version of the `AGENCY` templates.
*   **Upgradability**: Update templates in one place and propagate changes everywhere.

## 2. 🛠️ How to Add This Repo as a Submodule
To add this repository's `AGENCY` folder (or specific parts) to another repo:

1.  **Navigate to the target repo**:
    ```bash
    cd path/to/target-repo
    ```

2.  **Add the submodule**:
    ```bash
    git submodule add <URL_TO_THIS_REPO> AGENCY_TEMPLATE
    ```

3.  **Initialize and update**:
    ```bash
    git submodule init
    git submodule update
    ```

## 3. 🔄 AUTOMATIC SYNCHRONIZATION (The "One Fetch" Rule)
To ensure that fetching the parent repository **always** updates the `AGENCY` submodule automatically, configure your git environment as follows:

### Option A: Per-Repository Configuration (Recommended)
Run this command inside your repository to make `git pull` automatically update submodules:

```bash
git config submodule.recurse true
```

Now, when you run:
```bash
git pull
```
Git will automatically fetch and update the `AGENCY_TEMPLATE` folder to the commit specified by the parent repo.

### Option B: Global Configuration
To make this the default behavior for *all* your repositories:

```bash
git config --global submodule.recurse true
```

### Option C: Manual "One-Shot" Update
If you don't want to change the config, use this flag every time you pull:

```bash
git pull --recurse-submodules
```

## 4. 📝 Best Practices
*   **Do not modify submodule files directly** inside the consuming repo unless you intend to push changes back to the source.
*   **Always verify** that the submodule is pointing to the correct commit/tag for your project's stability.
