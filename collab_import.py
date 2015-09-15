####################################################################
# Module      : collab_import.py
# Author      : Klazen108 (twitch.tv/klazen108)
# Date        : 2015-09-11
# Description : Imports collab resources into main project
####################################################################

import os
import sys
import traceback
import ntpath
from os.path import join, getsize
import re
import codecs
import shutil
import xml.etree.ElementTree as ET

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def traverse(path,target_path):
	fgroup = []
	#if not os.file.exists(target_path):
		#os.makedirs(target_path)
	
	files = [f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.endswith(".gmx"))]
	fgroup.extend(files)
	
	files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
	#for f in files:
		#shutil.copyfile(os.path.join(path,f),os.path.join(target_path,f))
	dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
	for d in dirs:
		fgroup.append(traverse(os.path.join(path,d),os.path.join(target_path,d)))
	
	return fgroup

# project_path - the root path of the project where the resources are located (the split output for gm8)
def main(target_path,source_path,collab_id):
	print("Target project: "+target_path)
	print("Source project: "+source_path)
	print("\n")
	files = [os.path.join(target_path,f) for f in os.listdir(target_path) if f.endswith(".gmx")]
	tree = ET.parse(files[0])
	root = tree.getroot()
	new_resources = [ ["sounds",[]], ["sprites",[]], ["backgrounds",[]], ["paths",[]], ["scripts",[]], ["fonts",[]], ["objects",[]], ["rooms",[]]]
	for child in root:
		print(child.tag)
		for res in child:
			print("\t"+res.tag)
	#print(ET.tostring(root, 'utf-8'))
	sys.exit(0)


if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])