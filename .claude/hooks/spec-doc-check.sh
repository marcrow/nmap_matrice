#!/usr/bin/env bash
# PostToolUse (Write|Edit): a spec or ticket under .scratch/ changed -> remind to update the user docs.
f=$(jq -r '.tool_input.file_path // .tool_response.filePath // empty')
[[ "$f" =~ /\.scratch/[^/]+/(spec\.md|issues/[^/]+\.md)$ ]] || exit 0
jq -n --arg f "$f" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext:
  ("Spec or ticket changed (" + $f + "). Check the user docs this changes and update them in the same work: docs/guide/*.md, docs/index.md, README.md, and the app Overview (segowl/assets/overview.html). If a gesture, rule, file format or screen changes, the page that describes it changes too; if nothing in the docs is affected, say so in one line.")}}'
