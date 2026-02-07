# 🔐 VAULT PROTOCOL: FULL-STACK CLIENT-SIDE ENCRYPTION

> "True privacy means the server never sees the truth."

## 🏗️ Architecture
The Vault Protocol implements **Zero-Knowledge** principles for sensitive tasks. When a task is marked as `is_encrypted`, the core data is transformed into ciphertext before leaving the client's browser.

## 🔒 Encrypted Entities
The system applies AES-GCM (256-bit) encryption to the following fields:
1.  **Objective (Title):** The primary task content.
2.  **Core Details (Description):** Detailed parameters and notes.
3.  **Subtask Sequences (Checklist):** The entire array of subtasks, including status and timestamps.
4.  **Visual Blueprint (Whiteboard):** The complete Excalidraw scene (elements, state, and files).

## 🔑 Key Management
- **Engine:** Web Crypto API (`window.crypto.subtle`).
- **Algorithm:** AES-GCM for encryption, PBKDF2 for key derivation.
- **Scope:** Keys are derived from the **user's password**, ensuring that even if the database and the system are compromised, the data remains inaccessible without the correct password.
- **Persistence:** The derivation password is kept in `sessionStorage` during the active session and is never persisted to disk or sent to the server.

## 🛠️ Operational Logic
- **Auth Flow:** `Password` -> `Stored in sessionStorage (Client Only)`.
- **Write Flow:** `Plaintext Data` -> `JSON Stringify` -> `Encrypt (Client using session password)` -> `Store (Supabase)`.
- **Read Flow:** `Ciphertext (Supabase)` -> `Decrypt (Client using session password)` -> `JSON Parse` -> `Render UI`.

## ⚠️ Privacy Warning
Encryption is linked to the **User Password**. If the password is changed via an external reset or forgotten, the encrypted data will be unrecoverable unless the previous password is known.

---
*Vega OS Kernel - Security Module*
