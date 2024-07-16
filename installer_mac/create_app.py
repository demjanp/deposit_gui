from deposit_gui import __version__
import os
import plistlib
import shutil

# Define the app structure and info plist
app_name = 'dist/Deposit.app'
app_icon = 'src/deposit_gui/res/deposit_icon.icns'
bundle_identifier = 'com.thelapteam.depositgui'
dep_gui_src = 'dist/dep_gui'
info_plist = {
    'CFBundleName': 'DepositGUI',
    'CFBundleDisplayName': 'Deposit GUI',
    'CFBundleVersion': __version__,
    'CFBundleShortVersionString': ".".join(__version__.split(".")[:2]),
    'NSHighResolutionCapable': 'True',
    'CFBundleDevelopmentRegion': 'English',
    'LSMinimumSystemVersion': '11',
    'CFBundleExecutable': 'dep_gui',
    'CFBundleIconFile': 'deposit_icon.icns',
}

# Create directory structure
def create_directory_structure(app_name):
    os.makedirs(os.path.join(app_name, 'Contents', 'MacOS'), exist_ok=True)
    os.makedirs(os.path.join(app_name, 'Contents', 'Resources'), exist_ok=True)
    os.makedirs(os.path.join(app_name, 'Contents', 'Frameworks'), exist_ok=True)

# Write Info.plist
def write_info_plist(app_name, info_plist):
    plist_path = os.path.join(app_name, 'Contents', 'Info.plist')
    with open(plist_path, 'wb') as plist_file:
        plistlib.dump(info_plist, plist_file)

# Copy icon file
def copy_icon_file(app_name, app_icon):
    resources_path = os.path.join(app_name, 'Contents', 'Resources')
    os.makedirs(resources_path, exist_ok=True)
    if os.path.exists(app_icon):
        shutil.copy(app_icon, resources_path)

# Copy dep_gui contents to MacOS directory
def copy_dep_gui(app_name, dep_gui_src):
    macos_dest = os.path.join(app_name, 'Contents', 'MacOS')
    if os.path.exists(dep_gui_src):
        try:
            shutil.copytree(dep_gui_src, macos_dest, dirs_exist_ok=True)
        except shutil.Error as e:
            print(f"Error during copying dep_gui: {e}")

# Main function to create the app package
def create_app_package():
    create_directory_structure(app_name)
    copy_icon_file(app_name, app_icon)
    copy_dep_gui(app_name, dep_gui_src)
    write_info_plist(app_name, info_plist)
    print(f'{app_name} has been created successfully.')

if __name__ == "__main__":
    create_app_package()
