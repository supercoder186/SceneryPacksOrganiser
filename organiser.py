from os import walk, rename, remove
from os.path import join, isfile, exists

xplane_path = input('Enter the path to the X-Plane folder: ')
scenery_path = join(xplane_path, 'Custom Scenery')
SCENERY_PACK_CONST = 'SCENERY_PACK Custom Scenery/'
FILE_BEGIN_CONST = 'I\n1000 Version\nSCENERY\n\n'


def list_directory_dirs(directory):
    dirlist = []
    for (dirpath, dirnames, filenames) in walk(directory):
        dirlist.extend(dirnames)
        break
    return dirlist


def list_contains(searchlist, item):
    return any(x == item for x in searchlist)


def isOrthoTile(directory):
    dirlist = list_directory_dirs(join(scenery_path, directory))
    return (list_contains(dirlist, 'Earth nav data') and list_contains(dirlist, 'textures') and
            list_contains(dirlist, 'terrain'))


def isLibrary(directory):
    return isfile(join(scenery_path, directory, 'library.txt')) or directory == 'OpenSceneryX'


def isOverlay(directory):
    navdata_folder = join(scenery_path, directory, 'Earth nav data')
    return exists(navdata_folder) and not isfile(join(navdata_folder, 'apt.dat')) or 'X-Plane Landmarks' in directory


def isDefaultAirport(directory):
    return directory == 'Global Airports' or 'Aerosoft' in directory


def isAirport(directory):
    navdata_folder = join(scenery_path, directory, 'Earth nav data')
    return exists(navdata_folder) and isfile(join(navdata_folder, 'apt.dat'))


def isSceneryPlugin(directory):
    return exists(join(scenery_path, directory, 'plugins'))


def dirformat(directory):
    return SCENERY_PACK_CONST + directory + '/\n'


def processDir(directory):
    if isOrthoTile(directory):
        orthotiles.append(dirformat(directory))
    elif isOverlay(directory):
        overlays.append(dirformat(directory))
    elif isDefaultAirport(directory):
        defaultairports.append(dirformat(directory))
    elif isAirport(directory):
        airports.append(dirformat(directory))
    elif isLibrary(directory):
        libraries.append(dirformat(directory))
    elif isSceneryPlugin(directory):
        plugins.append(dirformat(directory))
    else:
        print('Unable to classify', directory)
        print('If this is a valid scenery pack, paste this line into the file')
        print(dirformat(directory))


def check_SAM():
    SAM_path = join(xplane_path, 'Resources', 'plugins', 'SAM', 'lib', 'SAM_Library')
    if exists(SAM_path):
        libraries.append("SCENERY_PACK " + SAM_path + '/\n')


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

check_SAM()

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

input('Press enter to close')
