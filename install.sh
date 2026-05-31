#!/bin/sh

set -eu

REPO_URL=${SOURCE_REPO_URL:-}
ASSUME_YES=${ASSUME_YES:-0}
PROJECT_ROOT=${PROJECT_ROOT:-}
SOURCE_ROOT=""
SOURCE_SKILLS_DIR=""
TEMP_DIR=""

die() {
  printf '%s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}

trap cleanup EXIT HUP INT TERM

usage() {
  cat <<'EOF'
Usage: ./install.sh [--repo-url URL] [--project-root PATH] [--yes]

Interactive installer for the repository's bundled Codex skills.

Options:
  --repo-url URL      Clone from URL when the local .codex/skills tree is missing.
  --project-root PATH  Use PATH as the project root when project scope is chosen.
  --yes               Skip confirmation prompts where possible.
  -h, --help          Show this help text.
EOF
}

prompt_line() {
  label=$1
  default=${2:-}

  if [ -n "$default" ]; then
    printf '%s [%s]: ' "$label" "$default" >&2
  else
    printf '%s: ' "$label" >&2
  fi

  IFS= read -r reply <&3 || return 1

  if [ -z "$reply" ]; then
    reply=$default
  fi

  printf '%s\n' "$reply"
}

prompt_yes_no() {
  question=$1
  default=${2:-n}

  while :; do
    if [ "$default" = "y" ]; then
      suffix='[Y/n]'
    else
      suffix='[y/N]'
    fi

    printf '%s %s ' "$question" "$suffix" >&2
    IFS= read -r reply <&3 || return 1
    reply=${reply:-$default}

    case "$reply" in
      y|Y|yes|YES) return 0 ;;
      n|N|no|NO) return 1 ;;
      *) printf 'Please answer y or n.\n' >&2 ;;
    esac
  done
}

prompt_scope() {
  while :; do
    printf 'Install scope: [g]lobal/user or [p]roject? ' >&2
    IFS= read -r scope <&3 || return 1

    case "$scope" in
      g|G|global|user) printf '%s\n' 'global' ; return 0 ;;
      p|P|project) printf '%s\n' 'project' ; return 0 ;;
      *) printf 'Please choose global/user or project.\n' >&2 ;;
    esac
  done
}

abspath_existing_dir() {
  target=$1
  (
    cd "$target" 2>/dev/null && pwd -P
  ) || return 1
}

clone_repo_if_needed() {
  repo_url=$1

  [ -n "$repo_url" ] || return 1
  command -v git >/dev/null 2>&1 || die "git is required to clone the repository source."

  TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/openspec-skill-installer.XXXXXX" 2>/dev/null || mktemp -d)
  git clone --depth 1 "$repo_url" "$TEMP_DIR" >/dev/null 2>&1 || die "Failed to clone repository from $repo_url"
  SOURCE_ROOT=$TEMP_DIR
  SOURCE_SKILLS_DIR=$SOURCE_ROOT/.codex/skills
}

resolve_source_tree() {
  script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
  local_source="$script_dir/.codex/skills"

  if [ -d "$local_source" ]; then
    SOURCE_ROOT=$script_dir
    SOURCE_SKILLS_DIR=$local_source
    return 0
  fi

  clone_repo_if_needed "$REPO_URL"
}

resolve_global_destination() {
  if [ -n "${CODEX_HOME:-}" ]; then
    printf '%s/skills\n' "$CODEX_HOME"
  else
    printf '%s/.codex/skills\n' "$HOME"
  fi
}

resolve_project_destination() {
  project_root=$1
  printf '%s/.codex/skills\n' "$project_root"
}

is_within_path() {
  child=$1
  parent=$2

  case "$child" in
    "$parent"|"$parent"/*) return 0 ;;
    *) return 1 ;;
  esac
}

copy_skill_dir() {
  skill_source=$1
  skill_dest=$2

  cp -R "$skill_source" "$skill_dest"
}

main() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --repo-url)
        [ $# -ge 2 ] || die "--repo-url requires a value"
        REPO_URL=$2
        shift 2
        ;;
      --repo-url=*)
        REPO_URL=${1#*=}
        shift
        ;;
      --project-root)
        [ $# -ge 2 ] || die "--project-root requires a value"
        PROJECT_ROOT=$2
        shift 2
        ;;
      --project-root=*)
        PROJECT_ROOT=${1#*=}
        shift
        ;;
      --yes|-y)
        ASSUME_YES=1
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        die "Unknown option: $1"
        ;;
    esac
  done

  exec 3</dev/tty || die "This installer needs an interactive terminal."

  resolve_source_tree

  [ -d "$SOURCE_SKILLS_DIR" ] || die "Could not find a .codex/skills source tree. Run this from a clone or pass --repo-url."

  source_root_abs=$(abspath_existing_dir "$SOURCE_ROOT") || die "Unable to resolve the source repository root: $SOURCE_ROOT"

  scope=$(prompt_scope)

  case "$scope" in
    global)
      DESTINATION=$(resolve_global_destination)
      ;;
    project)
      if [ -n "$PROJECT_ROOT" ]; then
        project_root_input=$PROJECT_ROOT
      else
        project_root_input=$(prompt_line "Project root" "$(pwd)")
      fi

      [ -d "$project_root_input" ] || die "Project root does not exist: $project_root_input"
      project_root_abs=$(abspath_existing_dir "$project_root_input") || die "Unable to resolve project root: $project_root_input"

      if is_within_path "$project_root_abs" "$source_root_abs"; then
        die "Project root points inside the source repository. Choose a different project directory."
      fi

      DESTINATION=$(resolve_project_destination "$project_root_abs")
      ;;
    *)
      die "Unknown install scope: $scope"
      ;;
  esac

  printf 'Source: %s\n' "$SOURCE_SKILLS_DIR"
  printf 'Destination: %s\n' "$DESTINATION"

  if is_within_path "$DESTINATION" "$source_root_abs"; then
    die "Destination points inside the source repository. Choose a different project or global target."
  fi

  if [ "$ASSUME_YES" -eq 0 ] && ! prompt_yes_no "Proceed with installation?" "y"; then
    die "Installation cancelled."
  fi

  mkdir -p "$DESTINATION" || die "Unable to create destination directory: $DESTINATION"

  installed=0
  skipped=0
  overwritten=0

  found_any=0
  for skill_source in "$SOURCE_SKILLS_DIR"/*; do
    [ -d "$skill_source" ] || continue
    found_any=1
    skill_name=$(basename "$skill_source")
    skill_dest="$DESTINATION/$skill_name"

    if [ -e "$skill_dest" ] || [ -L "$skill_dest" ]; then
      if [ "$ASSUME_YES" -eq 1 ] || prompt_yes_no "Overwrite existing skill '$skill_name'?" "n"; then
        rm -rf "$skill_dest"
        copy_skill_dir "$skill_source" "$skill_dest"
        overwritten=$((overwritten + 1))
        printf 'Overwrote %s\n' "$skill_name"
      else
        skipped=$((skipped + 1))
        printf 'Skipped %s\n' "$skill_name"
      fi
    else
      copy_skill_dir "$skill_source" "$skill_dest"
      installed=$((installed + 1))
      printf 'Installed %s\n' "$skill_name"
    fi
  done

  [ "$found_any" -eq 1 ] || die "No skills were found under $SOURCE_SKILLS_DIR"

  printf '\nDone.\n'
  printf 'Installed: %s\n' "$installed"
  printf 'Overwritten: %s\n' "$overwritten"
  printf 'Skipped: %s\n' "$skipped"
  printf 'Target: %s\n' "$DESTINATION"
}

main "$@"
