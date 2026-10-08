#!/usr/bin/env bash
# Download every datasheet in manifest.tsv into this directory.
# Skips files already present; verifies each result is a PDF.
set -uo pipefail
cd "$(dirname "$0")"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
fail=0
while IFS=$'\t' read -r file lcsc mpn block url; do
  [[ -z "$file" || "$file" == \#* ]] && continue
  if [[ -s "$file" ]] && head -c4 "$file" | grep -q '%PDF'; then
    printf '%-28s ok (cached)\n' "$file"; continue
  fi
  code=$(curl -sSL -m 120 -A "$UA" -e 'https://www.lcsc.com/' -o "$file" -w '%{http_code}' "$url" 2>&1)
  if [[ -s "$file" ]] && head -c4 "$file" | grep -q '%PDF'; then
    printf '%-28s ok  %s  %s\n' "$file" "$code" "$(du -h "$file" | cut -f1)"
  else
    printf '%-28s FAIL http=%s type=%s\n' "$file" "$code" "$(file -b "$file" 2>/dev/null | cut -c1-40)"
    rm -f "$file"; fail=1
  fi
done < manifest.tsv
exit $fail
