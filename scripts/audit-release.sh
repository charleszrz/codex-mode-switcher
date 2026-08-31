#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

fail=0
forbidden_paths='(^|/)(\.git|\.DS_Store|__pycache__|node_modules|dist|build|target|switch-backups|backups|logs|[^/]+\.egg-info)(/|$)|(^|/)auth[^/]*\.json$|(^|/)config[^/]*\.toml$|\.(pem|key|p12|pfx)$'
secret_patterns='(gh[pousr]_[[:alnum:]_]{20,}|sk-[[:alnum:]_-]{16,}|xox[baprs]-[[:alnum:]-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|OPENAI_API_KEY[[:space:]]*[:=][[:space:]]*[^[:space:]]+)'
local_path_patterns='(/User''s/|C:\\User''s\\)'

while IFS= read -r -d '' file; do
  relative="${file#./}"
  if [[ "$relative" =~ $forbidden_paths ]]; then
    echo "forbidden release artifact: $relative" >&2
    fail=1
  fi
done < <(find . \( -path './.git' -o -path '*/__pycache__' -o -path '*/node_modules' -o -path './dist' -o -path './build' -o -path './target' -o -path '*.egg-info' \) -prune -o -type f -print0)

if git ls-files | rg -n -e "$forbidden_paths"; then
  echo "forbidden generated artifact is tracked" >&2
  fail=1
fi

if rg -n -I -e "$secret_patterns" -e "$local_path_patterns" --glob '!.git/**' .; then
  echo "possible secret or local path found" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo "release audit passed"
