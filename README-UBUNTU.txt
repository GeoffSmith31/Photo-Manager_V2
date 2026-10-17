# Photo Manager — Ubuntu Installation

## Supported platform

This package is intended for Ubuntu on 64-bit x86 systems (x86_64).

Ubuntu 24.04 LTS has been tested. Other Ubuntu versions may work but have not necessarily been tested.

## Prerequisites

Photo Manager is distributed as a packaged application. Python does not need to be installed separately.

**Google Chrome**

Google Chrome must be installed and available as either `google-chrome` or `google-chrome-stable`. Photo Manager uses an external browser and does not include Chrome in its package.

**System libraries**

The application uses Qt for its desktop interface. On Ubuntu, the Qt X11 platform plugin may require `libxcb-cursor0`.

If the installer reports that this library is missing, open a terminal and run:

```bash
sudo apt update
sudo apt install libxcb-cursor0
```

The installer checks for Google Chrome and known runtime dependencies. It reports missing prerequisites and stops rather than attempting to install system packages automatically.

## Installation

1. Extract the Photo Manager distribution package.
2. Open a terminal in the extracted directory.
3. Run:

   ```bash
   ./install.sh
   ```

4. Follow any instructions if prerequisites are missing.

The installer places the application in:

`~/.local/opt/photo-manager/`

It creates a desktop launcher in:

`~/.local/share/applications/photo-manager.desktop`

After successful installation, find **Photo Manager** in your desktop application's menu.

## Uninstallation

To remove Photo Manager, open a terminal and run:

```bash
~/.local/opt/photo-manager/uninstall.sh
```

The uninstaller asks for confirmation before removing the application and its desktop launcher.

**Important:** The uninstaller is stored inside the installed application directory, rather than in the desktop menu. This is intentional.

Uninstallation preserves the following user data:

- Settings: `~/.config/photo_manager/`
- Application data and logs: `~/.local/share/photo_manager/`
- Photo projects and workspaces in their configured locations

These items are not removed by the uninstaller.

## Troubleshooting

If the application fails to start, check that Google Chrome is installed and that the system libraries reported by the installer are available.

If the application is not visible in the desktop application menu immediately after installation, refresh the desktop session or log out and back in.

When reporting a problem, include the Ubuntu version, the error message, and the application log if available.

## Verifying the Download

The release archive is accompanied by a SHA-256 checksum file:

`PhotoManager-2.0.0-ubuntu-x86_64.tar.gz.sha256`

Before extracting the archive, verify its integrity by placing both files in the same directory and running:

```bash
sha256sum -c PhotoManager-2.0.0-ubuntu-x86_64.tar.gz.sha256
```

A result of `OK` confirms that the archive matches the published checksum.
