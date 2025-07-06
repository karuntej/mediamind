import re, html

def highlight_terms(query: str, text: str) -> str:
    """Return HTML where query terms are wrapped in <mark>."""
    if not query:
        return html.escape(text)
    terms = [re.escape(t) for t in query.split() if t]
    if not terms:
        return html.escape(text)
    pattern = re.compile(r"(" + "|".join(terms) + r")", re.IGNORECASE)
    def repl(match):
        return f"<mark>{html.escape(match.group(0))}</mark>"
    return pattern.sub(repl, html.escape(text))
