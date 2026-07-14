"""Normalize Loco's Qt ``.ts`` export into Qt-consumable form.

Loco's Qt exporter (flagged "LEGACY") emits Apple/printf-style placeholders
(``%@``, ``%lld``, ``%1$s``) and SwiftUI Markdown (``**bold**``). Neither is
understood by Qt at runtime: ``QString::arg`` only knows ``%1``…``%99`` and the
plural token ``%n``, and ``Text`` renders HTML rich text, not Markdown.

This module rewrites, in place, the text of every ``<source>``,
``<translation>`` and ``<numerusform>`` element:

* ``%@`` / ``%lld`` / ``%d`` …            → ``%1``, ``%2`` … (in order)
* positional ``%1$s`` / ``%2$@`` …        → ``%1``, ``%2`` (index preserved)
* an integer specifier inside a plural    → ``%n`` (Qt's count token)
* ``**bold**``                            → ``&lt;b&gt;bold&lt;/b&gt;``

Numbering restarts at each element, which keeps the source and every
translation of the same message consistent: Apple ``%@`` ordering is by
appearance, so numbering by appearance matches the original semantics.

It also **empties every ``<context>`` name**. The export is id-based (each
``<message>`` carries an ``id``) and is meant to be looked up at runtime with
``qtTrId``/``qsTrId``, which only ever query the *empty* context. Loco writes each
string's category into the ``<context>`` name (``main``, ``Settings``, ``Description
for … error`` …), which would scatter the ids across named contexts and make them
unreachable; blanking the name files every message under the empty context, keyed
by its id alone.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Conversion specifiers that actually occur in kDrive catalogs. Restricting the
# set keeps a literal '%' in prose from ever being mistaken for a placeholder.
_CONV = r"[@sdiufxX]"
_LEN = r"(?:hh|h|ll|l|L|z|j|t)?"

# One printf/Apple placeholder:
#   %%            escaped percent (left untouched)
#   %1$s %2$@     positional: explicit argument index
#   %@ %lld %d …  non-positional: numbered by order of appearance
_TOKEN_RE = re.compile(
    r"%%"
    r"|%(?P<pos>\d+)\$" + _LEN + _CONV
    + r"|%[+\-# 0]*\d*(?:\.\d+)?" + _LEN + r"(?P<conv>" + _CONV + r")"
)

# Integer conversions become Qt's ``%n`` count token inside a plural form.
_INT_CONV = frozenset("diuxX")

# SwiftUI bold. Text content is XML-escaped, so we inject escaped angle brackets
# to keep the .ts valid; lrelease decodes them back to <b>…</b> in the .qm.
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)

# Loco stores each string's category as the <context> name, but qtTrId/qsTrId only look up the
# empty context. Blanking every name keys each message by its id alone. (<name> only ever appears
# as a context name in a .ts, so a document-wide sub is safe.)
_CONTEXT_NAME_RE = re.compile(r"(<name>)[^<]*(</name>)")

_MESSAGE_RE = re.compile(r"<message\b.*?</message>", re.S)
_SOURCE_RE = re.compile(r"(<source>)(.*?)(</source>)", re.S)
_NUMERUS_RE = re.compile(r"(<numerusform>)(.*?)(</numerusform>)", re.S)
_TRANSLATION_RE = re.compile(r"(<translation\b[^>]*>)(.*?)(</translation>)", re.S)


def _convert_placeholders(text: str, in_plural: bool) -> str:
    counter = [1]

    def repl(match: "re.Match[str]") -> str:
        token = match.group(0)
        if token == "%%":
            return token
        pos = match.group("pos")
        if pos is not None:
            return "%" + pos
        if in_plural and match.group("conv") in _INT_CONV:
            return "%n"
        number = counter[0]
        counter[0] += 1
        return "%%%d" % number

    return _TOKEN_RE.sub(repl, text)


def _convert_markdown(text: str) -> str:
    return _BOLD_RE.sub(r"&lt;b&gt;\1&lt;/b&gt;", text)


def _convert_element_text(text: str, in_plural: bool) -> str:
    return _convert_markdown(_convert_placeholders(text, in_plural))


def _normalize_message(block: str) -> str:
    # A plural message wraps its forms in <numerusform>; its <source> then also
    # carries the count placeholder and must be treated as plural too.
    is_plural = "<numerusform>" in block

    block = _SOURCE_RE.sub(
        lambda m: m.group(1) + _convert_element_text(m.group(2), is_plural) + m.group(3),
        block,
    )
    if is_plural:
        block = _NUMERUS_RE.sub(
            lambda m: m.group(1) + _convert_element_text(m.group(2), True) + m.group(3),
            block,
        )
    else:
        block = _TRANSLATION_RE.sub(
            lambda m: m.group(1) + _convert_element_text(m.group(2), False) + m.group(3),
            block,
        )
    return block


def normalize(content: str) -> str:
    """Return *content* (a Qt ``.ts`` document) with contexts, placeholders and Markdown converted."""
    # Blank Loco's category names so every id resolves via qtTrId's empty-context lookup.
    content = _CONTEXT_NAME_RE.sub(r"\1\2", content)
    return _MESSAGE_RE.sub(lambda m: _normalize_message(m.group(0)), content)


def normalize_file(path: str) -> None:
    """Rewrite the Qt ``.ts`` file at *path* in place if normalization changes anything."""
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    converted = normalize(content)
    if converted == content:
        return

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(converted)
    logger.debug("Normalized Qt placeholders and markdown in %s", path)