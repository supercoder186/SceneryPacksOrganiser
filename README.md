# Scenery Pack Organiser XP10/11/12

Are you tired of sifting through all the packs in the Custom Scenery folder and reordering them manually?\
Do you hate having to start X-Plane and quit just to add new scenery packs to the file so you can reorganise it?\
This simple script is for you!


## Installation
Whether you use the .py script or standalone executable version, you can store the program anywhere you'd like.
### Script (.py) version
- You need to have Python3 installed. [You can get it here for all platforms](https://www.python.org/downloads/).
    - [For macOS, you can also use Homebrew](https://docs.python-guide.org/starting/install3/osx/).
    - For Linux, you can also use your distro's package manager.
- You need to have PIP installed. To check, open Command Prompt or Terminal and do `pip --version`

Make sure both Python3 and PIP are added to PATH.\
If you have something more elaborate set up, please ensure the following libraries are available: `glob locale os pathlib pkg_resources struct sys time`, and also `pywin32` if you're on Windows.
### Standalone executable
You do not need anything installed on your system (not even Python) if you're using the standalone executable. Simply download the one for your OS.\
Currently, only Windows and Linux executables are available. macOS executables and CLI install options are coming soon.


## Usage
### How to run
- On Windows, you can simply doubleclick the program. This works for both the .exe and the .py script.
- On macOS, you will need to open Terminal in the folder you have the program stored. 
    - If you're using the .py script, do `python organiser_v2.0b4.py`
    - mac standalone executables are coming soon
- On Linux, you will need to open Terminal in the folder you have the program stored.
    - If you're using the .py script, do `python3 organiser_v2.0b4.py`
    - If you're using the executable, do `./organiser_v2.0b4`
### Prompts and responses
At various stages, the program might ask you for input. Here I'll go through them in order and explain each one.
1. The program will try to automatically locate X-Plane. It will list out all locations it finds. To use one of those, enter the serial number as displayed in the list. If this doesn't work or if you want to use a different location, simply paste the path from your file explorer. **Do not format it as a shell path (eg. wrapping it in quotes, escaping backslashes)**
2. If you had disabled some scenery packs in your old scenery_packs.ini, the program will offer to retain those in the new ini. You can respond with yes/no or y/n.
3. The program checks for conflicts in your Custom Airports (based on their ICAO codes). If it find any, it will tell you the ICAO code, and will list the Airport name and its folder name. To resolve it, enter the serial numbers as shown in the list in descending order of priority (highest first, lowest last).


## Features
- Sorts scenery packs according to the required hierarchy:
    - Custom Airports
    - Default Airports
    - Prefab Airports
    - Global Airports
    - Scenery Plugins
    - Scenery Libraries
    - Custom Overlays
    - Default Overlays
    - Orthophotos
    - Terrain Meshes
- Supports Windows shortcuts (.LNK files, eg. for SAM Library)
- Supports [Prefab Airports](https://forums.x-plane.org/index.php?/files/file/27582-prefab-scenery-for-25000-airports/) (requires you to retain "prefab" somewhere in the folder name for it to work)
- Attempts to locate X-Plane installs automatically, letting you choose between the results or manually inputting an X-Plane install path
- Offers to carry over SCENERY_PACK_DISABLED from existing scenery_packs.ini
- Checks for Custom Airport conflicts and resolves them with user input
- Will warn you of folders-in-folder (It's more common than you'd think)
- Supports XP10/11's and XP12's Global Airports entry simultaneously


## Credits/Changelog
A big thank-you to [@supercoder186](https://github.com/supercoder186/), for his superb utility and encouragement.\
If you would like to contribute, [here is the project GitHub](https://github.com/therectifier/SceneryPacksOrganiser/).\
Feel free to message me on Discord - my username is **therectifier**. I'm also present in the X-Plane Community and Official servers.

- 1.0 - Initial Upload
- 1.1 - UI improvement: wait for user confirmation before exiting
- 1.2 - Added Windows shortcut (.LNK) support and code comments
- 1.3.0 - Added XP12 support. Sort Default below Custom Airports
- 1.3.1 - Fixed packs getting jumbled
- 1.3.2 - Fixed syntax error (I have no clue how this crept in)
- 1.4b1 - Now attempt to locate XP installs (only available for direct downloads)
- **Skipped 1.4 release - I went overboard with the changes and ended up rewriting the whole thing**
- 2.0b1 - Now parse apt.dat to verify if a pack is an airport. Now sort Default below Custom Overlays. Now alphabetically sort each layer. Now support "Earth Nav data" and other non-conventional capitalisations within packs
- 2.0b2 - Now check for Custom Airport conflicts and resolve with user input. Removed X-Plane 9 support (never worked to begin with). UI improvements: Now leave gaps in console to differentiate stages, Added timer for each stage
- 2.0b3 - Now treat Prefab Airports as its own thing to avoid clashes with Default or Custom Airports
- 2.0b4 - Now offer to carry over DISABLED tags from existing ini. Fixed Windows shortcut support. 


## Known Issues
- Automatic location of X-Plane installs doesn't work for Steam users. This is because Steam doesn't use the same mechanism used by the X-Plane installer, which is also what this program uses. There is no timeline for getting this one fixed - if you would like to contribute, I would urge you to check out the project GitHub.
- Meshes such as AlpilotX's HD/UHD Mesh get treated as overlays. This is because on the surface, they look identical. Only by parsing the DSF is it possible to discern the two - some code for this has been written but it's incomplete. I'm not sure exactly when, but this will be addressed in 2.0 release 1.
