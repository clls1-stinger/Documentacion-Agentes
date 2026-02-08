---
type: decision_record
author: [AGENT_ID]
date: 2024-05-23
context: Creating a scalable, performant storage architecture for media and system usage.
decision: Adopt a Unified Btrfs Pool and the '70/30 Rule' for caching.
status: ACCEPTED
---

# 🧠 DECISION RECORD: STORAGE POLICY & ARCHITECTURE (THE JEWELS)

> **Meta-Cognition Principle**: Capture the *reasoning* so future agents understand the *intent*.

## 1. ❓ CONTEXT (THE PROBLEM)
*   **Situation**: We need to manage storage for system files, media content (Jellyfin), and downloads without rigid partitions that waste space.
*   **Constraints**: High-speed NVMe storage needs to be preserved (SLC Caching). Bandwidth limitations for streaming (Morelia).
*   **Assumption**: Btrfs allows for flexible subvolumes and easy expansion.

## 2. 💡 OPTIONS CONSIDERED
*   **Option A**: **Unified Btrfs Pool** (Chosen)
    *   **Pros**: Zero fragmentation. Share 1TB freely between OS and Data. Easy to expand.
    *   **Cons**: Btrfs maintenance (balance, scrub).
*   **Option B**: **Traditional Partitioning**
    *   **Pros**: Isolation.
    *   **Cons**: Rigid boundaries. Resizing is risky and difficult.

## 3. ✅ THE DECISION
*   **Chosen Option**: **Option A (Unified Btrfs)**.
*   **Rationale**: Flexibility is key. We treat storage as a pool, not a set of drawers.
*   **Key Policies**:
    1.  **The 70/30 Rule**: Keep 30% of SSD free for SLC Caching performance.
        *   **Allocation**: Media Cache (400GB), System (200GB), Safety Buffer (~300GB).
    2.  **Transcoding vs. Pre-conversion**: Prioritize "Direct Play". Use Jellyfin "Versions" to pre-convert high-bitrate content for lower bandwidth clients, storing these versions permanently.
    3.  **Scalability**: New drives are added to the pool (`btrfs device add`) without partitioning.

## 4. 🔮 PREDICTED CONSEQUENCES (FUTURE)
*   **Positive**: **Efficiency**. Optimized for YTS-quality content (~285 hours capacity). "Transcode once, Stream many".
*   **Negative**: If we upgrade to 4K Remux (80 Mbps), capacity will be insufficient (~11 hours).

## 5. 🔄 REVIEW TRIGGER
*   **When to reconsider**: If moving to 4K Remux content or if Btrfs stability issues arise.
