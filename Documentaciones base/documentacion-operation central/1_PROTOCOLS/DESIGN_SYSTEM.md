# 🎨 Design System Protocol (Aesthetic v4.0 - Spatial Flow)

> Guidelines for the high-fidelity npmx-inspired UI and its spatial interactions.

## Visual Tokens
- **Core Color**: `#00dc82` (Nuxt Green) used for glows, highlights, and active states.
- **Background**: `#050505` (Deepest Black) for maximum contrast.
- **Glassmorphism**: 
    - `backdrop-filter: blur(24px)` for sidebars and headers.
    - `border: 1px solid rgba(255,255,255,0.05)` for subtle definition.
- **Typography**: `Inter` for UI, `JetBrains Mono` for metadata and technical IDs.

## Interaction Principles
- **Hide-on-Scroll Navigation**: Header uses a spring transition (`stiffness: 200, damping: 25`) to animate out of view.
- **Vertical Tabs**: Side-aligned triggers with `[writing-mode:vertical-lr]` text and width-expansion on hover.
- **Independent Column Scrolling**: Uses `overflow-y-auto` on individual columns while the main background remains static.
- **World Transitions**: Uses Framer Motion `AnimatePresence` with `x` (slide) or `scale` (pop) transitions depending on the target world.

## Component Architecture
- **TaskCard**: Hover-reactive (`translate-y-[-2px]`), priority-coded status indicators (Urgent=Red, High=Orange, etc.).
- **Utility Tabs**: Backlog (Zinc/Muted), New Task (Emerald/Vibrant).
- **Fancy Toast**: Top-centered notification with scale-up entrance and holographic glow.

---
*Vega OS Kernel - Design Intelligence Module*
