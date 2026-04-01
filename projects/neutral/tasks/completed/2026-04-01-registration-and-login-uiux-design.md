# Registration and Login UI/UX Design

**Agent:** ingrid
**Status:** completed
**Created:** 2026-04-01
**Completed:** 2026-04-01
**depends_on:** 2026-04-01-authentication-system-architecture.md

## Description

Design the user-facing authentication flows for the URL shortener. Produce: (1) wireframes (ASCII or structured descriptions) for register page, login page, and logged-in dashboard showing owned URLs; (2) user flow diagram covering happy path (register → verify → login → shorten URL) and error states (wrong password, duplicate email, expired token); (3) form field specifications including validation rules and error messages; (4) UX decisions on redirect behavior after login, session persistence options, and account settings page layout. Output as a markdown document with embedded ASCII wireframes.

## Deliverable

`output/2026-04-01-auth-ux-design.md`

Covers all 7 auth screens (register, email-verification pending, login, forgot-password, reset-password, dashboard URL list, account settings), full user flow diagram with happy path and 6 error paths, field specs, validation rules, empty/loading/error states, 8 UX decisions, accessibility notes, component reuse checklist, and implementation notes for Arve.
