# 🎨 VEGA OS KERNEL: UX/UI & AESTHETIC PROTOCOL

> **Directive**: All agents (AI or Human) contributing to the Vega OS interface MUST adhere to these visual and functional standards.

## 1. 🌈 VISUAL IDENTITY (The "Glassmorphic Emerald" System)
The Vega OS uses a high-contrast, dark-mode design system with glassmorphic elements and neon accents.

*   **Primary Background**: `#050505` (Pure Deep Black).
*   **Secondary Background (Cards)**: `#080808` with `backdrop-blur-xl` and `border-white/5`.
*   **Accent Color**: `#00dc82` (Emerald Green). Use it for actions, progress, and highlights.
*   **Typography**: Inter or similar Sans-Serif. Use **UPPERCASE** and **Black (900)** weights for headings and small labels to give a "military/system" feel.
*   **Glow Effect**: Use `shadow-[0_0_20px_rgba(0,220,130,0.3)]` on emerald elements to simulate neon glow.

## 2. ⚡ UX PRINCIPLES
*   **Zero Native Prompts**: NEVER use `window.prompt()` or `window.confirm()`. All inputs must be inline or styled modals.
*   **Immediate Feedback**: Every action must have a visual response (hover states, active scales `scale-95`, loading spinners).
*   **Glassmorphism**: Use `bg-white/5` and `backdrop-blur-md` for elements that float over the main background.
*   **Micro-interactions**: Use `framer-motion` for transitions. Initial state: `opacity: 0, y: 10`, Final state: `opacity: 1, y: 0`.

## 3. 🧩 COMPONENT STANDARDS
*   **Buttons**:
    *   Primary: Emerald background, black text, bold uppercase.
    *   Secondary: Glassy background (`bg-white/5`), emerald border, emerald text.
*   **Inputs**:
    *   Transparent or very dark backgrounds.
    *   Subtle borders (`border-white/10`).
    *   Emerald glow on focus (`focus:border-emerald-500/50`).
*   **Cards**:
    *   Rounded corners: `rounded-2xl` or `rounded-3xl`.
    *   Border: `border border-white/5`.
    *   Hover state: `hover:border-emerald-500/30`.

## 4. 🛠️ AGENT SKILL: "The Aesthetic Eye"
When modifying UI components, an agent MUST:
1.  **Check Context**: Read `index.css` and `tailwind.config.js` before adding new classes.
2.  **Maintain Hierarchy**: Ensure labels use small, bold, uppercase text with letter-spacing (tracking).
3.  **Validate on View**: After a change, confirm that the new element doesn't break the "Glassmorphic" synergy.

---
*Vega OS Kernel - Design Authority v2.0*
