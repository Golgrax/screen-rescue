#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== 1. Building Standalone Binary with PyInstaller ==="
rm -rf build dist AppDir
pyinstaller --noconfirm --onedir --windowed \
    --name "screen-rescue" \
    --add-data "icon.png:." \
    --add-data "evgrab:." \
    --icon "icon.png" \
    main.py

echo "=== 2. Creating AppDir Structure ==="
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/applications

cp -r dist/screen-rescue/* AppDir/usr/bin/
cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/screen-rescue.png
cp icon.png AppDir/icon.png
cp screen-rescue.desktop AppDir/
cp screen-rescue.desktop AppDir/usr/share/applications/

# Create AppRun
cat << 'APPRUN' > AppDir/AppRun
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
exec "${HERE}/usr/bin/screen-rescue" "$@"
APPRUN
chmod +x AppDir/AppRun

echo "=== 3. Downloading appimagetool if needed ==="
if [ ! -f "appimagetool" ]; then
    echo "Downloading appimagetool..."
    curl -sL -o appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool
fi

echo "=== 4. Packaging into AppImage ==="
ARCH=x86_64 ./appimagetool --appimage-extract-and-run AppDir ScreenRescue-x86_64.AppImage

chmod +x ScreenRescue-x86_64.AppImage
echo "=== 5. Copying to ~/Applications/ ==="
mkdir -p "$HOME/Applications"
cp ScreenRescue-x86_64.AppImage "$HOME/Applications/"

echo "=== ScreenRescue AppImage built successfully ==="
ls -lh ScreenRescue-x86_64.AppImage
