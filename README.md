# EDMC Capture
A plugin for [Elite Dangerous Market Connector](https://github.com/Marginal/EDMarketConnector) that allows for:
- Conversion of the screenshot to alternate formats (.png / .jpg)
- Renaming screenshots based on your current in-game location
- Moving images to an alternate directory
- Importing images into your Steam screenshot library
- Cross platform, works on both Windows and Linux

## Installation
1. Install [Elite Dangerous Market Connector](https://github.com/Marginal/EDMarketConnector).
2. Download the latest plugin release from [Releases](https://github.com/theGeigus/EDMC-Capture/releases) (.zip file).
3. Extract the .zip file into EDMC's plugins directory.
    - You can open this folder from within EDMC via *File → Settings → Plugins → Open Plugins Folder*.
    - **Note** The plugin files must be in their own folder. The layout should look like: `.../plugins/EDMC Capture/load.py`
4. Restart EDMC.

## Setup
1. **Required**: Supply the path of Elite Dangerous's image directory to the "*Elite image directory*" field.
    - **Windows**: this is usually just `C:\Users\USERNAME\Pictures\Frontier Developments\Elite Dangerous`.
    - **Linux**: Replace `C:\` with your Wine/Proton prefix's path. Remember `.../users/` is lowercase here.
        - For steam users, this is most likely `~/.steam/steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Pictures/Frontier Developments/Elite Dangerous`
2. Set the name of the target file, see **Name Format** for more information
3. (Optional) Enable "*Move image*" and supply a target directory for the image to be moved to.
4. (Optional) Enable "*Add to Steam*" and supply your Steam screenshot directory.
    - This can be found by opening an already taken screenshot on the game's library page (*Library → Elite Dangerous → Recordings and screenshots*). Right-click on the image and then "*show on disk*."
    - **Note**: The screenshot will only be added to Steam *after* Steam restarts.

Once configured, simply take a screenshot in-game using your Elite Dangerous keybind (F10). The plugin handles the rest automatically.

## Naming Format

Files can be named using a template. The following keys can be used:

|Variable       |Description                                                |Example        |
|---------------|-----------------------------------------------------------|---------------|
|`{system}`     |Current star system                                        |`Altair`       |
|`{body}`       |Nearest planetary body (if any, otherwise "Deep Space")    |`Darkes Hollow`|
|`{station}`    |Nearest station (if any, otherwise "Unknown")              |`Solo Orbiter` |
|`{location}`   |Same as `{station}` if available, otherwise `{body}`       |`Solo Orbiter` |
|`{ship}`       |The name of your current ship                              |`Teapot`       |
|`{ship_id}`    |The ID of your current ship                                |`ER-418`       |
|`{elite_year}` |In-game year                                               |`3312`         |
|`{year}`       |Real-world year                                            |`2026`         |
|`{month}`      |Month (01-12)                                              |`05`           |
|`{day}`        |Day (01-31)                                                |`12`           |
|`{hour}`       |Hour (00-23)                                               |`14`           |
|`{minute}`     |Minute (00-59)                                             |`35`           |
|`{second}`     |Second (00-59)                                             |`08`           |

**Default template**: `{elite_year}-{month}-{day} {hour}_{minute}_{second} ({system} - {location})`

**Note**: You can use `/` in your format to automatically sort screenshots into folders
- Example: `{system}/{year}_{month}_{day}` will create a folder for the star system.

## Note for Flatpak users
If using the Flatpak variant of EDMC, ensure the application has permission to access the Elite Dangerous photo directory and permission to write to your Steam photo directory and your target directory.

## Planned Features:
- [x] Customizable naming format for screenshots
- [ ] Auto detection of Elite's image path (or just autofill Windows path)
- [ ] Auto Detection of Steam's screenshot path (via .vdf)

## License
This project is licensed under the [GNU GPLv3](LICENSE).
