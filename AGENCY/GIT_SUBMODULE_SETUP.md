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

## 3. 🔄 How to Update Templates
1.  **Pull changes in the submodule**:
    ```bash
    cd AGENCY_TEMPLATE
    # Fetch latest changes
    git fetch
    git merge origin/main
    ```

2.  **Commit the updated reference in the main repo**:
    ```bash
    cd ..
    git add AGENCY_TEMPLATE
    git commit -m "chore: update agency templates to latest version"
    ```

## 4. 📝 Best Practices
*   **Do not modify submodule files directly** inside the consuming repo unless you intend to push changes back to the source.
*   **Always verify** that the submodule is pointing to the correct commit/tag for your project's stability.
