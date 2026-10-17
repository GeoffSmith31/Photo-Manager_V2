
#!/usr/bin/env bash
set -Eeuo pipefail

APP_NAME="Photo Manager"
INSTALL_DIR="${HOME}/.local/opt/photo-manager"
LAUNCHER_DIR="${HOME}/.local/share/applications"
LAUNCHER_FILE="${LAUNCHER_DIR}/photo-manager.desktop"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="${SOURCE_DIR}/PhotoManager"
APP_EXECUTABLE="${BUNDLE_DIR}/PhotoManager"
ICON_SOURCE="${BUNDLE_DIR}/_internal/photo_manager/resources/photo-manager.png"

missing=()

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

printf '%s\n' "=================================="
printf '%s\n' "       Photo Manager Installer"
printf '%s\n' "=================================="
printf '\n'

# Check the supported platform.
if [[ ! -f /etc/os-release ]]; then
    fail "Cannot identify this operating system."
fi

# shellcheck disable=SC1091
source /etc/os-release

if [[ "${ID:-}" != "ubuntu" ]]; then
    missing+=("Operating system: this installer currently supports Ubuntu only.")
fi

if [[ "$(uname -m)" != "x86_64" ]]; then
    missing+=("Architecture: this package requires 64-bit x86 (x86_64).")
fi

# Check that the packaged application and icon are present.
[[ -x "$APP_EXECUTABLE" ]] ||
    missing+=("Packaged executable not found or not executable: $APP_EXECUTABLE")

[[ -f "$ICON_SOURCE" ]] ||
    missing+=("Bundled application icon not found: $ICON_SOURCE")

# Check Google Chrome.
if ! command -v google-chrome >/dev/null 2>&1 &&
   ! command -v google-chrome-stable >/dev/null 2>&1; then
    missing+=("Google Chrome is not installed or is not in PATH.")
fi

# Check tools required to inspect system library dependencies.
if ! command -v ldconfig >/dev/null 2>&1; then
    missing+=("Required system command not found: ldconfig.")
elif ! ldconfig -p 2>/dev/null | grep 'libxcb-cursor\.so\.0' >/dev/null; then
    missing+=("Missing system library: libxcb-cursor.so.0 (Ubuntu package: libxcb-cursor0).")
fi

if ! command -v ldd >/dev/null 2>&1; then
    missing+=("Required system command not found: ldd.")
fi

# Check other runtime dependencies of the main executable and Qt X11 plugin.
if [[ -x "$APP_EXECUTABLE" ]]; then
    while IFS= read -r line; do
        missing+=("Executable dependency: $line")
    done < <(ldd "$APP_EXECUTABLE" 2>/dev/null | grep 'not found' || true)
fi

xcb_plugin="${BUNDLE_DIR}/_internal/PySide6/Qt/plugins/platforms/libqxcb.so"
if [[ -f "$xcb_plugin" ]]; then
    while IFS= read -r line; do
        missing+=("Qt X11 plugin dependency: $line")
    done < <(ldd "$xcb_plugin" 2>/dev/null | grep 'not found' || true)
fi

# Do not make any installation changes until all checks pass.
if (( ${#missing[@]} > 0 )); then
    printf '%s\n' "Installation cannot continue. The following prerequisites need attention:"
    printf '\n'
    for item in "${missing[@]}"; do
        printf '  - %s\n' "$item"
    done

    printf '\n'
    printf '%s\n' "For the known Ubuntu dependency, you can install it with:"
    printf '%s\n' "  sudo apt update"
    printf '%s\n' "  sudo apt install libxcb-cursor0"
    printf '\n'
    printf '%s\n' "Install the missing prerequisites, then run install.sh again."
    exit 1
fi

# Create the installation directories only after checks pass.
mkdir -p "$(dirname "$INSTALL_DIR")" "$LAUNCHER_DIR"

# Refuse to overwrite an existing installation without an explicit uninstall.
if [[ -e "$INSTALL_DIR" ]]; then
    fail "An installation already exists at $INSTALL_DIR. Run its uninstall.sh first."
fi

printf 'Installing %s to %s\n' "$APP_NAME" "$INSTALL_DIR"

# Copy to a temporary sibling directory, then rename into place.
temporary_dir="$(mktemp -d "${HOME}/.local/opt/photo-manager-install.XXXXXX")"
cleanup() {
    if [[ -n "${temporary_dir:-}" && -d "$temporary_dir" ]]; then
        rm -rf -- "$temporary_dir"
    fi
}
trap cleanup EXIT

cp -a "${BUNDLE_DIR}/." "$temporary_dir/"
cp -- "${SOURCE_DIR}/uninstall.sh" "$temporary_dir/uninstall.sh"
chmod 755 "$temporary_dir/uninstall.sh"

mv -- "$temporary_dir" "$INSTALL_DIR"
temporary_dir=""

# Create the application-menu launcher.
# If this fails, remove the partial installation and any partial launcher.
rollback_install() {
    printf '\n%s\n' "ERROR: Installation did not complete. Cleaning up..." >&2
    rm -f -- "$LAUNCHER_FILE"
    rm -rf -- "$INSTALL_DIR"
}

if ! cat > "$LAUNCHER_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Photo Manager
Comment=Manage and edit photo projects
Exec=${INSTALL_DIR}/PhotoManager
Terminal=false
Icon=${INSTALL_DIR}/_internal/photo_manager/resources/photo-manager.png
StartupWMClass=PhotoManager
Categories=Graphics;Utility;
EOF
then
    rollback_install
    exit 1
fi

if ! chmod 644 "$LAUNCHER_FILE"; then
    rollback_install
    exit 1
fi

printf '\n'
printf '%s\n' "Photo Manager was installed successfully."
printf '%s\n' "Application: $INSTALL_DIR/PhotoManager"
printf '%s\n' "Launcher:    $LAUNCHER_FILE"
printf '%s\n' "Uninstaller: $INSTALL_DIR/uninstall.sh"
printf '\n'
printf '%s\n' "Find Photo Manager in your desktop application menu."
