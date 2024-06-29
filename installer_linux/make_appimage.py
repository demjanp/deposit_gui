import os
import shutil
import subprocess

def create_apprun_script(app_dir):
    app_run_content = """#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/dep_gui/dep_gui" "$@"
"""
    apprun_path = os.path.join(app_dir, "AppRun")
    with open(apprun_path, "w") as f:
        f.write(app_run_content)
    os.chmod(apprun_path, 0o755)

def create_desktop_entry(app_dir):
    desktop_entry_content = """[Desktop Entry]
Name=Deposit GUI
Exec=dep_gui
Icon=deposit_icon
Type=Application
Categories=Utility;
"""
    desktop_entry_path = os.path.join(app_dir, "deposit_gui.desktop")
    with open(desktop_entry_path, "w") as f:
        f.write(desktop_entry_content)

def copy_application_files(source_dir, app_dir):
    dest_dir = os.path.join(app_dir, "dep_gui")
    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

def copy_icon(source_dir, app_dir):
    icon_source = os.path.join(source_dir, "deposit_gui", "res", "deposit_icon.png")
    icon_dest_dir = os.path.join(app_dir, "usr", "share", "icons", "hicolor", "256x256", "apps")
    os.makedirs(icon_dest_dir, exist_ok=True)
    shutil.copy2(icon_source, os.path.join(icon_dest_dir, "deposit_icon.png"))
    shutil.copy2(icon_source, os.path.join(app_dir, "deposit_icon.png"))

def build_appimage(app_dir, output_dir):
    os.chdir(output_dir)
    appimagetool_path = "appimagetool-x86_64.AppImage"
    if not os.path.exists(appimagetool_path):
        url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        subprocess.run(["wget", url, "-O", appimagetool_path], check=True)
        os.chmod(appimagetool_path, 0o755)
    subprocess.run(["./" + appimagetool_path, "deposit_gui.AppDir", "deposit_gui.AppImage"], check=True)

def main():
    source_dir = "dist/dep_gui"
    output_dir = "dist"
    app_dir = os.path.join(output_dir, "deposit_gui.AppDir")

    # Clean up any existing AppDir
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)

    os.makedirs(app_dir)
    
    create_apprun_script(app_dir)
    create_desktop_entry(app_dir)
    copy_application_files(source_dir, app_dir)
    copy_icon(source_dir, app_dir)
    build_appimage(app_dir, output_dir)
    
    print("AppImage creation completed successfully.")

if __name__ == "__main__":
    main()
