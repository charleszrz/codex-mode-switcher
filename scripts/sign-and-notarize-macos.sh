#!/usr/bin/env bash
# Sign and notarize a locally built macOS .app. This script deliberately
# requires a Developer ID identity and a local notarytool Keychain profile;
# neither certificate material nor App Store credentials belong in this repo.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <Developer ID Application identity> <path-to-app> <notarytool-keychain-profile>" >&2
  exit 64
fi

identity=$1
app_path=$2
notary_profile=$3

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This release step must run on macOS." >&2
  exit 69
fi
if [[ ! -d "$app_path" || "${app_path##*.}" != "app" ]]; then
  echo "Expected a .app bundle: $app_path" >&2
  exit 66
fi

codesign --force --deep --options runtime --timestamp --sign "$identity" "$app_path"
codesign --verify --deep --strict --verbose=2 "$app_path"

archive_path="${app_path%.app}-notarization.zip"
ditto -c -k --keepParent "$app_path" "$archive_path"
xcrun notarytool submit "$archive_path" --keychain-profile "$notary_profile" --wait
xcrun stapler staple "$app_path"
spctl --assess --type execute --verbose=4 "$app_path"

echo "Signed, notarized, stapled: $app_path"
