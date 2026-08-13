---
name: vault-compounding-loop
description: Use when deciding whether generated synthesis belongs in the vault's outputs. Save only provenance-backed dura
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, outputs, provenance, compounding]
    related_skills: [vault-ingestion, vault-retrieval, vault-external-workflow-evaluation]
---

# Vault Compounding Loop

## Overview

Robert wants a compounding knowledge system, not transcript pollution. The output gate is strict: save durable synthesis only when it is grounded in proper ingestion, internalization, or already-existing source-backed vault material.

## When to Use

- You are deciding whether a result should become an `outputs/` note.
- A post-ingestion discussion produced reusable synthesis.
- An external-workflow evaluation might produce a durable recommendation.
- A retrieval answer was strong, but you need to decide whether it belongs in the vault.

## Output Creation Policy

- Do not create vault files from ordinary chat assessments.
- Outputs require source-backed ingestion or existing source-backed vault material.
- Background reports do not automatically become `outputs/` notes.
- If a discussion after ingestion produces durable synthesis, save it only when provenance exists and link it to real source material.

## Common Pitfalls

1. Saving a useful chat answer even though it has no durable provenance.
2. Confusing operational reports with knowledge artifacts.
3. Creating an output because the synthesis sounds good rather than because it is grounded.
4. Failing to link the output to the notes or extracts that justify it.

## Verification Checklist

- [ ] Provenance exists.
- [ ] The result is durable and reusable.
- [ ] The note links back to real source material.
- [ ] This is not just an ordinary chat answer or background report.
