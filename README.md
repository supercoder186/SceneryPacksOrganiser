# Scenery Pack Organiser

Are you tired of having to manually sift through all the packs in the Custom Scenery folder and having to reorder them manually?\
Do you hate having to start X-Plane and quit just to add new scenery packs to the file so you can reorganise it?\
This simple script is for you!\
It automatically detects all the folders in the Custom Scenery folder (and the SAM Scenery Library in the plugins folder), sorts them and then writes a scenery_packs.ini file!

### Features:
- Sorts scenery packs according to the required hierarchy (Custom Airport, Default Airport, Scenery Plugin, Library, Custom Overlay, Default Overlay, Ortho, Mesh)
- Will warn you of folders-in-folder (It's more common than you'd think :))
- Supports Windows shortcuts (.LNK files, eg. for SAM Library)
- Ensures Global Airports entry at the end of Airports section and also supports XP12's style of Global Airport entry
- Segregates Default (ie. Global Airports, Demo Areas, X-Plane Airports, Aerosoft Airports, X-Plane Landmarks) and Custom Airports
- Attempts to locate XP installs automatically, and lets you choose between the results or manually inputting a filepath
- *(New in 2.0 beta 1)*
- *Segregates Default (ie. X-Plane Landmarks) and Custom Overlays*


### Requirements:
You need to have Python 3 installed. [You can get it here for Windows and macOS](https://www.python.org/downloads/). [Alternatively for macOS, you can use Homebrew](https://docs.python-guide.org/starting/install3/osx/). For Linux, you can use your distro's package manager.
You also need to have PIP (Python's package installer) installed. To check, open Command Prompt or your Terminal and do `pip --version`.


### Installation/Usage:
There is no real installation process. The program will automatically download and install any required libraries, provided you have PIP installed.
To run, simply double-click the file. **If this doesn't work, open a Terminal in the folder you have the script and do `python3 organiser.py` or `python organiser.py`.**

The program will try to locate your X-Plane installs, and it will offer a choice to use those. If this doesn't work, or if you want to use a different install, simply paste the path to your X-Plane install. **Do not format the path as a shell path. Simply paste the path as-is.**
The backup "scenery_packs.ini.bak" will be stored in the same place as the real "scenery_packs.ini". Do keep in mind this backup will be overwritten every time you run the organiser.


### Credits/Changelog:
Thanks once again to [@supercoder186](https://github.com/supercoder186/) for your superb utility and for your permission and encouragement. If you would like to take a look at the source code or contribute, [here is the project GitHub](https://github.com/therectifier/SceneryPacksOrganiser/).
Feel free to message me on Discord - my username is **therectifier**. I'm also present in the XP Community and Official servers.

1.0 - Initial Upload
1.1 - UI Improvement: Wait for user confirmation before exiting
1.2 - Add shortcut (.lnk) support and code comments
1.3 - Add XP12 support. Sort Default below Custom Airports.
1.3.1 - Fix Scenery Packs getting jumbled
1.3.2 - Fix syntax error (I have no clue how this crept in)
1.4b1 - Attempt to locate XP installs (only available for direct downloads)
(skipped 1.4 release - I went overboard with the changes :D - ended up rewriting practically the whole thing to support planned features)
2.0b1 - Parse apt.dat to verify if a pack is an airport. Sort Default below Custom Overlays. Now deal with all permutations of capitalised letters. Alphabetically sort each layer.


### KNOWN ISSUES:
- Automatic location of X-Plane installs (as far as I know) doesn't work for Steam users.
- Meshes such as AlpilotX's HD/UHD Mesh get treated as overlays. This is because on the surface, they look identical. Only by parsing the DSF is it possible to discern the two - some code for this has been written but it is far from complete. If you have experience in this matter, please please please get in touch.​
