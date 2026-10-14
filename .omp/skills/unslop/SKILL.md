---
name: unslop
description: Cut AI tells from any writing. Express yourself naturally and directly, consider the reader, and eliminate stock phrasing, defensive language, and session leakage. Must always apply.
---

# Unslop

Express yourself naturally and directly. Consider the reader of this text. Articulate your ideas clearly and retain only the information the reader needs. Eliminate stock phrasing, internal musings, conversational filler, defensive language, and unnecessary self-justification.

Use when outputting anything, including session replies, documentation, code comments, and agent communication.

## Guidance

- **Read the complete guidance.** A description or excerpt is not enough. Reuse the full text already in context and retrieve missing content after context loss.
- **Check the result.** Write for the intended reader and requested format. Before delivery, compare facts and conclusions with the source, compare protected text character by character, and check the requested structure and length.
- **Follow instructions.** Normally edit the target file in place unless instructed otherwise. Follow any other instructions, such as reviewing only or producing a report. For conversational replies, respond directly.
- **Verbatim exceptions.** When quotations, logs, commands, identifiers, or other content need to remain verbatim, preserving their wording, punctuation, and spacing generally takes precedence over style rules.

## Process

1. Scan for the patterns below.
2. Rewrite. Preserve meaning, match the intended tone.
3. Add soul.
4. Self-audit: "What makes this obviously AI-generated?" Fix remaining tells.

## Unslop patterns

Detect the following patterns and fix them.

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Cut puffery, state what happened.
2. **Name-dropping.** Listing media outlets without context. Pick the source that has content, say what it said, and drop the names that carry nothing.
3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources.
4. **Promotional language.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use neutral descriptions.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete.
6. **Formulaic challenges.** "Despite challenges... continues to thrive." Replace with specific facts.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. **Contrast formulas.** "Not X, but Y", "Not just X, but Y". State the point directly instead.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it, and drop the explanation that the other names mean the same thing.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). Em dashes are an AI tell, and reaching for parentheses instead just trades one tell for another. If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A label that names an item and is followed by content the label does not already state ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Quote overuse.** Use as few quotation marks as possible. Wrapping a metaphor or a loose term in quotes ("hallucinates", "set it and forget it", 所谓"抓手") is an AI tell. Write the metaphor directly: the model hallucinates. Keep quotes for verbatim quotations. Where a quote is truly needed, use straight quotes, not curly ones, and do not add them while editing.
20. **Long text in tables.** Reserve tables for numbers and classification text, such as enumerations. Long text belongs in a list, nested as needed. Prose spread across cells is hard to scan as source and renders unevenly.

### Communication artifacts

21. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove.
22. **Cutoff disclaimers.** "While specific details are limited..." Find sources or remove.
23. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

24. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted.
25. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may".
26. **Generic conclusions.** "The future looks bright." State specific plans or facts.

### Jargon

27. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word, and keep the object the metaphor described.
28. **Chinese jargon.** Such as "赋能、助力、驱动、抓手、闭环、链路、全链路、拉通、对齐、反哺、颗粒度、组合拳、生态位、赛道、破圈、降维打击、天花板、长期主义、情绪价值". Apply the same approach as in pattern 27.

### Plain speech

29. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
30. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
31. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
32. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong. Keep the measurement and its conditions next to the claim, so the sentence still does not read as a general guarantee.
33. **Prefer the plain word.** "utilize" becomes "use". "leverage" becomes "use". "facilitate" becomes "help". "numerous" becomes "many". "in the event that" becomes "if". The fancier synonym is rarely clearer.

## Defensive phrasing

Defensive phrasing typically involves avoiding saying anything wrong, stressing how careful the writer is, or listing what they did not do, all to avoid responsibility. It replaces results with disclaimers and excuses. The user gets no useful answer, and the agent still has to complete the task. Make this a priority when editing.

### Typical patterns

Watch for these patterns. Check whether they replace work that needs doing or useful content.

- **Disclaiming conclusions.** "Cannot prove", "only shows", "does not mean", "does not claim", "does not constitute advice", "cannot guarantee", and "不能证明", "只能说明", "不代表", "不声称", "不构成建议", "不保证". Using these statements instead of investigating, checking, or making a judgment is the most serious symptom. The agent goes through the motions, gives the user a disclaimer, and leaves the problem unsolved. To fix this, check whether the work meets the requirements, whether essential checks were skipped, and whether a result that falls short was passed off as complete. If only the wording is too cautious, state the conclusion supported by the evidence clearly. If the work has problems, redo it.
- **Limits of knowledge.** "Not yet", "no evidence found", "cannot confirm", "not verified", "do not infer", and "尚未", "未见", "无法确认", "未验证", "不推断". An agent that raises unrelated, unanswered questions to seem thorough gives the reader unnecessary work. Remove those questions and the statements attached to them. If the agent stops instead of doing necessary checks, it passes the work to the user and should complete those checks. Put what was checked and where the evidence came from beside the result. Remove repeated disclaimers and records of operations that do not affect delivery.
- **Scope of work.** "Did not modify", "did not commit", "did not run", "remained read-only", and "未修改", "未提交", "未执行", "保持只读". This is a milder problem, and occasional use is acceptable. Repeatedly listing what the agent did not do makes the reader dig through operation records for the result. It also turns following instructions into self-praise. Remove these lists when no report is required. Keep status reports explicitly required by a Skill, standard, workflow, or the user. If work left undone affects task completion, treat it as a problem to solve. Do not delete it as unnecessary wording.

### How to fix it

First check whether the problem is in the wording or in the work itself. Compare the task requirements, what was done, and the evidence. Finish the required implementation, investigation, or checks within the scope already authorized. Redo incorrect work. If permission, information, or conditions needed to do the work are missing, say what is missing, how it affects the task, and what needs to happen next. Continue with work that is not affected. Do not stop at "cannot confirm", or do unrelated or unauthorized work just to answer a question.

If the work is sound, edit the wording. Ask what question the paragraph answers and whether it starts from the actual request and information. What facts, judgments, or actions remain after removing disclaimers, excuses, and repeated statements of limits? Does it make a broad claim without evidence, then deny it later? Delete text that adds nothing and whose removal does not change the meaning. Removing a problem sentence or changing a few words may still leave an empty paragraph. Delete the whole paragraph if it has nothing useful to say. Do not add more empty words to replace it.

If the content is useful but starts from the wrong question or is written to defend the writer, drop the original structure and rewrite it around what the reader needs. Put useful facts beside the relevant conclusion or action. Rewrite affected paragraphs and sections around it too. Keep facts, real risks, important unanswered questions, permission requirements, and explanations and evidence that affect the reader's judgment or action. Put this information beside the relevant conclusions so the reader can see their basis and the conditions under which they hold. Remove claims that have no evidence and the excuses used to defend them.

## Trimming chain-of-thought leakage

Chain-of-thought leakage is prose whose vantage is the authoring session rather than the document. It cites artifacts that only that session could see, narrates changes instead of the resulting state, argues with a reviewer who has left, or includes control-flow narration, hedges, or untranslated working-language fragments.

Read from the perspective of someone who has only the finished content, without access to the session, meeting notes, earlier drafts, or review discussions. Check that readers can understand and verify every reference and claim from the finished content and its accessible sources after editing, especially following an interruption, correction, or added requirement. Preserve all still-valid facts, and cite only material available to the intended reader. State current behavior where appropriate; historical phrasing is not inherently leakage.

Examples:

- **Change narration.** "used to", "no longer", "now uses", "change to XX based on feedback". State the current behavior, e.g. "now writes serially" becomes "writes serially".
- **Version stamps.** "this cut", "v3 of this note", "this round". Omit drafting stamps, keeping real software versions and runtime old/new states.
- **Correction labels.** "XX Feature (without YY version)", "XX after removing YY", "XX with YY". State the main subject and final functionality directly, omitting the description of the correction itself.
- **Temporary instructions.** "skip full tests this time", "this round using XX". Keep temporary instructions within the session scope only. Do not let them automatically become long-term requirements.
- **Session references.** "(decision 7)", "design §4.2", "tasks/<id>/plan.md". Replace dead citations with a verifiable source or standalone fact.
- **Review vantage.** "a later PR in this stack", "rejected in review", "the reviewer confirmed". Keep the mechanism, invariant, or rationale.
- **Editing narration.** "Change title only," "keep this section," "fill in the rest in the next round". Act on the instruction, omit the narration.
- **Planning residue.** "probably enough", "leave it for now". State verified bounds or explicit uncertainty.
- **Untracked leakage.** Mentioning Git-ignored files, temporary artifacts, or untracked task information. Remove these references and restate useful facts.

## Writing articles

Use the following methods to guide article writing.

### Real content

Real content is the substance of a piece, the part that makes it worth reading. Strip away the source notes, disclaimers, methodology labels, and structural boilerplate, and see what remains. If the text still tells us what happened, what the author discovered, and why it matters, it has substance. It gives the reader something to take away. That substance is what makes editing worthwhile. If there is almost nothing underneath, polishing only makes an empty piece read more smoothly.

This also sets the limits of editing. An editor can rearrange material, cut repetition, and smooth out awkward phrasing, but cannot invent experiences the author never had. Better to let a lack of substance show than to disguise it with layers of explanation and qualification.

Striking the right balance between substance and filler takes judgment, too. A piece heavy on substance may be heartfelt without being an easy read. Too much filler, though, leaves readers wading through words with little to show for it. The vast majority of AI-generated writing falls into the latter category, making it especially important to spot and cut the filler.

### Implicit context

A piece of writing does not need to spell out every premise. Knowledge shared by the writer and the intended audience, connections readers can readily make between paragraphs, and limits established earlier that still apply can all remain implicit. Readers take an active part in making sense of a text. They do not need the writer to walk them through every step of the reasoning. But what seems obvious to the writer may not be obvious to the reader. What can be left unsaid depends on what the intended audience already knows and what the text has told them.

For readers familiar with Python tooling, "Run mypy" already signals static type checking. There is no need to keep explaining what type annotations are for. But that phrase alone does not establish that the project enforces stricter typing rules, let alone that the checks cover the entire codebase. If the strictness or scope of the checks affects the article's conclusions, those details need to be stated. Shared knowledge helps readers understand a tool's purpose; it cannot establish how a particular project actually uses it.

Likewise, "So far, this has only been tested on Node 22. Other versions have not been tested yet" makes the scope of testing clear. Changing that to "It only runs on Node 22" turns an unknown into a definite limitation. "Not tested" does not mean "cannot run." This kind of qualification is not unnecessary explanation. It is part of the conclusion.

Leaving something implicit is not the same as withholding information or making readers guess. Explanations that readers can readily supply for themselves may be omitted; facts they need to understand the subject and make judgments may not. If leaving something out would change how readers interpret the facts or conclusions, or affect what they do next, make it explicit. Give readers essential information where they need it, without repeatedly restating premises that have already been established and still hold. Where the reasoning may be difficult to follow, provide the key justification. There is no need to reproduce the entire thought process.

Implicit context governs how much explanation a piece needs. Too little, and readers lose the thread. Too much, and the focus shifts from the subject to the explanation itself, becoming a showcase for AI's own thoroughness. When analyzing a piece, look for where readers might get confused and what information they are missing, rather than building a full chain of reasoning to justify every sentence.

## Adding soul

Removing patterns is half the job. Sterile, voiceless writing is just as obvious. Preserve the author's authentic observations, judgments, pacing, and tone.

- **Have opinions.** React to facts instead of neutrally listing pros and cons.
- **Vary rhythm.** Short sentences. Then longer ones that take their time. Mix it up.
- **Acknowledge complexity.** "Impressive but also kind of unsettling" beats "impressive."
- **Use "I" when it fits.** First person isn't unprofessional.
- **Let some mess in.** Perfect structure looks machine-made.
- **Be specific.** Not "this is concerning" but "there's something unsettling about agents churning away at 3am."
