import os
import logging
import re
import sys
from shutil import copyfile

logger = logging.getLogger('i2nsrec_count_error_check')
hdlr = logging.FileHandler('i2nsrec_count_error_check.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

if len(sys.argv) < 2:
	print("Please provide Dropbox directory")
	exit(-1)
dirb = sys.argv[1] #"/mnt/d/Dropbox/Music/General Collection"

dbhash = {}

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

def error_check_dir(dirName, parentDir):
	if dirName == "mp3":
		return
	path = os.path.join(parentDir, dirName)
	logger.info("Error checking '" + path + "'")
	if not hasSubDirNamed(path, "mp3"):
		logger.info(path + " does not have an MP3 directory.  Skipping.")
	else:
		logger.info(path + " has an MP3 directory. Checking...")
		aacCount=0
		mp3Count = 0
	
		for file in os.listdir(path):
			if file.endswith(".mp3") or file.endswith(".m4a"):
				aacCount+=1
		for file in os.listdir(os.path.join(path, "mp3")):
			if file.endswith(".mp3"):
				mp3Count+=1
		#if file count does not match, log error
		if aacCount != mp3Count:
			print(path)
			logger.error("There are " +str(mp3Count) + " mp3s in '" + os.path.join(path, "mp3") + "', but only " + str(aacCount) + " AAC/MP3 files in '" + path + "'" )
		#else, log info
		else:
			logger.info("MP3 count matches for '" + os.path.join(path, "mp3") + "' and '" + path + "'" )
	for dir in get_immediate_subdirectories(path):
		error_check_dir(dir, path)  
for dir in get_immediate_subdirectories(dirb): 	
	error_check_dir(dir, dirb)  

 


 


	