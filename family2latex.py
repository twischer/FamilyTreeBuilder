#! /usr/bin/python3
# Exectly one child of a root child need a spouse tag 
# regardless (außer) the first root child tree of the xml file.
# This child descripes how the other childs will connected to the first root child tree.
# Be carful, the xml structure must contain only one spouse tag 
# for all childs of the same root child
import xml.etree.ElementTree as ET


def printChildTopDown(id,  text,  parentId='',  childCount=0,  childNr=0):
	# child 1 of 1
	leftOffset = 0.0
	rightOffset = 0.0
	
	if childCount == 2:
		if childNr == 1:
			leftOffset = -1.5
		elif childNr == 2:
			rightOffset = -1.5
		else:
			raise Exception('ChildNr > ChildCount')
	elif childCount == 3:
		if childNr == 1:
			leftOffset = 0.2
		elif childNr == 2:
			# same as child 1 of 1
			leftOffset = 0.0
			rightOffset = 0.0
		elif childNr == 3:
			rightOffset = 0.2
		else:
			raise Exception('ChildNr > ChildCount')
			
	printNode(id,  text,  parentId,  None,  0.5,  leftOffset,  rightOffset)


def  printNode(id,  text,  parentId='',  aboveOffset=None,  belowOffset=None,  leftOffset=None,  rightOffset=None):
	# print tkiz node similar to
	# \node[below left=0.5 and 0.2 of mother1] (child1) {Kind 1};
	print('\t\\node',  end="") 
	
	# only use relative postioning,
	# if a mother exists
	if parentId != '':
		print('[',  end="")
		# define which directions the rel pos should have
		relPosOffsets = []
		if aboveOffset:
			print('above',  end="")
			relPosOffsets.append( str(aboveOffset) )
		if belowOffset:
			print(' below',  end="")
			relPosOffsets.append( str(belowOffset) )
		if leftOffset:
			print(' left',  end="")
			relPosOffsets.append( str(leftOffset) )
		if rightOffset:
			print(' right',  end="")
			relPosOffsets.append( str(rightOffset) )
		
		relPosOffString = ' and '.join(relPosOffsets)
		print('=' + relPosOffString + ' of ' + parentId + '] ',  end="")
		
	print('(' + id + ') {' + text + '};')
		
	# only print connection line,
	# if a mother exists
	if parentId != '':
		if aboveOffset:
			# print tikiz line for connecting child with parent
			# \draw[thick] (mother1) |- ($ (child1.south) + (0,0.25) $) -- (child1);
			print('\t\\draw[thick] (' + id + ') |- ($ (',  end="")
			print(parentId + '.north) + (0,0.25) $) -- (' + parentId + ');')
		if belowOffset:
			# print tikiz line for connecting mother with the child
			# \draw[thick] (mother1) |- ($ (child1.north) + (0,0.25) $) -- (child1);
			print('\t\\draw[thick] (' + parentId + ') |- ($ (',  end="")
			print(id + '.north) + (0,0.25) $) -- (' + id + ');')
		else:
			# print tikiz line for connecting married persons
			# \draw[thick] (mother1) -- (father1);
			print('\t\\draw[thick] (' + parentId + ') -- (' + id + ');')



def getChildDescription(xmlNode):
	text = xmlNode.get('name')
	text += xmlNode.get('birth',  'UNKOWN')
	return text


def getUniqId(xmlNode):
	# create id if no id could be found in xml structure
	id = xmlNode.get('id')
	if not id:
		text = getChildDescription(xmlNode)
		id = text.replace(" ",  "")
		id = id.replace(".",  "")
		# TODO replace ä ü ö
	return id


def printXmlNode(xmlNode,  parentId='',  aboveOffset=None,  belowOffset=None,  leftOffset=None,  rightOffset=None):
	text = getChildDescription(xmlNode)
	id = getUniqId(xmlNode)
	printNode(id,  text,  parentId,  aboveOffset,  belowOffset,  leftOffset,  rightOffset)
	
	return id


def processChildren(root,  motherId):
	children = root.findall('child')
	childCount = len(children)
	childNr = 1
	for child in children:
		text = getChildDescription(child)
		id = getUniqId(child)
		printChildTopDown(id, text,  motherId,  childCount,  childNr)
		processChildren(child,  id)
		childNr += 1


def findRootPath(parent):
	if parent.find('spouse') is not None:
		subRootChildrenList = []
		subRootChildrenList.append(parent)
		return subRootChildrenList
	else:
		children = parent.findall('child')
		for child in children:
			# check childs of this child for spouse tag
			subRootChildrenList = findRootPath(child)
			if subRootChildrenList:
				subRootChildrenList.append(parent)
				return subRootChildrenList
		return None


print('\\begin{tikzpicture}[node distance=0.2,auto,nodes={inner sep=0.3em, minimum height=3em, rectangle,draw=black, text centered,text width=3cm}]')

tree = ET.parse('family.xml')
root = tree.getroot()
children = root.findall('child')
doButtomUp = False
for child in children:
	text = getChildDescription(child)
	id = getUniqId(child)
	
	if doButtomUp:
		rootChildrenList = findRootPath(child)
		if not rootChildrenList:
			print("ERR: No spouse tag found in root child! "
				"Do not know how to connect other root child trees with first root child tree.")
			exit(-1)
		
#		# For debugging
#		for rootChild in rootChildrenList:
#			childText = getChildDescription(rootChild)
#			print("Spouse " + childText)
		
		# TODO print connection line, too
		# if there are more than one spouse tag
		# but do not use relative offset and try to use absolut positions
		
		
		# TODO use find instead
		#spouseTag = rootChildrenList[0].find('spouse')
		#if spouseTag:
		marriedChild = rootChildrenList.pop(0)
		spouseTag = marriedChild.findall('spouse')
		parentId = None
		if len(spouseTag) >= 1:
			parentId = spouseTag[0].get('id',  None)
		
		if not parentId:
			print("ERR: Spouse tag does not contain an id attribute!")
			exit(-1)
		
		# print and conect all children of rootChildrenList
		parentId = printXmlNode(marriedChild,  parentId,  None,  None,  None,  0.2)
		for rootChild in rootChildrenList:
			parentId = printXmlNode(rootChild,  parentId,  0.5)
		
		# TODO if it is married conect to given id
		# buttonUp geht nicht, da ein Mann mehrmals heiraten kann
		# und damit sich mit mehreren Frauen verbinden müsste
		#printChildTopDown(id, text,  parentId,  1,  1)
	else:
		printNode(id,  text)
		processChildren(child,  id)
	
	# apend all other root children expecting the first one with a
	# buttom up connection in the root tree
	doButtomUp = True

print('\\end{tikzpicture}')
