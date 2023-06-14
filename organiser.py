import struct
from os import walk, rename, remove
from os.path import join, isfile, exists
import time
from glob import glob
import locale

# Get the X-Plane folder, and define constants
xplane_path = input('Enter the path to the X-Plane folder: ')
scenery_path = join(xplane_path, 'Custom Scenery')
SCENERY_PACK_CONST = 'SCENERY_PACK '
CUSTOM_SCENERY_CONST = 'SCENERY_PACK Custom Scenery/'
FILE_BEGIN_CONST = 'I\n1000 Version\nSCENERY\n\n'

now = time.time()


# I did not write the code to read the shortcut target
# The code can be found over here: https://gist.github.com/Winand/997ed38269e899eb561991a0c663fa49
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


# Get the list of all directories inside a parent directory
def list_directory_dirs(directory):
    dirlist = []
    for (dirpath, dirnames, filenames) in walk(directory):
        dirlist.extend(dirnames)
        break
    return dirlist


# Check if a list contains a value
# I know it's a simple thing to have this in the code, but this looks cleaner
def list_contains(searchlist, item):
    return item in searchlist


# Check if a tile is an ortho tile. All Ortho4XP sceneries have an Earth nav data, textures and terrain folder
# I used the presence of these folders to determine whether or not a scenery is an ortho tile
# This also works with the US Orthophotos project
def isOrthoTile(directory):
    dirlist = list_directory_dirs(directory)
    return (list_contains(dirlist, 'Earth nav data') and list_contains(dirlist, 'textures') and
            list_contains(dirlist, 'terrain'))


# Check if a scenery pack is a library. If it contains a library.txt file or OpenSceneryX is in the directory, then
# it is considered a scenery library
def isLibrary(directory):
    return isfile(join(directory, 'library.txt')) or 'OpenSceneryX' in directory


# Check if a scenery pack is an overlay. If it has a navdata folder and does not have an apt.dat file, or it contains
# X-Plane Landmarks, then it is considered an overlay scenery
def isOverlay(directory):
    navdata_folder = join(directory, 'Earth nav data')
    return exists(navdata_folder) and not isfile(join(navdata_folder, 'apt.dat')) or 'X-Plane Landmarks' in directory


# Check if something is a default airport. If the directory is named Global Airports or contains Aerosoft, then it is
# considered a default airport
def isDefaultAirport(directory):
    for i in ['Global Airports','Aerosoft','Demo Area','X-Plane Airports']:
        if i in directory:
            return True


# Check if something is a custom airport. If it has a navdata folder and an apt.dat file, then it is considered an
# airport
def isAirport(directory):
    navdata_folder = join(directory, 'Earth nav data')
    return exists(navdata_folder) and isfile(join(navdata_folder, 'apt.dat'))


# Check if something is a scenery plugin. If it contains a plugins folder, then it is considered a scenery plugin
def isSceneryPlugin(directory):
    return exists(join(directory, 'plugins'))


# Format the directory according to the required format in the scenery_packs.ini file
def dirformat(directory, inMainFolder):
    if inMainFolder:
        return CUSTOM_SCENERY_CONST + directory + '/\n'
    else:
        return SCENERY_PACK_CONST + directory + '/\n'


# Classify the scenery pack. Pretty simple to understand
def processDir(directory, inMainFolder=True):
    if inMainFolder:
        s_directory = join(scenery_path, directory)
    else:
        s_directory = directory

    if isOrthoTile(s_directory):
        orthotiles.append(dirformat(directory, inMainFolder))
    elif isOverlay(s_directory):
        overlays.append(dirformat(directory, inMainFolder))
    elif isDefaultAirport(s_directory):
        defaultairports.append(dirformat(directory, inMainFolder))
    elif isAirport(s_directory):
        airports.append(dirformat(directory, inMainFolder))
    elif isLibrary(s_directory):
        libraries.append(dirformat(directory, inMainFolder))
    elif isSceneryPlugin(s_directory):
        plugins.append(dirformat(directory, inMainFolder))
    else:
        print('Unable to classify', directory)
        print('If this is a valid scenery pack, paste this line into the file')
        print(dirformat(directory, inMainFolder))


# List all directories in the Custom Scenery folder
custom_scenery_dir = list_directory_dirs(scenery_path)

# Move Global Airports to the end so as to not override demo areas, also check to inject *GLOBAL_AIRPORTS* for XP12
try:
    gl_apt = custom_scenery_dir.pop(custom_scenery_dir.index('Global Airports'))
    custom_scenery_dir.append(gl_apt)
    xp12 = False
except ValueError:
    xp12 = True

orthotiles = []
libraries = []
overlays = []
defaultairports = []
airports = []
plugins = []

print('Reading directory')

# Process each directory in the Custom Scenery folder
for obj in custom_scenery_dir:
    processDir(obj)

# Process each shortcut in the Custom Scenery folder
custom_scenery_dir = glob(scenery_path + "\\*.lnk")
for shortcut in custom_scenery_dir:
    scenery_pack_dir = read_shortcut_target(shortcut)
    processDir(scenery_pack_dir, inMainFolder=False)

print('All packs classified, except those specified otherwise')

# Inject Global Airports for XP12 if needed
if xp12:
    defaultairports.append(f"{SCENERY_PACK_CONST}*GLOBAL_AIRPORTS*\n")

print('All packs classified, except those specified otherwise')

scenery_packs_file_path = join(scenery_path, 'scenery_packs.ini')
scenery_packs_bkp_file_path = scenery_packs_file_path + '.bak'

# Remove the old backup file, if present
if exists(scenery_packs_bkp_file_path):
    print('Removing old backup file')
    remove(scenery_packs_bkp_file_path)

# Back up the current scenery_packs.ini file
if exists(scenery_packs_file_path):
    print('Backing up scenery_packs.ini file')
    rename(scenery_packs_file_path, scenery_packs_bkp_file_path)

# Write out the new scenery_packs.ini file
print('Writing new scenery_packs.ini file'

f = open(scenery_packs_file_path, 'w+')
f.write(FILE_BEGIN_CONST)
f.writelines(airports)
f.writelines(defaultairports)
f.writelines(plugins)
f.writelines(libraries)
f.writelines(overlays)
f.writelines(orthotiles)

f.flush()
f.close()
print('Done!')
print("Took", time.time() - now, 'seconds')
input('Press enter to close')
