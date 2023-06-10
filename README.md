# SceneryPacksOrganiser
Are you tired of having to manually sift through all the packs in the Custom Scenery folder and having to reorder them manually?

Do you hate having to start X-Plane and quit just to add new scenery packs to the file so you can reorganise it?

This simple script is for you!

It automatically detects all the folders in the Custom Scenery folder (and the SAM Scenery Library in the plugins folder), sorts them and then writes a scenery_packs.ini file!

It is organised in this fashion

1. Airports
2. Default Airports
3. Scenery Plugins (I'm not sure how it works, but MisterX KSFO has something like this)
4. Libraries
5. Overlays, VFR Sceneries, etc.
6. Ortho tiles
 

The script is very fast, and I can guarantee that you have an atrociously high amount of scenery (I tested it with about 155 scenery packages), it will complete in under 5 seconds

(My system took under 1 second)

There is no real installation process. Simply download and unzip the file, then double click to run. On some Linux distributions, you may need to use the command line to run, like so: `python organiser.py`

Requirements:

Python 3
