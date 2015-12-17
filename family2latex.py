#! /usr/bin/python3
# Exectly one child of a root child need a spouse tag 
# regardless (außer) the first root child tree of the xml file.
# This child descripes how the other childs will connected to the first root child tree.
# Be carful, the xml structure must contain only one spouse tag 
# for all childs of the same root child
import xml.etree.ElementTree as ET


def printChild(xmlNode,  parentId=None,  childCount=0,  childNr=0, topDown=True, onlyConnect=False):
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
			
	aboveOffset = None;
	belowOffset = None;
	if topDown:
		belowOffset = 0.5
	else:
		aboveOffset = 0.5
	
	return printNode(xmlNode,  parentId,  aboveOffset,  belowOffset,  leftOffset,  rightOffset, onlyConnect)


def  printNode(xmlNode,  parentId=None,  aboveOffset=None,  belowOffset=None,  leftOffset=None,  rightOffset=None, onlyConnect=False):
	id = getUniqId(xmlNode)
	if not onlyConnect:
		text = getChildDescription(xmlNode)
	
		# print tkiz node similar to
		# \node[below left=0.5 and 0.2 of mother1] (child1) {Kind 1};
		print('\t\\node',  end="") 
		
		# only use relative postioning,
		# if a mother exists
		if parentId is not None:
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
	if parentId is not None:
		if belowOffset:
			# print tikiz line for connecting mother with the child
			# \draw[thick] (mother1) |- ($ (child1.north) + (0,0.25) $) -- (child1);
			print('\t\\draw[thick] (' + parentId + ') |- ($ (',  end="")
			print(id + '.north) + (0,0.25) $) -- (' + id + ');')
		elif aboveOffset is None:
			# print tikiz line for connecting married persons
			# \draw[thick] (mother1) -- (father1);
			print('\t\\draw[thick] (' + parentId + ') -- (' + id + ');')
			
	return id



def getChildDescription(xmlNode):
	text = xmlNode.get('name')
	# TODO newline 
	text += " "
	text += "* " + xmlNode.get('birth',  'UNKOWN')
	# TODO death und places
	return text


def getUniqId(xmlNode):
	# create id if no id could be found in xml structure
	id = xmlNode.get('id')
	if not id:
		text = getChildDescription(xmlNode)
		id = text.replace(" ",  "")
		# TODO lower case the hole id
		
		id = id.replace(".",  "")
		id = id.replace(",",  "")
		# TODO replace all >=8 bit characters
		# and remove special charachters
		id = id.replace("ä",  "ae")
		id = id.replace("ö",  "oe")
		id = id.replace("ü",  "ue")
		
	return id


def printXmlNode(xmlNode,  parentId=None):
	children = xmlNode.findall('child')
	childCount = len(children)
	# if the children processed buttom up
	# the positioned child should always the 
	# left one 
	childNr = childCount
	topDown = False
	return printChild(xmlNode,  parentId,  childCount,  childNr, topDown)


def processChildren(root,  motherId,  ignoreXmlElements=[]):
	children = root.findall('child')
	childCount = len(children)
	childNr = 1
	for child in children:
		childAlreadyExists = False
		for element in ignoreXmlElements:
			if element == child:
				childAlreadyExists = True
				break
		
		# only print the child,
		# if it is not a part of the ignore list
		# if it is a part of the ignore list print only the connection
		id = printChild(child,  motherId,  childCount,  childNr, True, childAlreadyExists)
		
		processChildren(child,  id,  ignoreXmlElements)
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


print('\\begin{tikzpicture}[align=center,node distance=0.2,auto,nodes={inner sep=0.3em, minimum height=3em, rectangle,draw=black, text centered,text width=4cm}]')

tree = ET.parse('family.xml')
root = tree.getroot()
children = root.findall('child')
doButtomUp = False
alreadyMarriedIds = []
for child in children:
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
		
		marriedChild = rootChildrenList[0]
		
		parentId = None
		spouseTag = marriedChild.findall('spouse')
		if len(spouseTag) >= 1:
			parentId = spouseTag[0].get('id',  None)
		
		if not parentId:
			print("ERR: Spouse tag does not contain an id attribute!")
			exit(-1)
		
		# connect the hosband to the left
		# if this woman has already married
		marrieLeft = False
		for i in range(0, len(alreadyMarriedIds)):
			if alreadyMarriedIds[i] == parentId:
				marrieLeft = True
				break
		
		# save the id that it has a right nighbour
		alreadyMarriedIds.append(parentId)
		
		leftOffset = None
		rightOffset = None
		if marrieLeft:
			leftOffset = 0.2
		else:
			rightOffset = 0.2
		
		
		# print and connect all children of rootChildrenList
		parentId = printNode(marriedChild,  parentId,  None,  None,  leftOffset,  rightOffset)
		for i in range(1, len(rootChildrenList)):
			parentId = printXmlNode(rootChildrenList[i],  parentId)
		
		# TODO if it is married connect to given id
		# buttonUp geht nicht, da ein Mann mehrmals heiraten kann
		# und damit sich mit mehreren Frauen verbinden müsste
		
		processChildren(child,  parentId,  rootChildrenList)
	else:
		id = printNode(child)
		processChildren(child,  id)
	
	# apend all other root children expecting the first one with a
	# buttom up connection in the root tree
	doButtomUp = True

print('\\end{tikzpicture}')
