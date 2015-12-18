#! /usr/bin/python3
# Exectly one child of a root child need a spouse tag 
# regardless (außer) the first root child tree of the xml file.
# This child descripes how the other childs will connected to the first root child tree.
# Be carful, the xml structure must contain only one spouse tag 
# for all childs of the same root child
import xml.etree.ElementTree as ET

# in cm
NODE_WIDTH = 4.2
NODE_HSPACE = 0.2
NODE_VSPACE = 0.5

# this is used for searching the node with the correct ID
# speed up instead of iterating through the family tree data structure
allChildNodes = []

def findChildNode(childId):
	for childNode in allChildNodes:
		if childNode.id == childId:
			return childNode
	return None


class Node :
	def __init__(self,  xml,  mother,  offset) :
		self.id = getUniqId(xml)
		self.text = getChildDescription(xml)
		self.mother = mother
		self.spouses = []
		self.children = []
		self.column = 0
		
		if mother is not None:
			self.column = mother.column + offset
		
		allChildNodes.append(self)
		pass


def printChild(childNode,  parentNode=None,  rowOffset=1):
	leftOffset = 0.0
	rightOffset = 0.0
	
	if parentNode is not None:
		childOffset = childNode.column - parentNode.column
		if childOffset < 0:
			leftOffset = NODE_HSPACE + (-childOffset - 1) * (NODE_WIDTH + NODE_HSPACE)
		elif childOffset > 0:
			rightOffset = NODE_HSPACE + (childOffset - 1) * (NODE_WIDTH + NODE_HSPACE)
			
	aboveOffset = None;
	belowOffset = None;
	if rowOffset > 0:
		belowOffset = NODE_VSPACE
	if rowOffset < 0:
		aboveOffset = NODE_VSPACE
	
	return printNode(childNode,  parentNode,  aboveOffset,  belowOffset,  leftOffset,  rightOffset)


def  printNode(childNode,  parentNode=None,  aboveOffset=None,  belowOffset=None,  leftOffset=None,  rightOffset=None):
	# print tkiz node similar to
	# \node[below left=0.5 and 0.2 of mother1] (child1) {Kind 1};
	print('\t\\node',  end="") 
	
	# only use relative postioning,
	# if a mother exists
	if parentNode is not None:
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
		print('=' + relPosOffString + ' of ' + parentNode.id + '] ',  end="")
	
	print('(' + childNode.id + ') {' + childNode.text + '};')
	
	
def connectParentChild(motherId,  childId):
	# print tikiz line for connecting mother with the child
	# \draw[thick] (mother1) |- ($ (child1.north) + (0,0.25) $) -- (child1);
	print('\t\\draw[thick] (' + motherId + ') |- ($ (',  end="")
	print(childId + '.north) + (0,0.25) $) -- (' + childId + ');')
	

def connectSpouses(id1,  id2):
	# print tikiz line for connecting married persons
	# \draw[thick] (mother1) -- (father1);
	print('\t\\draw[thick] (' + id1 + ') -- (' + id2 + ');')


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


def processChildren(parentXml,  parentNode):
	# check for spouse tag for married connections
	spouseTagsXml = parentXml.findall('spouse')
	for spouseTagXml in spouseTagsXml:
		spouseId = spouseTagXml.get('id',  None)
		if not spouseId:
			print("ERR: Spouse tag does not contain an id attribute!")
			exit(-1)
			
		spouseNode = findChildNode(spouseId)
		if not spouseNode:
			print("ERR: child with spouse ID not already defined!")
			exit(-1)
			
		# connect spouses bidirectional
		parentNode.spouses.append(spouseNode)
		spouseNode.spouses.append(parentNode)
	
	# TODO fix all position offsets of all upper persons if married
	
	# process children of this mother
	childrenXml = parentXml.findall('child')
	childCount = len(childrenXml)
	childNr = 0
	for childXml in childrenXml:
		# calulate position offset in columns
		offset = childNr - ( (childCount / 2) - 0.5 )
		childNode = Node(childXml,  parentNode,  offset)
		parentNode.children.append(childNode)
		processChildren(childXml,  childNode)
		childNr += 1


def printNodes(parentNode,  lastNode):
	for childNode in parentNode.children:
		# do not run the same way back
		if childNode is lastNode:
			continue
		
		printChild(childNode,  parentNode)
		connectParentChild(parentNode.id,  childNode.id)
		printNodes(childNode,  parentNode)
	
	# only process mother, if not comming from there
	if (parentNode.mother is not None) and (parentNode.mother is not lastNode):
		# print mother node and position inverse
		# (one row above)
		printChild(parentNode.mother,  parentNode,  -1)
		connectParentChild(parentNode.mother.id,  parentNode.id)
		printNodes(parentNode.mother,  parentNode)

	for spouseNode in parentNode.spouses:
		# do not run the same way back
		if spouseNode is lastNode:
			continue
		# position in the same row
		# column offset depends on colums of each spouse
		printChild(spouseNode,  parentNode,  0)
		connectSpouses(parentNode.id,  spouseNode.id)
		printNodes(spouseNode,  parentNode)


rootChildNode = None

tree = ET.parse('family.xml')
root = tree.getroot()
childrenXml = root.findall('child')
for childXml in childrenXml:
	childNode = Node(childXml,  None,  0)
	processChildren(childXml,  childNode)
	
	# TODO set if no sqouse tag
	# TODO warn if already set and no second sqouse tag
	if not rootChildNode:
		rootChildNode = childNode


print('\\begin{tikzpicture}[align=center,node distance=0.2cm,auto,nodes={inner sep=0.3em, minimum height=3em, rectangle,draw=black, text centered,text width=4cm}]')
printChild(rootChildNode)
printNodes(rootChildNode,  None)
print('\\end{tikzpicture}')
