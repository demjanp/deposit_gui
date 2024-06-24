### Build a Windows installer for Deposit GUI

Open Windows Console

Go to the folder deposit_gui\installer_win

Execute the following command:

```
build.bat <setup file directory>
```

For example: ```build.bat c:\temp```

Make sure to use absolute paths!

This will create a Windows executable build of Deposit GUI in the directory deposit_gui\dist and place the file deposit_installer.ifp in the specified setup file directory.

Run [InstallForge](https://installforge.net/) (tested on version 1.4.3)
Open the file deposit_installer.ifp
Click on Build

This will create a setup file named deposit_{version}_setup.exe in the specified setup file directory.
