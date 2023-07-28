import glob
import locale
import os
import struct
import sys
import time

# State version
print("Scenery Pack Organiser version 2.0b1")


# DEF: Expand shell paths to absolute paths
def expand_path(path):
    if sys.platform == "win32":
        return os.path.expandvars(path)
    elif sys.platform in ["darwin","linux"]:
        return os.path.expanduser(path)


# Attempt to programmatically locate X-Plane installs and offer to use those
# TODO: Locate steam installs too
search_path = None
install_locations = {}
if sys.platform == "win32":
    search_path = "%USERPROFILE%/AppData/Local"
elif sys.platform == "darwin":
    search_path = "~/Library/Preferences"
elif sys.platform == "linux":
    search_path = "~/.x-plane"
else:
    print(f"Unsupported OS '{sys.platform}' detected. Please leave a comment if you believe this an error. Please also share a screenshot of this window. ")
if search_path:
    i = 0
    for version in ["", "_10", "_11", "_12"]:
        try:
            txtpath = expand_path(os.path.join(search_path, f"x-plane_install{version}.txt"))
            txtfile = open(txtpath,"r")
            for install_location in txtfile.readlines():
                install_locations[i] = [f"X-Plane {version.strip('_') if version else '9 or earlier'}", install_location.strip("\n")]
                i+=1
            txtfile.close()
        except FileNotFoundError:
            pass
if install_locations:
    print("Found the following X-Plane installs:")
    for i in range(len(install_locations)):
        print(f"{i}: {install_locations[i][0]} at '{install_locations[i][1]}'")
    print("If you would like to use one of these paths, enter its serial number as displayed in the above list. ")
    print("Otherwise, paste the filepath in as normal. ")
    choice = input("Enter your selection here: ")
    try:
        xplane_path = install_locations[int(choice)][1]
    except ValueError:
        xplane_path = choice
else:
    print("Could not find any X-Plane installs. You will need to enter a filepath manually. ")
    xplane_path = input("Enter the path to the X-Plane folder: ")


# Constant and variable declarations
SCENERY_PATH = os.path.join(xplane_path, "Custom Scenery")
XP11_GLOBAL_AIRPORTS = "SCENERY_PACK Custom Scenery/Global Airports/\n"
XP12_GLOBAL_AIRPORTS = "SCENERY_PACK *GLOBAL_AIRPORTS*\n"
FILE_LINE_REL = "SCENERY_PACK Custom Scenery/"
FILE_LINE_ABS = "SCENERY_PACK "
FILE_DISAB_LINE_REL = "SCENERY_PACK_DISABLED Custom Scenery/"
FILE_DISAB_LINE_ABS = "SCENERY_PACK_DISABLED "
FILE_BEGIN = "I\n1000 Version\nSCENERY\n\n"
START_TIME = time.time()

airport_registry = []
defaultairports = []
customairports = []
defaultoverlays = []
customoverlays = []
orthos = []
meshes = []
libraries = []
plugins = []


# Check if the path is broken
if not os.path.exists(SCENERY_PATH):
    print("Could not find a Custom Scenery directory here. Perhaps a broken or deleted install? ")
    input("Press enter to close")
    exit()


# DEF: Read Windows shorcuts
# This code was taken from https://gist.github.com/Winand/997ed38269e899eb561991a0c663fa49
def read_shortcut_target(path):
    with open(path, 'rb') as stream:
        content = stream.read()
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
        last_pos = position
        position += 0x04
        length = struct.unpack('I', content[last_pos:position])[0]
        position += 0x0C
        lbpos = struct.unpack('I', content[position:position + 0x04])[0]
        position = last_pos + lbpos
        size = (length + last_pos) - position - 0x02
        content = content[position:position + size].split(b'\x00', 1)
        return content[-1].decode('utf-16' if len(content) > 1
                                  else locale.getdefaultlocale()[1])


# DEF: Check if a directory contains a folder or file (case insensitive)
# Ignore items list and return case-sensitive path for apt.dat calls if it exists
def dir_contains(directory:str, items:list, type:str = None):
    walk = tuple(os.walk(directory))
    if type == "apt.dat":
        for folder in walk[0][1]:
            if folder.lower() == "earth nav data":
                for path, folders, files in walk:
                    if path == os.path.join(directory, folder):
                        for file in files:
                            if file.lower() == "apt.dat":
                                return os.path.join(directory, folder, file)
        return None
    elif type in [None, "generic"]:
        item_present = {}
        for item in items:
            item_present[item] = False
            for obj in walk[0][2 if type == "generic" else 1]:
                if obj.lower() == item.lower():
                    item_present[item] = True
                    break
        for present in item_present.values():
            if not present:
                return False
        return True


# DEF: Check if any of the items in a list are present in a given string
# Used for checking if a scenery package is default
def str_contains(searchstr:str, itemslist: list):
    for item in itemslist:
        if item in searchstr:
            return True
    return False


# DEF: Classify as Ortho, Mesh, or Overlay after reading DSF and scanning folders
# TODO: Open some DSF, if sim/overlay is 1, the pack is an overlay. Check if default by X-Plane Landmarks in name
# If folder contains textures and terrain folder, the pack is an ortho mesh
# If folder only has Earth nav data, the pack is a mesh
def isOrthoMeshOverlay(dirpath, dirname):
    if not dir_contains(dirpath, ["Earth nav data"]):
        return None
    if dir_contains(dirpath, ["Earth nav data"]) and False:
        return "Mesh"
    if dir_contains(dirpath, ["Earth nav data", "textures", "terrain"]) and True:
        return "Ortho"
    if dir_contains(dirpath, ["Earth nav data"]) and True and str_contains(dirname, ["X-Plane Landmarks"]):
        return "Default Overlay"
    if dir_contains(dirpath, ["Earth nav data"]) and True:
        return "Custom Overlay"


# DEF: Check if the pack is an airport. If it has an apt.dat file, read and verify. Also check if default
def isAirport(dirpath, dirname):
    apt_type = None
    apt_path = dir_contains(dirpath, None, "apt.dat")
    if apt_path:
        apt_file = open(apt_path, "r")
        for line in apt_file.readlines():
            if line.startswith("1 ") or line.startswith("16 ") or line.startswith("17 "):
                if str_contains(dirname, ["Global Airports", "Demo Area", "X-Plane Airports", "X-Plane Landmarks", "Aerosoft"]):
                    apt_type = "Default Airport"
                else:
                    apt_type = "Custom Airport"
                    splitline = line.split(maxsplit=5)
                    airport_registry.append([splitline[4], splitline[5].strip("\n"), dirname])
        apt_file.close()
    return apt_type


# DEF: Check if the pack is a library. If it contains a library.txt file, is a library
def isLibrary(dirpath):
    return dir_contains(dirpath, ["library.txt"], "generic")


# DEF: Check if the pack is a scenery plugin. If it contains a plugins folder, it is a scenery plugin
def isPlugin(dirpath):
    return dir_contains(dirpath, ["plugins"])


# DEF: Format the line according to the required format for scenery_packs.ini
def formatLine(ini_path, shortcut):
    if shortcut:
        return f"{FILE_LINE_ABS}{ini_path}/\n"
    else:
        return f"{FILE_LINE_REL}{ini_path}/\n"


# DEF: Classify the pack
def processType(path, shortcut = False):
    abs_path = os.path.join(SCENERY_PATH, path)
    if shortcut:
        ini_path = abs_path
    else:
        ini_path = path        
    sorted = False
    if not sorted:
        type = isAirport(abs_path, path)
        if type == "Default Airport":
            defaultairports.append(formatLine(ini_path, shortcut))
            sorted = True
        elif type == "Custom Airport":
            customairports.append(formatLine(ini_path, shortcut))
            sorted = True
    if not sorted:
        type = isOrthoMeshOverlay(abs_path, path)
        if type == "Default Overlay":
            defaultoverlays.append(formatLine(ini_path, shortcut))
            sorted = True
        elif type == "Custom Overlay":
            customoverlays.append(formatLine(ini_path, shortcut))
            sorted = True
        elif type == "Ortho":
            orthos.append(formatLine(ini_path, shortcut))
            sorted = True
        elif type == "Mesh":
            meshes.append(formatLine(ini_path, shortcut))
            sorted = True
    if not sorted:
        if isLibrary(abs_path):
            libraries.append(formatLine(ini_path, shortcut))
            sorted = True
        elif isPlugin(abs_path):
            plugins.append(formatLine(ini_path, shortcut))
            sorted = True
    if not sorted:
        print("Unable to classify", path)
        print("Perhaps a folder-in-folder? If this a valid pack, paste the following line into the file")
        print(formatLine(ini_path, shortcut))
     

print("Reading directory")

# Process each directory in the Custom Scenery folder
for directory in list(os.walk(SCENERY_PATH))[0][1]:
    processType(directory)

# Process each shortcut in the Custom Scenery folder
for shortcut in glob.glob(SCENERY_PATH + "\\*.lnk"):
    processType(read_shortcut_target(shortcut), shortcut=True)


# Sort tiers alphabetically
defaultairports.sort()
customairports.sort()
defaultoverlays.sort()
customoverlays.sort()
orthos.sort()
meshes.sort()
libraries.sort()
plugins.sort()


# Move XP11 Global Airports to the end, or inject XP12 Global Airports
try:
    del defaultairports[defaultairports.index(XP11_GLOBAL_AIRPORTS)]
    defaultairports.append(XP11_GLOBAL_AIRPORTS)
except ValueError:
    defaultairports.append(XP12_GLOBAL_AIRPORTS)

print("All packs classified, except those specified otherwise")


# TODO: Check custom airport clashes using airport_registry


scenery_ini_path_dep = os.path.join(SCENERY_PATH, "scenery_packs.ini")
scenery_ini_path_bak = f"{scenery_ini_path_dep}.bak"

# Remove the old backup file, if present
if os.path.exists(scenery_ini_path_bak):
    print("Removing old backup file")
    os.remove(scenery_ini_path_bak)

# Back up the current scenery_packs.ini file
if os.path.exists(scenery_ini_path_dep):
    print("Backing up scenery_packs.ini file")
    os.rename(scenery_ini_path_dep, scenery_ini_path_bak)

# Write out the new scenery_packs.ini file
print("Writing new scenery_packs.ini file")

f = open(scenery_ini_path_dep, "w+")
f.write(FILE_BEGIN)
f.writelines(customairports)
f.writelines(defaultairports)
f.writelines(plugins)
f.writelines(libraries)
f.writelines(customoverlays)
f.writelines(defaultoverlays)
f.writelines(orthos)
f.writelines(meshes)

f.flush()
f.close()
print("Done!")
print(f"Took {time.time() - START_TIME} seconds")
input("Press enter to close")
