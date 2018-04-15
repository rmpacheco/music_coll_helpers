import os
import logging
import re
import sys
from shutil import copyfile

logger = logging.getLogger('i2nsrec')
hdlr = logging.FileHandler('i2nsrec.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

if len(sys.argv) < 2:
    print("Please provide an iTunes Directory and a Dropbox directory")
    exit(-1)
if len(sys.argv) < 3:
    print("Please provide a Dropbox directory")
    exit(-1)

dira = sys.argv[1]  
dirb = sys.argv[2]

# [os.path.join(dirb, o) for o in os.listdir(dirb) if os.path.isdir(os.path.join(dirb, o))]
dbhash = {}


def addtodropboxhash(name, parentDir):
    # logger.info(name)
    # logger.info(parentDir)
    path = os.path.join(parentDir, name)
    dbhash[name.lower()] = path
    for n in get_immediate_subdirectories(path):
        addtodropboxhash(n, path)


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def get_immediate_files(a_dir):
    # logger.info("Dir: " + a_dir)
    return [name for name in os.listdir(a_dir)
            if os.path.isfile(os.path.join(a_dir, name))]


def getDropboxEquivPath(dir):
    if dir.lower() in dbhash:
        return dbhash[dir.lower()]


def hasSubDirNamed(dir, name):
    for n in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, n)):
            # we found a directory
            if n.lower() == name.lower():
                return True
    return False


def getFirstFileWithSongNameContaining(dir, songName, extension):
    logger.info("looking for " + extension + " file for song '" +
                songName + "' in '" + dir + "'")

    for file in os.listdir(dir):
        if file.endswith("." + extension):
            # we found a file
            sn = getSongNameFromFile(file)
            if not sn:
                sn = file
            if songName.lower().strip() == sn.lower().strip():
                return file

def getSongNameFromFile(file):
    m = re.search('^[0-9][0-9-]* (.+)\.[0-9a-zA-Z]{2,4}$', file)
    if m:
        name = m.group(1).replace("_", " ").replace("-", " ")
        logger.info("getSongNameFromFile('" + file + "') found '" + name + "'")
        return name


def getFileSize(path):
    statinfo = os.stat(path)
    return statinfo.st_size


def move_mp3s(path):
    mp3Dir = os.path.join(path, "mp3")
    if not os.path.exists(mp3Dir):
        os.makedirs(mp3Dir)

    for file in os.listdir(path):
        if file.endswith(".mp3"):
            os.rename(os.path.join(path, file), os.path.join(mp3Dir, file))

    if not os.listdir(mp3Dir):
        os.rmdir(mp3Dir)


def fileCount(path, ext):
    count = 0
    for file in os.listdir(path):
        if file.endswith(ext):
            count += 1
    return count


def processitunesdir(dirName, parentDir):
    path = os.path.join(parentDir, dirName)
    logger.info("path is " + path)
    pathaacfc = fileCount(path, ".m4a")
    pathmp3fc = fileCount(path, ".mp3")
    pathfc = pathaacfc+pathmp3fc
    
    if pathfc  ==0:
        logger.info("No itunes files to move in " + path)
    else: 
    
        dbPath = getDropboxEquivPath(dirName)

        if not dbPath:
            # remove /mnt/d/iTunes/iTunes Media/Music from itunes path to make your new path
            ldira = len(dira)
            dbPath = os.path.join(dirb, path[ldira:].strip("/"))
            logger.info("new dropbox path: " + dbPath)
            logger.warning("no dropbox dir found for " + path +
                           ".  Creating new directory at " + dbPath)
            os.makedirs(dbPath)

        logger.info("dropbox path is " + dbPath)
        mp3Dir = os.path.join(dbPath, "mp3")
        if hasSubDirNamed(dbPath, "mp3"):
            if not os.listdir(mp3Dir):
                logger.warning("found empty mp3 dir in " +
                               dbPath + "...deleting it")
                os.rmdir(mp3Dir)
            else:
                logger.warning(
                    dbPath + " has a non-empty mp3 directory, so it appears to have already been processed.  Skipping.")
        else:
            if hasSubDirNamed(dbPath, "aac"):
                logger.warning(
                    dbPath + " has an aac directory, so it appears to have already been processed.  Skipping.")
            else:
                # if # of aac files from itunes is > # of aac files already in dropbox
                dbaacfc = fileCount(dbPath, ".m4a")
                dbmp3fc = fileCount(dbPath, ".mp3")
                dbfc = dbaacfc+dbmp3fc
                if pathfc == dbfc and (pathaacfc != dbaacfc or pathmp3fc != dbmp3fc):
                    # move all mp3 files out
                    logger.info(dbPath + ": moving existing files")
                    move_mp3s(dbPath)
                    # replace with aac files
                    logger.info(dbPath + ": replacing with itunes files")
                    for f in get_immediate_files(path):
                        fPath = os.path.join(path, f)
                        copyfile(fPath, os.path.join(dbPath, f))
                elif dbfc == 0:     
                    logger.info(dbPath + ": new directory, moving itunes music over")
                    for f in get_immediate_files(path):
                        fPath = os.path.join(path, f)
                        copyfile(fPath, os.path.join(dbPath, f))
                else:
                    logger.warning("file count mismatch in '" + dbPath + "'.  Skipping")

        
    for dir in get_immediate_subdirectories(path):
        processitunesdir(dir, path)


for dir in get_immediate_subdirectories(dirb):
    addtodropboxhash(dir, dirb)

for dir in get_immediate_subdirectories(dira):
    processitunesdir(dir, dira)
