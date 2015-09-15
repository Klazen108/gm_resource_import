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

def recursive_copy(target_path,source_path,group_name,source_node,target_node):
	#make a group if it doesn't exist
	#if not os.path.exists(target_path):
	#	os.mkdirs(target_path)
	
	#get all the nodes representing groups
	source_groups = [e for e in source_node if e.tag==group_name]
	
	target_group_names = [g.get("name") for g in target_node if g.tag==group_name]
	target_entry_names = [g.text for g in target_node if not g.tag==group_name]
	
	#all nodes that aren't groups must be entries, copy those that don't already exist
	for entry in [e for e in source_node if e not in source_groups and e.text not in target_entry_names]:
		target_node.append(copy.deepcopy(entry))
		print("New entry: " +entry.text)
	
	#for all nodes that are groups, traverse them
	for cur_group in source_groups:
		folder_name = cur_group.get("name")
		target_group = child_with_name(target_node,folder_name)
		if (target_group is None):
			target_group = ET.Element(cur_group.tag,name=cur_group.get("name"))
			target_node.append(target_group)
		
		recursive_copy(pjoin(target_path,folder_name),pjoin(source_path,folder_name),group_name,cur_group,target_group)

def main(target_path,source_path,collab_id):
	print("Target project: "+target_path)
	print("Source project: "+source_path)
	print("\n")
	
	#open the target project XML
	files = [os.path.join(target_path,f) for f in os.listdir(target_path) if f.endswith(".gmx")]
	target_tree = ET.parse(files[0])
	target_root = target_tree.getroot()
	
	#open the source project XML
	files = [os.path.join(source_path,f) for f in os.listdir(source_path) if f.endswith(".gmx")]
	source_tree = ET.parse(files[0])
	source_root = source_tree.getroot()
	
	#go over each source type
	for source_node in source_root:
		cur_type = source_node.tag
		folder_name = source_node.get("name")
		if (folder_name is None):
			continue
		print(cur_type)
		
		#find the corresponding target node
		target_search_nodes = [n for n in target_root if n.tag == source_node.tag]
		target_node = target_root.find(source_node.tag)
		if target_node is None: #if it's not there, make a new one
			target_node = ET.Element(source_node.tag, name=folder_name)
			target_root.append(target_node)
		
		#copy the source structure to the target structure
		recursive_copy(pjoin(target_path,folder_name),pjoin(source_path,folder_name),cur_type,source_node,target_node)
	#print(ET.tostring(root, 'utf-8'))
	sys.exit(0)


if __name__ == "__main__":
	main(sys.argv[1],sys.argv[2],sys.argv[3])