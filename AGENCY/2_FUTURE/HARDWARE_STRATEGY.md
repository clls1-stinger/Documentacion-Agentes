# 🚀 HARDWARE & TRANSCODING STRATEGY

## 1. Current Infrastructure (Snapshot)
*   **CPU**: Intel i7-7700K (4.2GHz)
*   **GPU**: AMD Radeon RX 580 2048SP
*   **Storage**: 
    *   M2 NVMe: 1TB (1.8 GB/s Write Speed confirmed).
    *   HDDs: 2x 1TB (sda1, sdb3).

## 2. Transcoding Strategy
> [!IMPORTANT]
> **Primary Recommendation**: Use **Intel QuickSync (iGPU)**.
> - The i7-7700K includes Intel HD 630.
> - **Stability**: Much higher than the RX 580 on Linux for 24/7 service.
> - **Efficiency**: Decodes H.264/HEVC (10-bit) with minimal CPU usage.
> - **Safety**: It won't crash the graphical session or the kernel under heavy load, unlike older AMD/NVIDIA drivers sometimes do.

## 3. Future RTX Upgrade
If the service scales and generates revenue, these are the target GPUs:

| GPU | Why? | Estimated Performance |
| :--- | :--- | :--- |
| **RTX 3060 12GB** | **King of Value**. The 12GB of VRAM allows for many simultaneous 4K streams. | ~15-20+ 1080p transcodes. |
| **RTX 4060** | **Efficiency & AV1**. Lower power consumption and support for AV1 encoding (future-proof). | ~10-15+ 1080p transcodes. |

## 4. Storage Plan (The 900GB Goal)
*   **Short term**: Mount `nvme0n1p1` (Windows) as an external drive in `/mnt/windows` to consume existing media.
*   **Long term**: Clear the 600GB Windows partition, format to BTRFS or Ext4, and merge it into the Media Stack.

---
*Vega OS Kernel - Hardware Strategy v1.0*
