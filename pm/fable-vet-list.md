# Fable vet list (run when JB asks)

Kept by the Project Manager session. Each item: repo, PR or branch, and what to vet hardest.
The last Fable vet covered work through 2026-11-19 ~17:30 UTC.

## Payments (vet first and hardest)
- topshot-modular #417: payment alerts (bell and email, sender, owner and admins; PAYMENT_ALERT_EMAILS now "all")
- #414: monthly payment account choice, Account N names, rename with PIN
- #418: "never stops" fix 1: holds, hourly re-capture, confirming page with arrows, no "cancelled" when money may have moved
- #424: check connection
- #426: names cleanup phase 1 (staff tasks, bells, alerts name the account, never the processor)
- #427: legal pages say "the payment company" (Terms, Privacy, subprocessors, refunds)
- #428: business logo on the done/celebration screen
- #429: fix 2: unverified notice alerts (Square, Stripe, Clover, PayPal setup)
- #430: fix 3: calm customer screens and an immediate "being confirmed" bell
- #431: fix 4: hourly sweep for tickets, orders and PDF forms; "nothing taken" owner note (customer email OFF)
- #432: JB's "Hang tight" wording, 3s/10s timing, decline bell to the link sender
- #433: fix 5: fallback to a working account, missing-key bells, calm brake wording, OTG price-read retry
- #434: customer-facing names ("Secure card payment", "Pay $X securely"), nickname never on customer surfaces
- Coming: names phase 2 slices (invoicing "Pay link" rule, rosters, inbox, odds and ends)
- Live DB change made by the PM: Top Shot account nickname set to "TS PayPal" (tenant_payment_providers 48d4acb3…)

## Other merged work
- #415: PIN reminder chip
- #416: relay gallery gate and owner/staff wording
- #419: users.full_name fix (team page, VIP host alert)
- #420: Joy relay gate tier check
- #422 + migration 384 (applied): engagement campaign (stays OFF)
- #407: Show me and recipes (conflict resolved in action-executor-client.ts)
- #435: class type-to-filter, and Joy uses the Apps-page names
- #410 / #412: Video Studio edges and story staging
- #421: Workflow Builder phase 1 (automatic steps in guided flows, "Auto" pill; existing 90 automations untouched)
- #406 + migration 383: receipts part 1 (card numbers refused in notes)
- #423: video library server side (migration 385 NOT applied)
- #425: back pose sit and think
- builder #208: Harbor forms to intake (migration 906, builder test copy only)

## Later / not merged yet
- Lily kneel PR, the 90-day video removal rule, the campaign PR-A and PR-B, Harbor ease-of-use, Joy tax help, Harbor into live (900–906), decision 64 sweep, builder port batches
