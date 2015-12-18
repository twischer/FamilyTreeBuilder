#! /usr/bin/python3
# Exectly one child of a root child need a spouse tag 
# regardless (außer) the first root child tree of the xml file.
# This child descripes how the other childs will connected to the first root child tree.
# Be carful, the xml structure must contain only one spouse tag 
# for all childs of the same root child
import xml.etree.ElementTree as ET


class Node :
	def __init__(self,  xml,  mother=None) :
		self.id = getUniqId(xml)
		self.text = getChildDescription(xml)
		self.mother = mother
		self.married = []
		self.children = []
		self.column = 0
		pass



def printChild(childNode,  parentId=None,  childCount=0,  childNr=0, topDown=True):
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
	
	return printNode(childNode,  parentId,  aboveOffset,  belowOffset,  leftOffset,  rightOffset)


def  printNode(childNode,  parentId=None,  aboveOffset=None,  belowOffset=None,  leftOffset=None,  rightOffset=None):
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
	
	print('(' + childNode.id + ') {' + childNode.text + '};')
	
	
def connectParentChild(motherId,  childId):
	# print tikiz line for connecting mother with the child
	# \draw[thick] (mother1) |- ($ (child1.north) + (0,0.25) $) -- (child1);
	print('\t\\draw[thick] (' + motherId + ') |- ($ (',  end="")
	print(childId + '.north) + (0,0.25) $) -- (' + childId + ');')
	

def connectMarried(id1,  id2):
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
	childrenXml = parentXml.findall('child')
	for childXml in childrenXml:
		childNode = Node(childXml,  parentNode)
		parentNode.children.append(childNode)
		processChildren(childXml,  childNode)
		


#def findRootPath(parent):
#	if parent.find('spouse') is not None:
#		subRootChildrenList = []
#		subRootChildrenList.append(parent)
#		return subRootChildrenList
#	else:
#		children = parent.findall('child')
#		for child in children:
#			# check childs of this child for spouse tag
#			subRootChildrenList = findRootPath(child)
#			if subRootChildrenList:
#				subRootChildrenList.append(parent)
#				return subRootChildrenList
#		return None


def printNodes(parentNode):
	childCount = len(parentNode.children)
	childNr = 1
	for childNode in parentNode.children:
		printChild(childNode,  parentNode.id,  childCount,  childNr)
		connectParentChild(parentNode.id,  childNode.id)
		printNodes(childNode)
		childNr += 1



rootChildNode = None

tree = ET.parse('family.xml')
root = tree.getroot()
childrenXml = root.findall('child')
for childXml in childrenXml:
	childNode = Node(childXml)
	processChildren(childXml,  childNode)
	
	# TODO set if no sqouse tag
	# TODO warn if already set and no second sqouse tag
	if rootChildNode is None:
		rootChildNode = childNode


print('\\begin{tikzpicture}[align=center,node distance=0.2,auto,nodes={inner sep=0.3em, minimum height=3em, rectangle,draw=black, text centered,text width=4cm}]')
printChild(rootChildNode)
printNodes(rootChildNode)
print('\\end{tikzpicture}')
