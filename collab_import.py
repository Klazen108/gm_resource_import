####################################################################
# Module      : collab_import.py
# Author      : Klazen108 (twitch.tv/klazen108)
# Date        : 2015-09-11
# Description : Imports collab resources into main project
####################################################################

#<assets>
#  <sounds name="sound"> example of resource type - name attribute is folder name, tag name is group name
#    <sounds name="music"> example of group, name matches parent group name
#      <sound>sound\bgm_Tutorial</sound> example of entry, text is file path

import os
import sys
import traceback
import ntpath
from os.path import join
import re
import codecs
import shutil
import xml.etree.ElementTree as ET
import copy

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def child_with_name(parent,name):
	return parent.find("*[@name='"+name+"']")

def pjoin(a,b):
	return os.path.join(a,b)
	
def child_dirs(parent_path):
	return [d for d in os.listdir(parent_path) if os.path.isdir(pjoin(parent_path,d))]
	
def child_files(parent_path):
	return [f for f in os.listdir(parent_path) if os.path.isfile(pjoin(parent_path,f))]

def recursive_copy(target_path,source_path,group_name,source_node,target_node):
	#get all the nodes representing groups
	source_groups = [e for e in source_node if e.tag==group_name]
	
	target_group_names = [g.get("name") for g in target_node if g.tag==group_name]
	target_entry_names = [g.text for g in target_node if not g.tag==group_name]
	
	#all nodes that aren't groups must be entries, copy those that don't already exist
	for entry in [e for e in source_node if e not in source_groups and e.text not in target_entry_names]:
		target_node.append(copy.deepcopy(entry))
		print("\tNew entry: " +entry.text)
		#copy the entry
	
	#for all nodes that are groups, traverse them
	for cur_group in source_groups:
		folder_name = cur_group.get("name")
		target_group = child_with_name(target_node,folder_name)
		if (target_group is None):
			target_group = ET.Element(cur_group.tag,name=cur_group.get("name"))
			target_node.append(target_group)
		
		recursive_copy(pjoin(target_path,folder_name),pjoin(source_path,folder_name),group_name,cur_group,target_group)

def recursive_file_copy(source_path,target_path):
	
	#make a group if it doesn't exist
	if not os.path.exists(target_path):
		print("mkdir: "+target_path)
		os.mkdirs(target_path)
	
	dirs = child_dirs(source_path)
	files = child_files(source_path)
	for file in files:
		if not os.path.exists(pjoin(target_path,file)):
			print("copy:"+file)
			shutil.copyfile(pjoin(source_path,file),pjoin(target_path,file))
	for dir in dirs:
		recursive_file_copy(pjoin(source_path,dir),pjoin(target_path,dir))
	
def main(target_path,source_path,collab_id):
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
	#files = [os.path.join(target_path,f) for f in os.listdir(target_path) if f.endswith(".gmx")]
	#t_gmx = files[0] #todo - make sure it exists
	target_tree = ET.parse(t_gmx)
	target_root = target_tree.getroot()
	
	#open the source project XML
	s_gmx = next((os.path.join(source_path,f) for f in os.listdir(source_path) if f.endswith(".gmx")), None)
	if s_gmx is None:
		print("No .project.gmx file found in source directory '"+source_path+"'! Please check and try again.")
	#files = [os.path.join(source_path,f) for f in os.listdir(source_path) if f.endswith(".gmx")]
	#s_gmx = files[0] #todo - make sure it exists
	source_tree = ET.parse(s_gmx)
	source_root = source_tree.getroot()
	
	#go over each source type
	for source_node in source_root:
		cur_type = source_node.tag
		folder_name = source_node.get("name")
		if (folder_name is None): #skip groups without names, we're not interested in those
			continue
		print("Analyzing: "+cur_type)
		
		#find the corresponding target node
		target_node = target_root.find(source_node.tag)
		if target_node is None: #if it's not there, make a new one
			target_node = ET.Element(source_node.tag, name=folder_name)
			target_root.append(target_node)
		
		#copy the source structure to the target structure
		recursive_copy(pjoin(target_path,folder_name),pjoin(source_path,folder_name),cur_type,source_node,target_node)
	#print(ET.tostring(root, 'utf-8'))
	print("Writing project file to disk...")
	source_tree.write(t_gmx+".new")
	
	print("Copying resource files from source to target...")
	recursive_file_copy(source_path,target_path)
	print("Complete!")

if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])