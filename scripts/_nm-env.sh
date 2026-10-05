# Sourced by scripts/nm-test.sh and scripts/nm-lint.sh.
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
env_dir="${NM_ENV_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/fm-envs/data-buffet}"

# Linux node/npm only: drop any Windows (/mnt/<drive>) PATH entries.
PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -v '^/mnt/[a-z]/' | paste -sd: -)"
export PATH
command -v node >/dev/null && command -v npm >/dev/null \
  || { echo "nm: Linux node/npm not found on PATH" >&2; exit 1; }

version="$(sed -n 's/^dataformCoreVersion:[[:space:]]*"\{0,1\}\([0-9][^"[:space:]]*\)"\{0,1\}.*$/\1/p' "$repo/workflow_settings.yaml" | head -n1)"
[ -n "$version" ] || { echo "nm: dataformCoreVersion not found in workflow_settings.yaml" >&2; exit 1; }

mkdir -p "$env_dir"
env_dir="$(cd "$env_dir" && pwd -P)"
cli="$env_dir/node_modules/.bin/dataform"
stamp="$env_dir/.dataform-version"
if [ ! -x "$cli" ] || [ ! -f "$env_dir/node_modules/@dataform/core/package.json" ] || [ "$(cat "$stamp" 2>/dev/null)" != "$version" ]; then
  echo "nm: installing @dataform/cli@$version and @dataform/core@$version into $env_dir"
  rm -f "$stamp"
  (cd "$env_dir" && { [ -f package.json ] || echo '{"private":true}' > package.json; } \
    && npm install --save-exact --no-audit --no-fund --loglevel=error "@dataform/cli@$version" "@dataform/core@$version")
  echo "$version" > "$stamp"
else
  echo "nm: reusing @dataform/cli@$version and @dataform/core@$version from $env_dir"
fi

python="$env_dir/venv/bin/python"
bq_version="3.25.0"
stamp="$env_dir/.bigquery-version"
if [ ! -x "$python" ] || [ "$(cat "$stamp" 2>/dev/null)" != "$bq_version" ]; then
  command -v python3 >/dev/null || { echo "nm: python3 not found on PATH" >&2; exit 1; }
  echo "nm: installing google-cloud-bigquery==$bq_version into $env_dir/venv"
  rm -f "$stamp"
  python3 -m venv "$env_dir/venv"
  "$python" -m pip install --disable-pip-version-check "google-cloud-bigquery==$bq_version"
  echo "$bq_version" > "$stamp"
fi

nm_compile() (
  compile_dir="$(mktemp -d "$env_dir/project.XXXXXX")"
  trap 'rm -rf "$compile_dir"' EXIT
  cp -R "$repo/definitions" "$repo/includes" "$compile_dir/"
  sed '/^dataformCoreVersion:/d' "$repo/workflow_settings.yaml" > "$compile_dir/workflow_settings.yaml"
  cp "$env_dir/package.json" "$compile_dir/package.json"
  ln -s "$env_dir/node_modules" "$compile_dir/node_modules"
  "$cli" compile "$compile_dir" --json
)
