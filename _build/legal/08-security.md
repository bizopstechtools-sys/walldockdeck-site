title: Security Overview
path: /legal/security/
kicker: Security
group: Data, privacy and security
order: 4
updated: 2026-10-02
summary: How we protect what you give us, what we have not built yet, and how to report a problem.
---

## What this site is

walldockdeck.com is a static website. The pages you read are plain HTML files with no database behind them, which removes most of the ways a website gets broken into. Everything is served over HTTPS.

The forms are the part that handles your information, and they post into our CRM rather than into anything on this site.

## Your information

**In transit.** Everything between your browser, this site and our providers is encrypted with TLS.

**At rest.** Enquiry records live in our CRM, encrypted at rest by its database provider.

**Who can see it.** Access is limited to people who need it to answer you. Today that is a very short list.

**Contractors see only what they need** — your name, contact details, property address and your enquiry. Not your browsing history, not other enquiries, not anything else we hold.

## Messages

Email and text go through established providers rather than anything we built. We verify inbound webhooks from those providers before trusting them, so a forged delivery receipt cannot change a record.

## What we have not built

We would rather tell you than imply otherwise:

- **No SOC 2, ISO 27001, PCI DSS or HIPAA certification.** We have not been audited against any of them
- **No penetration test** has been run against this site
- **No formal incident response plan** beyond the notification duty below
- **No bug bounty**

We are a small business and these are honest gaps, not oversights we are hiding. They will close as we grow, and this page will say so when they do.

## What we deliberately do not hold

The simplest way to protect information is not to have it.

- **No payment card numbers.** We take no payments from property owners at all
- **No Social Security or government identifiers**
- **No health information**
- **No passwords from you** — there is no account to log into

If you send us any of the above in a notes field, we delete it.

## If something goes wrong

If a security incident affects your personal information, we will tell you as required by law, including **Florida Statutes § 501.171**, which requires notice within **30 days**. We will tell you what happened, what was affected, and what we are doing about it.

## Reporting a vulnerability

If you find a security problem, email **hello@walldockdeck.com** with enough detail to reproduce it.

**We will acknowledge within two business days** and keep you updated.

**Safe harbour.** We will not pursue or report anyone who reports a vulnerability in good faith, provided you do not access or modify other people's data, do not degrade the service, and give us a reasonable chance to fix it before telling anyone else. We will credit you if you want the credit.

## Your part

If you are a contractor in our network with access to referred enquiries: use a strong, unique password on your own systems, tell us the moment someone leaves your team, and never forward an owner's details outside your own business. Most incidents anywhere start with a reused password.
