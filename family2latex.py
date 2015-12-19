#! /usr/bin/python3
# Exectly one child of a root child need a spouse tag 
# regardless (außer) the first root child tree of the xml file.
# This child descripes how the other childs will connected to the first root child tree.
# Be carful, the xml structure must contain only one spouse tag 
# for all childs of the same root child
import sys
import xml.etree.ElementTree as ET

# in columns
NODE_SPOUSE_COL_SPACE = 0.5

# in cm
NODE_WIDTH = 4.2
NODE_HSPACE = 0.2
NODE_VSPACE = 0.5

MAX_FIX_OVERLAP_ITERATIONS = 10

DEBUG_MAX_FIXES = -1

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
		self.spouseRight = None
		self.spouseLeft = None
		self.children = []
		self.row = 0
		self.column = 0
		
		if mother is not None:
			self.row = mother.row + 1
			self.column = mother.column + offset
		
		allChildNodes.append(self)
		pass
	

#	def getAllNeighbours(self):
#		neighbours = []
#		neighbours += self.children
#		
#		if self.spouseRight is not None:
#			neighbours.append(self.spouseRight)
#		if self.spouseLeft is not None:
#			neighbours.append(self.spouseLeft)
#		if self.mother is not None:
#			neighbours.append(self.mother)
#		return neighbours


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
	print('\t\\node[child',  end="") 
	
	# only use relative postioning,
	# if a mother exists
	if parentNode is not None:
		print(',',  end="")
		# define which directions the rel pos should have
		relPosOffsets = []
		if aboveOffset:
			print(' above',  end="")
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
		print('=' + relPosOffString + ' of ' + parentNode.id,  end="")
	
	print('] (' + childNode.id + ') {' + childNode.text + '};')
	
	
def connectParentChild(motherId,  childId):
	# print tikiz line for connecting mother with the child
	# \draw[thick] (mother1) |- ($ (child1.north) + (0,0.25) $) -- (child1);
	print('\t\\draw[thick] (' + motherId + ') |- ($ (',  end="")
	print(childId + '.north) + (0,0.25) $) -- (' + childId + ');')
	

def connectSpouses(id1,  id2):
	# print tikiz line for connecting married persons
	# \draw[thick] (mother1) -- (father1);
	print('\t\\draw[thick] (' + id1 + ') -- node[above]{??.??.??} node[below]{Place} ++(' + id2 + ');')
#	print('\t\\draw[thick,decoration={text along path,text={path text},text align={center}},decorate] (' + id1 + ') -- (' + id2 + ');')


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
			raise Exception("ERR: Spouse tag does not contain an id attribute!")
		
		spouseNode = findChildNode(spouseId)
		if not spouseNode:
			raise Exception("ERR: child with spouse ID not already defined!")
		
		# caluclate offset for setting both nodes on same position
		columnOffset = spouseNode.column - parentNode.column
	
		if not spouseNode.spouseRight:
			# connect spouses bidirectional to the right
			spouseNode.spouseRight = parentNode
			parentNode.spouseLeft = spouseNode
			columnOffset += 1 + NODE_SPOUSE_COL_SPACE
		elif not spouseNode.spouseLeft:
			# connect spouses bidirectional to the left
			spouseNode.spouseLeft = parentNode
			parentNode.spouseRight = spouseNode
			columnOffset -= 1 + NODE_SPOUSE_COL_SPACE
		else:
			raise Exception("ERR: Not more than 2 spouses are supported!")
		
		updateColumnTillSpouse(spouseNode,  parentNode,  columnOffset,  spouseNode.row)
	
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



def updateColumnTillSpouse(lastNode,  currentNode,  columnOffset,  row):
	if not currentNode:
		return
	
	currentNode.row = row
	currentNode.column += columnOffset
	
	for childNode in currentNode.children:
		# do not run the same way back
		if childNode is not lastNode:
			updateColumnTillSpouse(currentNode,  childNode,  columnOffset,  row+1)
	
	if (currentNode.mother is not None) and (currentNode.mother is not lastNode):
		updateColumnTillSpouse(currentNode,  currentNode.mother,  columnOffset,  row-1)



def updateColumnTillMultiMother(currentNode,  columnOffset):
	if not currentNode:
		return
	
	# stop if mother has more than one child
	# so there exists a horizontal line 
	# which can be extended
	if len(currentNode.children) > 1:
		# calulate new column depending on left and right child
		newMotherColumn = (currentNode.children[-1].column + currentNode.children[0].column) / 2
		
		motherColumnOffset = newMotherColumn - currentNode.column
		# only proceed, if the mother position has changed
		if motherColumnOffset != 0:
			currentNode.column += motherColumnOffset
			# update all mothers and children of the grand mother
			if currentNode.mother is not None:
				# stop updating on this mother
				# So update all upward children
				updateColumnTillSpouse(currentNode,  currentNode.mother,  motherColumnOffset,  currentNode.mother.row)
		return
	
	currentNode.column += columnOffset
	
	if currentNode.mother is not None:
		updateColumnTillMultiMother(currentNode.mother,  columnOffset)



def updateColumnOfChildren(currentNode,  columnOffset):
	currentNode.column += columnOffset
	
	for childNode in currentNode.children:
		updateColumnOfChildren(childNode,  columnOffset)



def areChildrenMarried(node1,  node2):
	return node1.spouseLeft is node2 or node1.spouseRight is node2;


def checkOverlapps():
	for node1 in allChildNodes:
		for node2 in allChildNodes:
			if (node1 is not node2 and node1.row == node2.row):
				columnOffset = abs(node1.column - node2.column)
				if columnOffset < (1 + NODE_SPOUSE_COL_SPACE) and areChildrenMarried(node1,  node2):
					# between two spouses a spacing of NODE_SPOUSE_COL_SPACE columns is needed
					# for the text
					return fixOverlap(node1,  node2)
				elif columnOffset < 1:
					# if less than one column is between the nodes
					# there is always an overlapping,
					# because one node is exactly one column width
					return fixOverlap(node1,  node2)
	
	# nothing has been updated
	return False



fixCounter = 0
def fixOverlap(node1,  node2):
	global fixCounter
	
	print("Fixing overlapping of "+ node1.id + " " + str(node1.column) + " and " + 
		node2.id + " " + str(node2.column), file=sys.stderr)
	
	[leftNode,  rightNode] = sortNodesLeftToRight(node1,  node2)
	if leftNode is None or rightNode is None:
		return False
	
	# only 0.5 column shift is needed
	# do only 0.5 shift
	columnOffset = leftNode.column - rightNode.column + 1
	
	# add extra spacing if these children are connected because of marry
	if areChildrenMarried(leftNode,  rightNode):
		columnOffset += NODE_SPOUSE_COL_SPACE
	
	# update all sisters/brothers right of this node, too
	if rightNode.mother is not None:
		updatingStarted = False
		for childNode in rightNode.mother.children:
			if childNode is rightNode:
				updatingStarted = True
			elif updatingStarted is True:
				updateColumnOfChildren(childNode,  columnOffset)
	
	# update all children of this node
	updateColumnOfChildren(rightNode,  columnOffset)
	
	#only updates upward till a mother with more than one child
	# -> horizontal connection
	updateColumnTillMultiMother(rightNode.mother,  columnOffset)
	
	fixCounter += 1
	if DEBUG_MAX_FIXES >= 0 and fixCounter >= DEBUG_MAX_FIXES:
		raise Exception("Max fix count reached!")
	
	return True



def sortNodesLeftToRight(node1,  node2):
	# there is a direct connection to the left neighbour
	# so it would result in a crossing line,
	# if node1 would be moved
	if node1.spouseLeft is not None:
		# check if both nodes are married
		# so the left node has to leave left
		if node2 is node1.spouseLeft:
			return [node2,  node1]
		else:
			return [node1,  node2]
	if node2.spouseLeft is not None:
		if node1 is node2.spouseLeft:
			return [node1,  node2]
		else:
			return [node2,  node1]
	
	if node1.spouseRight is not None:
		return [node2,  node1]
	if node2.spouseRight is not None:
		return [node1,  node2]
	
	if not node1.mother:
		return [node2,  node1]
	if not node2.mother:
		return [node1,  node2]
	
	# mother lies more right than child
	# so this child can be shifted to the right
	if node1.mother.column > node1.column:
		return [node2,  node1]
	if node2.mother.column > node2.column:
		return [node1,  node2]
	
	if node1.mother.column > node2.mother.column:
		return [node2,  node1]
	if node2.mother.column > node1.mother.column:
		return [node1,  node2]
	
	raise Exception("WRN: No better solution found for fixing overlapping of " + node1.id + " and " + node2.id +
		". Fixing will be stopped.")



def printNodes(parentNode,  lastNode):
	for childNode in parentNode.children:
		# do not run the same way back
		if childNode is lastNode:
			continue
		
		printChild(childNode,  parentNode,  1)
		connectParentChild(parentNode.id,  childNode.id)
		printNodes(childNode,  parentNode)
	
	# only process mother, if not comming from there
	if (parentNode.mother is not None) and (parentNode.mother is not lastNode):
		# print mother node and position inverse
		# (one row above)
		printChild(parentNode.mother,  parentNode,  -1)
		connectParentChild(parentNode.mother.id,  parentNode.id)
		printNodes(parentNode.mother,  parentNode)
	
	printNodesSpouses(parentNode.spouseLeft,  parentNode,  lastNode)
	printNodesSpouses(parentNode.spouseRight,  parentNode,  lastNode)


def printNodesSpouses(spouseNode,  parentNode,  lastNode):
	if (not spouseNode):
		return
	# do not run the same way back
	if spouseNode is lastNode:
		return
	# position in the same row
	# column offset depends on colums of each spouse
	printChild(spouseNode,  parentNode,  0)
	connectSpouses(parentNode.id,  spouseNode.id)
	printNodes(spouseNode,  parentNode)



# convert the XML structure to the tree data structure (first stage)
print("INF: Reading file " + sys.argv[1], file=sys.stderr)
#tree = ET.parse("./data/family.xml")
tree = ET.parse(sys.argv[1])
root = tree.getroot()
childrenXml = root.findall('child')
for childXml in childrenXml:
	childNode = Node(childXml,  None,  0)
	processChildren(childXml,  childNode)


# move overlapping nodes (second stage)
exitCode = 0
try:
	for i in range(MAX_FIX_OVERLAP_ITERATIONS):
		if checkOverlapps() is False:
			# all overlapps are fixed
			exitCode = 1
			break
except Exception as e:
	# an overlapp could not be fixed
	print(e, file=sys.stderr)


# print the tree out (third stage)
print('\\begin{tikzpicture}[align=center,auto]')
# TODO shapes elipse
print("\t\\tikzstyle{child} = [distance=0.2cm, inner sep=0.3em, minimum height=3em, rectangle, draw=black, text centered, text width=4cm]")
printChild(allChildNodes[0])
printNodes(allChildNodes[0],  None)
print('\\end{tikzpicture}')

exit(exitCode)
