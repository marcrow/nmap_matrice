# Source View: most permissive state wins, not most recent

When several Scans from the same Source disagree on a port, the Source View keeps the most permissive state (open > closed > filtered), not the latest one. In an audit an open port observed once is proof the flow passed, whereas a filtered result proves nothing (packet loss, aggressive timing, a different scan type). "It has been fixed since" is answered by a Scan Diff between the two Scans, not by the merged view. The disagreement is always surfaced to the auditor, so this rule is never silent.
