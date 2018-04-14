import os
import logging
import re
from shutil import copyfile, move
import sys


logger = logging.getLogger('replace_aac_with_mp3')
hdlr = logging.FileHandler('replace_aac_with_mp3.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
dropBoxDir = None
iTunesDir = None
#topDir = dropBoxDir
#iTunesDir = "/mnt/d/iTunes/iTunes Media/Music"

i2hash = {}

always_replace = False


def addtohash(name, parentDir):
    path = os.path.join(parentDir, name)
    i2hash[name.lower()] = path
    for n in get_immediate_subdirectories(path):
        addtohash(n, path)


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def hasSubDirNamed(dir, name):
    for n in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, n)):
            # we found a directory
            if n.lower() == name.lower():
                return True
    return False


def getEquivItunesDir(path):
        # remove dropBoxDir from path to make your new path
        # /mnt/d/Dropbox/Music/General Collection/
    ldropBoxDir = len(dropBoxDir)
    dir = path[ldropBoxDir+1:]
    if dir.lower() in i2hash:
        dir = i2hash[dir.lower()]
    iTunesPath = os.path.join(iTunesDir, dir)
    logger.info("itunes equiv path: " + iTunesPath)
    return iTunesPath


def fileCount(path, ext):
    count = 0
    for file in os.listdir(path):
        if file.endswith(ext):
            count += 1
    return count


def evalDiff(path):
    mp3Dir = os.path.join(path, "mp3")
    replace = False  # init
    if not os.path.exists(mp3Dir):
        logger.warning("no equivalent mp3 dir exists for " + path)
        return
    if always_replace:
        replace = True
    else:
        # if there is an equivalent itunes directory and that directory has more m4as than this directory has mp3s, replace mp3 directory
        eid = getEquivItunesDir(path)
        if not os.path.exists(eid):
            logger.warning("no equivalent itunes dir exists for " + path)
            return
        if eid and ((fileCount(eid, ".m4a") + fileCount(eid, ".mp3")) > fileCount(mp3Dir, ".mp3")) or ((fileCount(eid, ".m4a") + fileCount(eid, ".mp3")) > (fileCount(path, ".mp3")+fileCount(path, ".m4a"))):
            logger.warning(eid + " has more itunes files as there are files in " +
                           path + ". Moving Mp3s back to allow for re-do")
            replace = True
    if replace:
        for file in os.listdir(path):
            if file.endswith(".m4a"):
                os.remove(os.path.join(path, file))

        for file in os.listdir(mp3Dir):
            os.rename(os.path.join(mp3Dir, file),  os.path.join(path, file))
        os.rmdir(mp3Dir)
    else:
        logger.info("No change")


def replace_aac_top(path):
    logger.info("Processing " + path)
    if not hasSubDirNamed(path, "mp3"):
        logger.info(path + " does not have an MP3 directory.  Skipping.")
    else:
        logger.info(path + " has an MP3 directory")
        evalDiff(path)
    for dir in get_immediate_subdirectories(path):
        replace_aac(dir, path)


def replace_aac(dirName, parentDir):
    if dirName == "mp3":
        return
    logger.info("Processing " + dirName)
    path = os.path.join(parentDir, dirName)
    if not hasSubDirNamed(path, "mp3"):
        logger.info(path + " does not have an MP3 directory.  Skipping.")
    else:
        logger.info(path + " has an MP3 directory")
    evalDiff(path)
    for dir in get_immediate_subdirectories(path):
        replace_aac(dir, path)


if len(sys.argv) > 2:
    always_replace = False
    iTunesDir = sys.argv[1]
    dropBoxDir = sys.argv[2]
    for dir in get_immediate_subdirectories(iTunesDir):
        addtohash(dir, iTunesDir)

elif len(sys.argv) > 1:
    always_replace = True
    iTunesDir = None
    dropBoxDir = sys.argv[1]
else:
    print("Check args")
# if len(sys.argv) < 2:
# 	print("Please provide an iTunes Directory and a Dropbox directory")
# 	exit(-1)
# if len(sys.argv) < 3:
# 	print("Please provide a Dropbox directory")
# 	exit(-1)

# for dir in get_immediate_subdirectories(dirb):
replace_aac_top(dropBoxDir)
