
#!/usr/bin/env bash
set -Eeuo pipefail

INSTALL_DIR="${HOME}/.local/opt/photo-manager"
LAUNCHER_FILE="${HOME}/.local/share/applications/photo-manager.desktop"

printf '%s\n' "=================================="
printf '%s\n' "      Photo Manager Uninstaller"
printf '%s\n' "=================================="
printf '\n'

if [[ ! -d "$INSTALL_DIR" ]]; then
    printf 'Photo Manager is not installed at:\n  %s\n' "$INSTALL_DIR"
    exit 1
fi

printf 'This will remove the Photo Manager application from:\n  %s\n' "$INSTALL_DIR"
printf '\n'
printf '%s\n' "Your settings, logs, and photo projects will not be removed."
printf '\n'
read -r -p "Continue with uninstallation? [y/N] " answer

case "$answer" in
    y|Y|yes|YES|Yes) ;;
    *)
        printf '%s\n' "Uninstallation cancelled."
        exit 0
        ;;
esac

# Remove the desktop launcher first.
if [[ -f "$LAUNCHER_FILE" ]]; then
    rm -- "$LAUNCHER_FILE"
    printf 'Removed launcher: %s\n' "$LAUNCHER_FILE"
fi

# Remove the installed application, including this script.
rm -rf -- "$INSTALL_DIR"

printf '\n'
printf '%s\n' "Photo Manager has been uninstalled."
printf '%s\n' "User settings, logs, and photo projects were preserved."
