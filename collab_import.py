####################################################################
# Module      : collab_import.py
# Author      : Klazen108 (twitch.tv/klazen108)
# Date        : 2015-09-11
# Description : Imports collab resources into main project
####################################################################
#print(ET.tostring(root, 'utf-8'))

#<assets>
#  <sounds name="sound"> example of resource type - name attribute is folder name, tag name is group name
#    <sounds name="music"> example of group, name matches parent group name
#      <sound>sound\bgm_Tutorial</sound> example of entry, text is file path

import os
import sys
import traceback
import ntpath
from os.path import join as pjoin
import re
import codecs
import shutil
import xml.etree.ElementTree as ET
import copy

def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

#function child_with_name
##Finds an XML node under 'parent' with a name attribute matching 'name'
#param parent: the parent XML node whose children we want to scan
#param name: the value of the name attribute we want to match
def child_with_name(parent,name):
	return parent.find("*[@name='"+name+"']")

#function child_dirs
##Returns all child directories in the parent directory
#param parent_path: the directory to scan
def child_dirs(parent_path):
	return [d for d in os.listdir(parent_path) if os.path.isdir(pjoin(parent_path,d))]

#function child_files
##Returns all child filenames in the parent directory
#param parent_path: the directory to scan
def child_files(parent_path):
	return [f for f in os.listdir(parent_path) if os.path.isfile(pjoin(parent_path,f))]

#function recursive_copy
##copies all new XML resource definitions from the source project to the target project
##Skips existing elements, and performs a recursive traversal of the XML tree
#param group_name: the name of the XML element in this structure that comprises a "group" (for example, sprites for sprite groups)
#param source_node: the current source XML element we're working from
#param target_node: the corresponding target element to check for the resource
#param target_copy_to_node: the target XML element to copy the resource reference to
def recursive_copy(group_name,source_node,target_node,target_copy_to_node):
	#get all the nodes representing groups
	source_groups = [e for e in source_node if e.tag==group_name]
	
	target_entry_names = [g.text for g in target_node if not g.tag==group_name]
	
	#all nodes that aren't groups must be entries, copy those that don't already exist
	for entry in [e for e in source_node if e not in source_groups and e.text not in target_entry_names]:
		target_copy_to_node.append(copy.deepcopy(entry))
		print("\tNew entry: " +entry.text)
	
	#for all nodes that are groups, traverse them
	for cur_group in source_groups:
		folder_name = cur_group.get("name")
		target_group = child_with_name(target_node,folder_name)
		#use an empty list if there's no corresponding target node, since we'll need to copy all files anyway
		if (target_group is None): 
			target_group = []
		
		recursive_copy(group_name,cur_group,target_group,target_copy_to_node)

#function recursive_file_copy
##copies a source directory structure to a target directory structure, for all elements that don't already exist
#param source_path: the source path to copy from
#param target_path: the target path to copy to
#param skip_files: if true, skips the files in this source directory, and just goes straight to the child directories
def recursive_file_copy(source_path,target_path,skip_files):
	#make a group if it doesn't exist
	if not os.path.exists(target_path):
		print("mkdir: "+target_path)
		os.mkdirs(target_path)
	
	#copy the files unless we're skipping here
	if not skip_files:
		files = child_files(source_path)
		for file in files:
			if not os.path.exists(pjoin(target_path,file)):
				print("\t"+file)
				shutil.copyfile(pjoin(source_path,file),pjoin(target_path,file))
	
	#recurse into the directories
	dirs = child_dirs(source_path)
	for dir in dirs:
		recursive_file_copy(pjoin(source_path,dir),pjoin(target_path,dir),False)

#function main
##Copies all new resources from a GMStudio project into another
#param target_path: the path of the target project to copy to (the folder the .project.gmx is contained in)
#param source_path: the path of the source project to copy from (the folder the .project.gmx is contained in)
#param folder_name: a string to name the folder in which the new resources are copied in GMStudio
def main(target_path,source_path,folder_name):
	if not os.path.exists(source_path):
		print("Source path '"+source_path+"' doesn't exist! Please check and try again.")
		sys.exit(-1)
	if not os.path.exists(target_path):
		print("Target path '"+target_path+"' doesn't exist! Please check and try again.")
		sys.exit(-2)
	
	print("Target project: "+target_path)
	print("Source project: "+source_path)
	print("\n")
	
	print("Copying resource definitions in project file...")
	#open the target project XML
	t_gmx = next((os.path.join(target_path,f) for f in os.listdir(target_path) if f.endswith(".gmx")), None)
	if t_gmx is None:
		print("No .project.gmx file found in target directory '"+target_path+"'! Please check and try again.")
		sys.exit(-3)
	target_tree = ET.parse(t_gmx)
	target_root = target_tree.getroot()
	
	#backup target project file
	print("backing up target project")
	if (os.path.exists(t_gmx+".bkup")):
		os.remove(t_gmx+".bkup")
	shutil.copyfile(t_gmx,t_gmx+".bkup")
	
	#open the source project XML
	s_gmx = next((os.path.join(source_path,f) for f in os.listdir(source_path) if f.endswith(".gmx")), None)
	if s_gmx is None:
		print("No .project.gmx file found in source directory '"+source_path+"'! Please check and try again.")
		sys.exit(-4)
	source_tree = ET.parse(s_gmx)
	source_root = source_tree.getroot()
	
	#analyze each source type (sprite, background, etc)
	for source_node in source_root:
		cur_type = source_node.tag
		if (source_node.get("name") is None): #skip groups without names, we're not interested in those
			continue
		print("Analyzing: "+cur_type)
		
		#find the corresponding target node
		target_node = target_root.find(source_node.tag)
		
		#make sure there's a group to import into
		target_group = child_with_name(target_node,folder_name)
		if (target_group is None):
			target_group = ET.Element(cur_type,name=folder_name)
			target_node.append(target_group)
		
		#copy the source structure to the target structure
		print(ET.tostring(target_group, 'utf-8'))
		recursive_copy(cur_type,source_node,target_node,target_group)
	
	#save the project
	print("Writing project file to disk...")
	target_tree.write(t_gmx)
	print("Project file written!\n")
	
	print("Copying resource files from source to target...")
	recursive_file_copy(source_path,target_path,True)
	print("Resources copied!")
	
	print("\nComplete!")

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])