---
name: deep-research
description: Use for structured evidence-first deep research when the user asks for deep research, broad research surveys, source-backed reports, or research packages that need source collection, cross-validation, claim boundaries, unresolved questions, and sub-agent parallelization.
---

# Deep Research

A structured, evidence-first, in-depth research process.

Research has no fixed time or token limit. Complete the requested scope and deliverables with evidence for key conclusions and an account of unresolved gaps. Do not extend the research merely because more sources exist.

## Workflow

Strictly follow the procedures below.

1. **Clarify the Research Question**
    - What exactly needs to be researched?
    - What level of detail is required?
    - Are there specific angles to prioritize?
    - What is the purpose of the research?

2. **Identify Key Aspects**
    - Break the topic into subtopics or dimensions
    - List main questions to answer
    - Note important context or background needed

3. **Broad Exploration**
    - Start with broad searches to understand the landscape
    - Search for the main topic to understand the overall context
    - From initial results, identify key subtopics, themes, angles, or aspects that need deeper exploration
    - Note different perspectives, stakeholders, or viewpoints that exist
    - Don't let the first one or two sources define the entire direction of the investigation

4. **Deep Dive**
    - For each important dimension identified, conduct targeted research
    - Search with precise keywords for each subtopic
    - Try different keyword combinations and phrasings
    - Read important sources in full, not just snippets
    - When sources mention other important resources, search for those too

5. **Validation**
    - Ensure comprehensive coverage of diverse information types, fetch and read the most important sources in full
    - When multiple sources repeat the same statement, they should be considered as part of the same chain of evidence, integrated and cross-verified
    - Mark important claims as facts, inferences, judgments, propaganda, or unresolved uncertainties
    - Do not write a definitive conclusion when the supporting relationships are unclear

6. **Summarize**
    - Compile and summarize the key findings from the research
    - Provide summary of conclusions, sources list, full report, and any unresolved questions
    - Write the output based on the evidence
    - Present facts, inferences, judgments, recommendations, and questions to be confirmed separately

## Fetching

Suitable for `Broad Exploration` and `Deep Dive`.

The preferred approach is to save the original content as a verifiable Markdown source file using Skills or MCP in user space. If valid webpage content is unavailable, at least a detailed summary, key excerpts, URLs, authors, publication dates, and access date should be saved for later analysis.

Sources:

- Official documents, articles, blogs, reports, statistics: authoritative sources
- General websites: require independent verification

## Principles

- The quality of your output directly depends on the quality and quantity of research conducted beforehand. A single search query is NEVER enough.
- Prioritize finding primary sources: official documents, papers, publication pages, and direct product documentation.
- Secondary sources should only be used to discover clues, supplement background information, or aid in comparisons.
- Separate source collection and final synthesis to avoid drawing premature conclusions.

## Output

Research requires the production of reports and documents by default, unless otherwise specified by the user.

Document the source material, evidence comparisons, and unresolved gaps needed to support the conclusions.

## Sub-Agents

- Use sub-agents as much as possible for parallel collection, processing, and analysis.
- The maximum number of sub-agents that can run concurrently depends on the limitations of the environment.
- If the number of tasks to be assigned exceeds the limit, queue them and start new sub-agents only after the preceding tasks have completed.
- Do not interrupt normally progressing sub-agents because they are slow. Correct errors, missing input, or scope drift promptly.
- Prefer correction to termination. If a task cannot recover, save its current state.
