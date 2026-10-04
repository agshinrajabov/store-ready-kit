# Rejection record (anonymised)

- **Platform / version:** iOS 1.0, second review of the same concept.
- **Date:** 17 September 2026. The day before, the first review had rejected the build under 2.1(a)
  (a tap on the first piece did nothing on an iPad). The fixed build was resubmitted and reviewed by a reviewer
  who played it.
- **Guideline:** 4.3(b) Design — Spam.
- **Wording (excerpts from the letter):** the app's "design, content, and overall concept do not provide the
  high-quality experience expected"; it asked for a "meaningful, well-crafted experience"; "Do not resubmit for
  review until significant changes have been made"; it recommended TestFlight; it closed with the Extended Review
  paragraph (repeat submissions with these issues lengthen review and can lead to removal from the Developer
  Program).

## What the developer's own audit found afterwards

- The mechanic was new. The package was the category's: 13 of 16 hyper-casual template traits fully on screen in
  the developer's own catalogue (15 full + 1 partial in this kit's catalogue, which also counts generated levels
  and the engine splash), a
  keyword-stack name and subtitle, generated levels, and five purchase or ad prompts within the first three minutes (recorded as `purchase_prompts_first_10_min: 5`).
- The letter matches the low-effort / low-quality prong of the June 2026 4.3(b) text, not the "saturated category"
  prong. Arguing "nothing else unfolds rides" would not have answered it.

## What the eval expects

`store-audit` must FLAG this listing, and its top reasons must include the template traits and the monetisation
surface — the two things a fix has to move. A PASS or a WARN here is a failed eval.
