import struct
from os import walk, rename, remove
from os.path import join, isfile, exists
import time
from glob import glob

xplane_path = input('Enter the path to the X-Plane folder: ')
scenery_path = join(xplane_path, 'Custom Scenery')
SCENERY_PACK_CONST = 'SCENERY_PACK '
CUSTOM_SCENERY_CONST = 'SCENERY_PACK Custom Scenery/'
FILE_BEGIN_CONST = 'I\n1000 Version\nSCENERY\n\n'

now = time.time()


def read_shortcut_target(file):
    with open(file, 'rb') as stream:
        content = stream.read()
        # skip first 20 bytes (HeaderSize and LinkCLSID)
        # read the LinkFlags structure (4 bytes)
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18
        # if the HasLinkTargetIDList bit is set then skip the stored IDList
        # structure and header
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
        last_pos = position
        position += 0x04
        # get how long the file information is (LinkInfoSize)
        length = struct.unpack('I', content[last_pos:position])[0]
        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags, and VolumeIDOffset)
        position += 0x0C
        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position + 0x04])[0]
        position = last_pos + lbpos
        # read the string at the given position of the determined length
        size = (length + last_pos) - position - 0x02
        temp = struct.unpack('c' * size, content[position:position + size])
        return ''.join([chr(ord(a)) for a in temp])


def list_directory_dirs(directory):
    dirlist = []
    for (dirpath, dirnames, filenames) in walk(directory):
        dirlist.extend(dirnames)
        break
    return dirlist


def list_contains(searchlist, item):
    return any(x == item for x in searchlist)


def isOrthoTile(directory):
    dirlist = list_directory_dirs(directory)
    return (list_contains(dirlist, 'Earth nav data') and list_contains(dirlist, 'textures') and
            list_contains(dirlist, 'terrain'))


def isLibrary(directory):
    return isfile(join(directory, 'library.txt')) or 'OpenSceneryX' in directory


def isOverlay(directory):
    navdata_folder = join(directory, 'Earth nav data')
    return exists(navdata_folder) and not isfile(join(navdata_folder, 'apt.dat')) or 'X-Plane Landmarks' in directory


def isDefaultAirport(directory):
    return directory == 'Global Airports' or 'Aerosoft' in directory


def isAirport(directory):
    navdata_folder = join(directory, 'Earth nav data')
    return exists(navdata_folder) and isfile(join(navdata_folder, 'apt.dat'))


def isSceneryPlugin(directory):
    return exists(join(directory, 'plugins'))


def dirformat(directory, inMainFolder):
    if inMainFolder:
        return CUSTOM_SCENERY_CONST + directory + '/\n'
    else:
        return SCENERY_PACK_CONST + directory + '/\n'


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


custom_scenery_dir = list_directory_dirs(scenery_path)
orthotiles = []
libraries = []
overlays = []
defaultairports = []
airports = []
plugins = []

print('Reading directory...')

for obj in custom_scenery_dir:
    processDir(obj)

custom_scenery_dir = glob(scenery_path + "\\*.lnk")
for shortcut in custom_scenery_dir:
    scenery_pack_dir = read_shortcut_target(shortcut)
    processDir(scenery_pack_dir, inMainFolder=False)

print('All packs classified, except those specified otherwise')

scenery_packs_file_path = join(scenery_path, 'scenery_packs.ini')
scenery_packs_bkp_file_path = scenery_packs_file_path + '.bkp'

if exists(scenery_packs_bkp_file_path):
    print('Removing old backup file...')
    remove(scenery_packs_bkp_file_path)

if exists(scenery_packs_file_path):
    print('Backing up scenery_packs.ini file')
    rename(scenery_packs_file_path, scenery_packs_bkp_file_path)

print('Writing new scenery_packs.ini file')
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
