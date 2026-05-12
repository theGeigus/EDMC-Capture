# EDMC Capture
A plugin for [Elite Dangerous Market Connector](https://github.com/Marginal/EDMarketConnector) that allows for:
- Conversion of the screenshot to alternate formats (.png / .jpeg)
- Renaming screenshots based on your in-game location
- Moving images to an alternate directory
- Importing images into Steam screenshots

## Installation
1. Install [Elite Dangerous Market Connector](https://github.com/Marginal/EDMarketConnector).
2. Download the plugin from [releases](https://github.com/theGeigus/EDMC-Capture/releases). This should be a .zip file.
3. Extract the .zip file into EDMC's plugins directory. This can be found by navigating to *File -> Settings -> Plugins -> Open Plugins Folder* within EDMC.
4. Restart EDMC to allow the plugin to load.

## Usage
1. **Required**: Supply the path of Elite Dangerous's image directory to the "*Elite image directory*" field. On Windows, this is likely "*C:\users\USERNAME\Pictures\Frontier Developments\Elite Dangerous*." Linux users will need to replace "*C:\\*" with their Wine/Proton prefix's path.
2. If desired, check "Move image" and supply a target directory for the image to be moved to.
3. If desired, check "Add to Steam" and supply your Steam screenshot directory. This can be found by clicking on an already taken screenshot on the game's library page (*Library -> Elite Dangerous -> Recordings and screenshots*). Then, right-click on the image and then "*show on disk*."
    - **Note**: The screenshot will only be added to Steam *after* Steam restarts.

## Note for Flatpak users
If using the Flatpak variant of EDMC, ensure the application has permission to access the Elite Dangerous photo directory, your Steam photo directory, and your target directory.

## Planned Features:
- [ ] Customizable naming format
- [ ] Auto detection of Elite's image path
- [ ] Auto Detection of Steam's screenshot path

## License
This project is licensed under the [GNU GPLv3](LICENSE).
