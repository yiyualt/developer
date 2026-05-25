Output Parsing Philosophy
=========================

Why Parse LLM Output?
----------------------

LLMs produce **free-form text**. They don't return JSON objects, Python
dicts, or database rows — they return strings that *look approximately*
like what you asked for.

This is the fundamental gap between LLMs and software:

.. code-block:: text

   LLM thinks in text          Software needs structure
   "Python is a programming    {"name": "Python",
    language"                    "type": "programming",
                                "paradigm": "multi"}

   "Python, Rust, Go"          ["Python", "Rust", "Go"]

Without OutputParser, LLMChain returns a string. That string might
contain JSON, a list, or just rambling prose — your code can't tell,
and can't use it programmatically.

The Parser as a Contract
-------------------------

OutputParser bridges this gap by converting approximate text into
exact data. It's a **contract** between the chain and the caller:

- The chain promises: "I will try to produce output in this format"
- The parser promises: "I will extract this format from whatever the LLM returns"

When the LLM returns clean JSON, parsing succeeds trivially. When it
returns JSON wrapped in markdown ``json`` code blocks or mixed with
explanatory text, the parser still extracts the structured portion.

Design Principle: Optional, Not Required
------------------------------------------

OutputParser is **optional** in LLMChain. Without it, the chain returns
raw strings (v0.0.1 behavior). This is intentional:

1. **Backward compatibility** — existing chains keep working unchanged
2. **Development flexibility** — start without a parser, add one when
   you need structured output
3. **Debugging** — see raw LLM output first, then decide what to parse

The pattern: **develop with raw output, graduate to parsed output**.

Why JsonOutputParser Uses Regex, Not Strict json.loads
-------------------------------------------------------

LLMs don't return pure JSON. Common patterns:

- A markdown ``json`` code block wrapping the JSON
- ``Here is the JSON: {"key": "value"}. Hope this helps!`` (mixed text)
- ``{"key": "value"}  // some comment`` (extra formatting)

Direct ``json.loads`` would fail on all three. JsonOutputParser first
*extracts* the JSON portion, then parses it. This two-step approach
(extract → parse) is more resilient than a single-step parse.

The Trade-off: Robustness vs Precision
---------------------------------------

OutputParser trades precision for robustness. It accepts imperfect
LLM output and extracts the best-fitting structure. This means:

- It may sometimes extract the wrong JSON block if multiple exist
- It may include extra whitespace or formatting artifacts
- ListOutputParser may misinterpret text that happens to contain commas

These are inherent limitations of parsing unpredictable text. Future
versions will add ``get_format_instructions()`` to *guide* LLM output
format, reducing ambiguity before parsing.