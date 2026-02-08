# 💎 STORAGE POLICY & ARCHITECTURE (THE JEWELS)

> **Directive**: This document preserves the "Infallible" storage decisions made during the initial setup phase. These are architectural jewels that must be respected in all future scaling.

## 1. 🧱 THE UNIFIED BTRFS PRINCIPLE
We have unified the M.2 NVMe partitions (formerly Windows and Linux) into a single Btrfs multi-device pool. 

*   **Logic**: Zero fragmentation. Instead of rigid partitions, we use subvolumes or logical folder structures.
*   **The Jewel**: Total flexibility. The system and the user share 1TB of high-speed space without needing to resize partitions ever again.

## 2. ⚡ CACHING & PERFORMANCE STRATEGY
For a 1TB high-speed NVMe (PUSKILL), we follow the **70/30 Rule** to preserve SSD health and performance (SLC Caching).

| Purpose | Allocation (Recommended) | Priority |
| :--- | :--- | :--- |
| **Media Cache** | 400 GB | High (Arrs/Transcoding) |
| **System/Home** | 200 GB | Critical (Daily Ops) |
| **Safety Buffer** | ~300 GB | Lifecycle (Leave Empty) |

## 3. 📈 SCALABILITY PATH
When a new M.2 or SATA SSD is added to the system:
1.  **Do not partition**.
2.  **Add to pool**: Use `btrfs device add` to expand the existing volume.
3.  **Balance**: Run `btrfs balance` to redistribute data and maintain speed.

## 4. 🎞️ MEDIA BITRATE ANALYSIS (YTS BASELINE)
We analyzed the existing collection (`/mnt/ErrE/Cine/`) to calibrate our caching needs.

*   **Sample Size**: 218 movies.
*   **Average Bitrate**: **3.13 Mbps** (~1.4 GB/hr).
*   **Efficiency Metric**: Our current 400GB Cache can hold approximately **285 hours** (or ~140 movies) of YTS-quality content simultaneously.

> [!TIP]
> **Scaling Warning**: If we upgrade to 4K Remux (avg 80 Mbps), the same 400GB will only hold ~11 hours of content. Our current strategy is perfectly optimized for the YTS/WebRip tier.

## 5. ⚙️ TRANSCODING VS. PRE-CONVERSION (VERSIONS)
To optimize CPU/GPU usage and provide a smooth experience for users with varying bandwidth:

*   **Direct Play First**: Prioritize "Direct Play" for Morelia users (700Mbps line is enough for 10-20Mbps local streams).
*   **Optimized Versions**: Use Jellyfin's "Versions" feature to pre-convert popular content into lower bitrates (e.g., 720p 2Mbps).
    *   **The Jewel**: Pre-converted versions are stored permanently in the media folder, *not* just temporary cache. This allows "Transcode once, Stream many" without needing a GPU later.
*   **Trickplay (Previews)**: Thumbnails and intro-skipping data are stored in `/var/lib/jellyfin/metadata`. This is high-IO work, perfect for the **M.2 M2_Cache subvolume**.

---
*Vega OS Kernel - Storage Decisions*
