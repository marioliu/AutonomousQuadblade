"""
Adapted from https://github.com/IntelligentQuadruped, with permission
Description: Manages file directories.
"""

import os, shutil, json
from time import time

def ensureDir(file_path):
	'''
	Creates folder for images if necessary. 

	Args:
		file_path: 	Intended destination of images 

	Output:
	Directory path
	'''
	if not os.path.exists(file_path):
		os.makedirs(file_path)
	print('Created path: {}'.format(file_path))
	return file_path

def getRelativePath(src_path,dst_path):
	'''
	Returns the relative path between from two absolute paths.

	Args:
		src_path:	Starting directory for relative path
		dst_path:	Destination directory for relative path

	Output:
		The relative path between the specified directories.
	'''
	return os.path.relpath(src_path,dst_path)

def moveFile(src_path, dst_path,file_name):
	'''
	MOVE images into the corresponding folders

	Args:
	    src_path: 	Directory of file origin
	 	dst_path: 	Directory of file destination
	 	file_name: 	Name of the file that is being moved

	Output:
	 	None
	'''
	src = str(os.path.join(src_path,file_name))
	dst = str(os.path.join(dst_path,file_name))
	shutil.move(src,dst)
	pass

def copyFile(src_path, dst_path,file_name):
	'''
	COPY images into the corresponding folders

	Args:
	 	src_path: 	Directory of file origin
	 	dst_path: 	Directory of file destination
	 	file_name: 	Name of the file that is being moved

	Output:
	 	None
	'''
	src = str(os.path.join(src_path,file_name))
	dst = str(os.path.join(dst_path,file_name))
	shutil.copyfile(src,dst)
	pass

def remove(path):
    '''
	Removes folder, or file at the specified path. 

	Args:
		path: Directory of the folder or file that will be deleted
	'''

    if os.path.isfile(path):
        os.remove(path)

    elif os.path.isdir(path):
        shutil.rmtree(path)

    else:
        raise ValueError("File {} is not a file or dir.".format(path))

    pass

def saveToJson(obj, name = 'output', file_path = './'):
	'''
	Saves input object to .json in the output folder.

	Args:
		obj:	Python object to be save to .json. 
		name:	Name of saved .json-file.
		file_path: directory in which .json file will be saved.
	'''
	if name == 'output':
		name = name + '_' + str(int(time()))
	if not name.endswith('.json'):
		name = name + '.json'
	with open(name,'w') as file:
		json.dump(obj,file, indent=4)
	pass
