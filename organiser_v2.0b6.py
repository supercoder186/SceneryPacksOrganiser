import glob
import locale
import os
import pathlib
import pkg_resources
import struct
import sys
import time

# If on Windows, import pywin32 (to read Windows shortcuts)
if sys.platform == "win32":
    try: 
        pkg_resources.require("pywin32")
    except:
        print("I could not locate the pywin32 package. I am thus installing it for you.")
        print("If you see an error after this or if the window abruptly closes, please restart the script.\n")
        os.system("pip install pywin32")
        print("\n")
    import win32com.client


# State version
print("Scenery Pack Organiser version 2.0b6\n")


# DEF: Expand shell paths to absolute paths
def expand_path(shell_path:str):
    absol_path = None
    if sys.platform == "win32":
        absol_path = os.path.expandvars(shell_path)
    elif sys.platform in ["darwin","linux"]:
        absol_path = os.path.expanduser(shell_path)
    return pathlib.Path(absol_path)


# Attempt to programmatically locate X-Plane installs and offer to use those, otherwise take user input
# Some remnants of code to support X-Plane 9 and earlier remain here. It's easy to see what needs to be removed
# However, it's worth neither the time nor the effort, and should rather be kept for possible future use cases
# TODO: Locate steam installs too
search_path = ""
install_locations = {}
if sys.platform == "win32":
    search_path = "%USERPROFILE%/AppData/Local"
elif sys.platform == "darwin":
    search_path = "~/Library/Preferences"
elif sys.platform == "linux":
    search_path = "~/.x-plane"
else:
    print(f"Unsupported OS '{sys.platform}' detected. Please report if you believe this an error.")
    print("Please also share a screenshot of this window.")
if search_path:
    i = 0
    for version in ["_10", "_11", "_12"]:
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
    print("I found the following X-Plane installs:")
    for i in range(len(install_locations)):
        print(f"    {i}: {install_locations[i][0]} at '{install_locations[i][1]}'")
    print("If you would like to use one of these paths, enter its serial number as displayed in the above list.")
    print("Otherwise, paste the filepath in as normal.")
    choice = input("Enter your selection here: ")
    try:
        xplane_path = install_locations[int(choice)][1]
    except ValueError:
        xplane_path = choice
else:
    print("I could not find any X-Plane installs. You will need to enter a filepath manually.")
    xplane_path = input("Enter the path to the X-Plane folder: ")

# Convert xplane_path to Path object
xplane_path = pathlib.Path(xplane_path)

# Constant and variable declarations
SCENERY_PATH = xplane_path / "Custom Scenery"
XP10_GLOBAL_AIRPORTS = "SCENERY_PACK Custom Scenery/Global Airports/\n"
XP12_GLOBAL_AIRPORTS = "SCENERY_PACK *GLOBAL_AIRPORTS*\n"
FILE_LINE_REL = "SCENERY_PACK Custom Scenery/"
FILE_LINE_ABS = "SCENERY_PACK "
FILE_DISAB_LINE_REL = "SCENERY_PACK_DISABLED Custom Scenery/"
FILE_DISAB_LINE_ABS = "SCENERY_PACK_DISABLED "
FILE_BEGIN = "I\n1000 Version\nSCENERY\n\n"

airport_registry = {}
disable_registry = {}
disable_choice = None
measure_time = []
unsorted_registry = []
unparsed_registry = []
customairports = []
defaultairports = []
prefabairports = []
globalairports = []
plugins = []
libraries = []
customoverlays = []
defaultoverlays = []
orthos = []
meshes = []


# Validate given path
if not SCENERY_PATH.is_dir():
    print(f"\nI could not find a Custom Scenery directory at {str(xplane_path)}. Perhaps a broken or deleted install?")
    input("No changes have been made to your files. Press enter to close")
    exit()

# Read old ini and store disabled packs. Ask user if they want to carry them forward
ini_path = SCENERY_PATH / "scenery_packs.ini"
if ini_path.is_file():
    ini_file = open(ini_path, "r", encoding = "utf-8")
    for line in ini_file.readlines():
        for disabled in [FILE_DISAB_LINE_REL, FILE_DISAB_LINE_ABS]:
            if line.startswith(disabled):
                disable_registry[line.split(disabled, maxsplit=1)[1].strip("\n")[:-1]] = disabled
                break
    ini_file.close()
    if disable_registry:
        print("\nI see you've disabled some packs in the current scenery_packs.ini")
        disable_choice = input("Would you like to carry over the DISABLED tags to the new ini? (yes/no or y/n): ").lower()
        if disable_choice in ["y","yes"]:
            print("Ok, I will carry over whatever is possible to the new ini.")
            disable_choice = True
        elif disable_choice in ["n","no"]:
            print("Ok, I will not carry over any of the old DISABLED tags.")
            disable_registry = {}
            disable_choice = False
        else:
            print(f"Sorry, I didn't understand. I'm assuming you meant no. I will therefore not carry over any of the old DISABLED tags.")
            disable_registry = {}
            disable_choice = False


# Initial time record
measure_time.append(time.time())

# Store the results of os.walk() from the Custom Scenery directory so we don't make a bunch of unnecessary calls
print("\nI will now scan the Custom Scenery folder...")
measure_time.append(time.time())
WALK = tuple(os.walk(SCENERY_PATH))
print(f"Took me {time.time() - measure_time.pop()} seconds to scan.")


# DEF: Read Windows shorcuts
# The non-Windows code was taken from https://gist.github.com/Winand/997ed38269e899eb561991a0c663fa49
def read_shortcut_target(sht_path:str):
    tgt_path = None
    if sys.platform == "win32":
        shell = win32com.client.Dispatch("WScript.Shell")
        tgt_path = shell.CreateShortCut(sht_path).Targetpath
    else:
        with open(sht_path, 'rb') as stream:
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
            tgt_path = content[-1].decode('utf-16' if len(content) > 1 else locale.getdefaultlocale()[1])
    return pathlib.Path(tgt_path)


# DEF: Check if a directory contains a folder or file (case insensitive)
# Ignore items list and return case-sensitive path for apt.dat or Earth nav data calls
def dir_contains(directory:pathlib.Path, items:list, type:str = None):
    dir_walk = None
    fld_walk = None
    for obj in WALK:
        if obj[0] == str(directory):
            dir_walk = tuple(WALK)
            fld_walk = obj
            break
    else:
        dir_walk = tuple(os.walk(directory))
        fld_walk = dir_walk[0]
    if type == "apt.dat":
        for folder in fld_walk[1]:
            if folder.lower() == "earth nav data":
                end_folder = directory / folder
                for path, folders, files in dir_walk:
                    if path == str(end_folder):
                        for file in files:
                            if file.lower() == "apt.dat":
                                return directory / folder / file
        return None
    elif type == "Earth nav data":
        for folder in fld_walk[1]:
            if folder.lower() == "earth nav data":
                return directory / folder
    elif type in [None, "generic"]:
        item_present = {}
        for item in items:
            item_present[item] = False
            for obj in fld_walk[2 if type == "generic" else 1]:
                if obj.lower() == item.lower():
                    item_present[item] = True
                    break
        for present in item_present.values():
            if not present:
                return False
        return True


# DEF: Check if any of the items in a list are present in a given string
# Used for checking if a scenery package is default
def str_contains(searchstr:str, itemslist:list, casesensitive:bool = True):
    for item in itemslist:
        if casesensitive and item in searchstr:
            return True
        elif not casesensitive and item.lower() in searchstr.lower():
            return True
    return False


# DEF: Check if the pack is an airport. If it has an apt.dat file, read and verify. Also check if default or prefab
def isAirport(dirpath:pathlib.Path, dirname:str, file_line:str):
    apt_path = dir_contains(dirpath, None, "apt.dat")
    if not apt_path: 
        return None
    if apt_path and dirname == "Global Airports": 
        return "Global"
    apt_lins = None
    for codec in ('utf-8', 'charmap', 'cp1252', 'cp850'):
        try:
            apt_file = open(apt_path, "r", encoding = codec)
            apt_lins = apt_file.readlines()
            break
        except:
            pass
    apt_type = None
    for line in apt_lins:
        if line.startswith("1 ") or line.startswith("16 ") or line.startswith("17 "):
            if str_contains(dirname, ["prefab"], casesensitive = False):
                apt_type = "Prefab"
                break
            elif str_contains(dirname, ["Demo Area", "X-Plane Airports", "X-Plane Landmarks", "Aerosoft"]):
                apt_type = "Default"
                break
            else:
                apt_type = "Custom"
                splitline = line.split(maxsplit=5)
                airport_entry = (splitline[5].strip("\n"), dirname, file_line)
                try:
                    airport_registry[splitline[4]].append(airport_entry)
                except KeyError:
                    airport_registry[splitline[4]] = [airport_entry]
    apt_file.close()
    return apt_type


# DEF: Classify as Ortho, Mesh, or Overlay after reading DSF and scanning folders
# Open some DSF, if sim/overlay is 1, the pack is an overlay. Also check if default
# If folder contains textures and terrain folder, the pack is an ortho mesh
# If folder only has Earth nav data, the pack is a mesh
def isOrthoMeshOverlay(dirpath:pathlib.Path, dirname:str):
    end_path = dir_contains(dirpath, None, "Earth nav data")
    overlay = True
    if not end_path:
        return None
    #TODO: remove below condition when dsf parsing is complete
    if dir_contains(dirpath, ["textures", "terrain"]):
            return "Ortho"
    if overlay:
        if str_contains(dirname, ["X-Plane Landmarks"]):
            return "Default Overlay"
        else:
            return "Custom Overlay"
    else:
        if dir_contains(dirpath, ["textures", "terrain"]):
            return "Ortho"
        else:
            return "Mesh"


# DEF: Check if the pack is a library. If it contains a library.txt file, is a library
def isLibrary(dirpath:pathlib.Path):
    return dir_contains(dirpath, ["library.txt"], "generic")


# DEF: Check if the pack is a scenery plugin. If it contains a plugins folder, it is a scenery plugin
def isPlugin(dirpath:pathlib.Path):
    return dir_contains(dirpath, ["plugins"])


# DEF: Format the line according to the required format for scenery_packs.ini
# Also check if this pack was previously disabled
def formatLine(ini_path:str, shortcut:bool):
    if ini_path in disable_registry:
        return_line = f"{disable_registry[ini_path]}{ini_path}/\n"
        del disable_registry[ini_path]
        return return_line
    if shortcut:
        return f"{FILE_LINE_ABS}{ini_path}/\n"
    else:
        return f"{FILE_LINE_REL}{ini_path}/\n"


# DEF: Classify the pack
def processType(path, shortcut = False):
    abs_path = SCENERY_PATH / path
    name = str(path)
    if shortcut:
        ini_path = str(abs_path)
    else:
        ini_path = str(path)
    sorted = False
    line = formatLine(ini_path, shortcut)
    if not sorted:
        type = isAirport(abs_path, name, line)
        if type == "Global":
            globalairports.append(line)
            sorted = True
        elif type == "Prefab":
            prefabairports.append(line)
            sorted = True
        elif type == "Default":
            defaultairports.append(line)
            sorted = True
        elif type == "Custom":
            customairports.append(line)
            sorted = True
    if not sorted:
        type = isOrthoMeshOverlay(abs_path, name)
        if type == "Default Overlay":
            defaultoverlays.append(line)
            sorted = True
        elif type == "Custom Overlay":
            customoverlays.append(line)
            sorted = True
        elif type == "Ortho":
            orthos.append(line)
            sorted = True
        elif type == "Mesh":
            meshes.append(line)
            sorted = True
    if not sorted:
        if isLibrary(abs_path):
            libraries.append(line)
            sorted = True
        elif isPlugin(abs_path):
            plugins.append(line)
            sorted = True
    if not sorted:
        unsorted_registry.append(line)
     

print("\nI will now classify each scenery pack...")
measure_time.append(time.time())


# Process each directory in the Custom Scenery folder
maxlength = 0
for directory in WALK[0][1]:
    progress_str = f"Processing: {directory}"
    if len(progress_str) <= maxlength:
        progress_str = f"{progress_str}{' ' * (maxlength - len(progress_str))}"
    else:
        maxlength = len(progress_str)
    print(f"\r{progress_str}", end = "\r")
    processType(directory)
sys.stdout.write("\033[K")

# Process each Windows shortcut in the Custom Scenery folder
shtcut_list = glob.glob(str(SCENERY_PATH / "*.lnk"))
if shtcut_list and sys.platform != "win32":
    print(f"\nI found Windows .LNK shortcuts, but I'm not on Windows! Detected platform: {sys.platform}")
    print("I will still attempt to read them, but I cannot guarantee anything. I would suggest you use symlinks instead.")
elif shtcut_list and sys.platform == "win32":
    print("\nReading .LNK shortcuts...")
maxlength = 0
printed = False
for shtcut_path in shtcut_list:
    try:
        folder_path = read_shortcut_target(shtcut_path)
        if folder_path.exists():
            progress_str = f"Processing: {str(folder_path)}"
            if len(progress_str) <= maxlength:
                progress_str = f"{progress_str}{' ' * (maxlength - len(progress_str))}"
            else:
                maxlength = len(progress_str)
            print(f"\r{progress_str}", end = "\r")
            processType(folder_path, shortcut = True)
            continue
        else: 
            pass
    except:
        pass
    unparsed_registry.append(shtcut_path)
if printed:
    sys.stdout.write("\033[K")


# Sort tiers alphabetically
unsorted_registry.sort()
customairports.sort()
defaultairports.sort()
prefabairports.sort()
globalairports.sort()
plugins.sort()
libraries.sort()
customoverlays.sort()
defaultoverlays.sort()
orthos.sort()
meshes.sort()

# Check to inject XP12 Global Airports
if not globalairports:
    globalairports.append(XP12_GLOBAL_AIRPORTS)


# Display all packs that couldn't be sorted and offer to write them at the top of the file
if unsorted_registry:
    measure_time.append(time.time())
    print("\nI was unable to classify some packs. I will show them formatted as per the ini:")
    for pack in unsorted_registry:
        pack_stripped = pack.strip('\n')
        print(f"    {pack_stripped}")
    unsorted_choice = input("Should I still write them into the ini? (yes/no or y/n): ").lower()
    if unsorted_choice in ["y","yes"]:
        print("Ok, I will write them at the top of the ini.")
    elif unsorted_choice in ["n","no"]:
        print("Ok, I will not write them in the ini.")
        unsorted_registry = None
    else:
        print(f"Sorry, I didn't understand. I'm assuming you meant no. I will therefore not write them in the ini.")
        unsorted_registry = None
    unsorted_wait = time.time() - measure_time.pop()
    print(f"Waited {unsorted_wait} seconds for your input")
else:
    unsorted_wait = 0


# Display all disabled packs that couldn't be found
if disable_registry:
    print("\nSome packs were tagged DISABLED in the old scenery_packs.ini, but could not be found.")
    print("They have probably been deleted or renamed. I will list them out now:")
    for pack in disable_registry:
        print(f"    {pack}")


# Display all shortcuts that couldn't be read
if unparsed_registry:
    print("\nI was unable to parse these shortcuts:")
    for shortcut in unparsed_registry:
        print(f"    {shortcut}")
    print("You will need to manually paste the target location paths into the file in this format:")
    print(f"{FILE_LINE_ABS}<path-to-target-location>/")


# Display time taken in this operation
print(f"\nI've classified all packs other than the specified ones. ")
print(f"Took me {time.time() - measure_time.pop() - unsorted_wait} seconds to classify.")


# Check custom airport clashes using airport_registry and ask the user if they want to resolve
print("\nI will now check for Custom Airport conflicts...")
measure_time.append(time.time())
measure_time.append(time.time())
conflicts = 0
for icao in airport_registry:
    if len(airport_registry[icao]) > 1: 
        conflicts+=1
if conflicts:
    resolve_conflicts = input(f"Found {conflicts} Custom Airport conflicts. Would you like to resolve them now? (yes/no or y/n): ")
    if resolve_conflicts in ["y","yes"]:
        print("Ok, I will display them and resolve with your input.")
        resolve_conflicts = True
    elif resolve_conflicts in ["n","no"]:
        print("Ok, I will only display them.")
        resolve_conflicts = False
    else:
        print(f"Sorry, I didn't understand. I'm assuming you meant no. I will therefore only display them.")
        resolve_conflicts = False
    conflict_wait = time.time() - measure_time.pop()
    print(f"Waited {conflict_wait} seconds for your input")
else:
    measure_time.pop()
    resolve_conflicts = None


# Display (and if opted for, resolve) all custom airport clashes
for icao in airport_registry:
    if len(airport_registry[icao]) == 1: 
        continue
    print(f"\nI found {len(airport_registry[icao])} airports for {icao}.")
    print("I'll list them out with a number, the airport name as per the pack, and the pack's folder's name.")
    airport_multiple = {}
    i = 0
    for airport in airport_registry[icao]:
        airport_multiple [i] = airport[2]
        print(f"    {i}: '{airport[0]}' in '{airport[1]}'")
        i+=1
    if not resolve_conflicts:
        continue
    order = input("Enter the serial numbers as per the list separated by commas. I will write them in that order: ").strip(" ").split(",")
    for sl in order:
        try:
            customairports.append(customairports.pop(customairports.index(airport_multiple[int(sl)])))
        except:
            print("That didn't work. Do read the instructions if you're unsure about how to input your preferences.")
            input("No changes have been made to your files. Press enter to close")
            exit()
if resolve_conflicts:
    print(f"Took me {time.time() - measure_time.pop() - conflict_wait} seconds to resolve conflicts with your help.\n")
elif conflicts:
    measure_time.pop()
    print("You may wish to manually go through the ini file for corrections.\n")
else:
    measure_time.pop()
    print("I didn't detect any conflicts.\n")


scenery_ini_path_dep = pathlib.Path(SCENERY_PATH / "scenery_packs.ini")
scenery_ini_path_bak = pathlib.Path(f"{scenery_ini_path_dep}.bak")


# Remove the old backup file, if present
if scenery_ini_path_bak.exists():
    print("I will now delete the old scenery_packs.ini.bak")
    scenery_ini_path_bak.unlink()

# Back up the current scenery_packs.ini file
if scenery_ini_path_dep.exists():
    print("I will now back up the current scenery_packs.ini")
    scenery_ini_path_dep.rename(scenery_ini_path_bak)

# Write out the new scenery_packs.ini file
print("I will now write the new scenery_packs.ini")


# Print packs as sorted (ONLY FOR DEVELOPMENT OR DEBUGGING USE)
if False:
    debug = {"unsorted":unsorted_registry, "customairports":customairports, "defaultairports":defaultairports, "prefabairports":prefabairports, "globalairports":globalairports, 
         "plugins":plugins, "libraries":libraries, "customoverlays":customoverlays, "defaultoverlays":defaultoverlays, "orthos":orthos, "meshes":meshes}
    for i in debug:
        lst = debug[i]
        print(i)
        for j in lst:
            print(f"    {j.strip()}")


f = open(scenery_ini_path_dep, "w+", encoding = "utf-8")
f.write(FILE_BEGIN)
if unsorted_registry:
    f.writelines(unsorted_registry)
f.writelines(customairports)
f.writelines(defaultairports)
f.writelines(prefabairports)
f.writelines(globalairports)
f.writelines(plugins)
f.writelines(libraries)
f.writelines(customoverlays)
f.writelines(defaultoverlays)
f.writelines(orthos)
f.writelines(meshes)

f.flush()
f.close()
print("\nDone!")
print(f"Took me {time.time() - measure_time.pop()} seconds in total.")
input("Press enter to close")
