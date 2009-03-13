#!/usr/bin/env python
from __future__ import with_statement

import sys, re

import logging

import BeautifulSoup

class abstractmethod(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwds):
        raise NotImplementedError("method %s is abstract." % self.func.func_name)

class DOMException(object):
    def __init__(self, code):
        self.code = code
        
    INDEX_SIZE_ERR                 = 1  # If index or size is negative, or greater than the allowed value
    DOMSTRING_SIZE_ERR             = 2  # If the specified range of text does not fit into a DOMString
    HIERARCHY_REQUEST_ERR          = 3  # If any node is inserted somewhere it doesn't belong
    WRONG_DOCUMENT_ERR             = 4  # If a node is used in a different document than the one that created it (that doesn't support it)
    INVALID_CHARACTER_ERR          = 5  # If an invalid or illegal character is specified, such as in a name. 
    NO_DATA_ALLOWED_ERR            = 6  # If data is specified for a node which does not support data
    NO_MODIFICATION_ALLOWED_ERR    = 7  # If an attempt is made to modify an object where modifications are not allowed
    NOT_FOUND_ERR                  = 8  # If an attempt is made to reference a node in a context where it does not exist
    NOT_SUPPORTED_ERR              = 9  # If the implementation does not support the type of object requested
    INUSE_ATTRIBUTE_ERR            = 10 # If an attempt is made to add an attribute that is already in use elsewhere
    
class Node(object):
    # NodeType
    ELEMENT_NODE                   = 1
    ATTRIBUTE_NODE                 = 2
    TEXT_NODE                      = 3
    CDATA_SECTION_NODE             = 4
    ENTITY_REFERENCE_NODE          = 5
    ENTITY_NODE                    = 6
    PROCESSING_INSTRUCTION_NODE    = 7
    COMMENT_NODE                   = 8
    DOCUMENT_NODE                  = 9
    DOCUMENT_TYPE_NODE             = 10
    DOCUMENT_FRAGMENT_NODE         = 11
    NOTATION_NODE                  = 12
    
    def __init__(self, doc):
        self.doc = doc
        
    def __eq__(self, other):
        return hasattr(other, "doc") and self.doc == other.doc
        
    def __ne__(self, other):
        return not self.__eq__(other)
    
    @property
    @abstractmethod
    def nodeType(self):
        pass
    
    @property
    @abstractmethod
    def nodeName(self):
        pass
    
    @abstractmethod
    def getNodeValue(self):
        return None
    
    @abstractmethod
    def setNodeValue(self, value):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
    
    nodeValue = property(getNodeValue, setNodeValue)
    
    @property
    def attributes(self):
        return None
    
    @property
    def childNodes(self):
        return NodeList(self.doc, [])
        
    @property
    def firstChild(self):
        return None
            
    @property
    def lastChild(self):
        return None
            
    @property
    def nextSibling(self):
        return None
            
    @property
    def previousSibling(self):
        return None
            
    @property
    def parentNode(self):
        return None
    
    @property
    def ownerDocument(self):
        return self.doc
    
    def insertBefore(self, newChild, refChild):
        raise DOMException(DOMException.HIERARCHY_REQUEST_ERR)
    
    def replaceChild(self, newChild, oldChild):
        raise DOMException(DOMException.HIERARCHY_REQUEST_ERR)
    
    def removeChild(self, oldChild):
        raise DOMException(DOMException.NOT_FOUND_ERR)
    
    def appendChild(self, newChild):
        raise DOMException(DOMException.HIERARCHY_REQUEST_ERR)
    
    def hasChildNodes(self):
        return False
    
    @abstractmethod
    def cloneNode(self, deep):
        pass
    
class NodeList(object):
    def __init__(self, doc, nodes):
        self.doc = doc
        self.nodes = nodes
    
    def item(self, index):        
        return Element(self.doc, self.nodes[index]) if 0 <= index and index < len(self.nodes) else None
    
    @property
    def length(self):
        return len(self.nodes)

class NamedNodeMap(object):
    def __init__(self, nodes):        
        self.nodes = nodes
        
    def getNamedItem(self, name):
        return self.nodes.get(name)
    
    def setNamedItem(self, node):
        self.nodes[node.nodeName] = node
    
    def removeNamedItem(self, name):
        if not self.nodes.has_key(name):
            raise DOMException(DOMException.NOT_FOUND_ERR)
            
        del self.nodes[name]
    
    def item(self, index):
        return self.nodes.get(self.nodes.keys()[index])
    
    @property
    def length(self):
        return len(self.nodes)
        
class Attr(Node):
    def __init__(self, parent, attr):
        self.parent = parent
        self.attr = attr
        
    @property
    def nodeType(self):
        return Node.ATTRIBUTE_NODE
       
    @property        
    def nodeName(self):
        return self.attr
    
    def getNodeValue(self):
        return self.getValue()
    
    def setNodeValue(self, value):
        return self.setValue(value)
        
    nodeValue = property(getNodeValue, setNodeValue)
    
    @property
    def childNodes(self):
        return NodeList(self.parent.doc, [])
    
    @property
    def parentNode(self):
        return self.parent
        
    @property
    def ownerDocument(self):
        return self.parent.doc
    
    @property
    def name(self):
        return self.attr
    
    def specified(self):
        return self.parent.has_key(self.attr)
    
    def getValue(self):
        return self.parent.tag[self.attr] if self.parent.tag.has_key(self.attr) else ""
        
    def setValue(self, value):
        self.parent.tag[self.attr] = value
        
    value = property(getValue, setValue)
    
class Element(Node):
    def __init__(self, doc, tag):
        Node.__init__(self, doc)
        
        self.tag = tag
        
    def __eq__(self, other):
        return Node.__eq__(self, other) and hasattr(other, "tag") and self.tag == other.tag
        
    @property
    def nodeType(self):
        return Node.ELEMENT_NODE
       
    @property
    def nodeName(self):
        return self.tagName
    
    @property
    def nodeValue(self):
        return None
    
    def childNodes(self):
        return NodeList(self.doc, self.tag.contents)
        
    def findChild(child):
        try:
            return self.tag.contents.index(newChild.tag)
        except ValueError:
            return -1
        
    def insertBefore(self, newChild, refChild):
        index = self.findChild(newChild)
        
        self.tag.insert(index if index >= 0 else len(self.tag.contents), refChild.tag)

    def replaceChild(self, newChild, oldChild):
        index = self.findChild(oldChild.tag)
        
        if index < 0:
            raise DOMException(DOMException.NOT_FOUND_ERR)
            
        self.tag.contents[index] = oldChild.tag
    
    def removeChild(self, oldChild):
        raise DOMException(DOMException.NOT_FOUND_ERR)
    
    def appendChild(self, newChild):
        raise DOMException(DOMException.HIERARCHY_REQUEST_ERR)
    
    def hasChildNodes(self):
        return False
    
    @property
    def tagName(self):
        return self.tag.name
    
    def getAttribute(self, name):
        return self.tag[name] if self.tag.has_key(name) else ""
        
    def setAttribute(self, name, value):
        self.tag[name] = value
        
    def removeAttribute(self, name):
        del self.tag[name]
        
    def getAttributeNode(self, name):
        return Attr(self, name) if self.tag.has_key(name) else None
    
    def setAttributeNode(self, attr):
        self.tag[attr.name] = attr.value
    
    def removeAttributeNode(self, attr):
        del self.tag[attr.name]
    
    def getElementsByTagName(self, name):
        return NodeList(self.doc, self.tag.findAll(name))
    
    def normalize(self):
        pass

class CharacterData(Node):
    def __init__(self, doc, str):
        Node.__init__(self, doc)
        
        self.str = str
        
    def getData(self):
        return unicode(self.str)
        
    def setData(self, data):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
        
    data = property(getData, setData)
    
    @property
    def length(self):
        return len(self.str)
        
    def substringData(self, offset, count):
        return self.str[offset:offset+count]
        
    def appendData(self, arg):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
        
    def insertData(self, offset, arg):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
        
    def deleteData(self, offset, count):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
        
    def replaceData(self, offset, count, arg):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)

class Text(CharacterData):
    def splitText(self, offset):
        raise DOMException(DOMException.NO_MODIFICATION_ALLOWED_ERR)
        
class CDATASection(Text):
    pass

class Comment(CharacterData):
    pass

class DocumentFragment(Node):
    pass

class DocumentType(Node):
    RE_DOCTYPE = re.compile("^DOCTYPE (\w+)", re.M + re.S)
    
    def __init__(self, doc, tag):
        Node.__init__(self, doc)
        
        self.parse(tag)
        
    def parse(self, text):
        m = self.RE_DOCTYPE.match(text)
        
        self._name = m.group(1) if m else ""
        
    @property
    def name(self):
        return self._name
    
    @property
    def entities(self):
        raise NotImplementedError()
    
    @property
    def notations(self):
        raise NotImplementedError()
    
class Notation(Node):
    @property
    def publicId(self):
        pass
    
    @property
    def systemId(self):
        pass
    
class Entity(Node):
    @property
    def publicId(self):
        pass
    
    @property
    def systemId(self):
        pass
    
    @property
    def notationName(self):
        pass
    
class EntityReference(Node):
    def __init__(self, doc, name):
        Node.__init__(self, doc)
        
        self.name = name
        
    def nodeName(self):
        return self.name
    
class ProcessingInstruction(Node):
    def __init__(self, doc, target, data):
        self._target = target
        self.data = data
        
    @property
    def target(self):
        return self._target   

class Document(Node):
    @property
    def nodeType(self):
        return Node.DOCUMENT_NODE
    
    @property
    def nodeName(self):
        return "#document"
    
    @property
    def nodeValue(self):
        return None
    
    @property
    def doctype(self):
        for tag in self.doc:
            if isinstance(tag, BeautifulSoup.Declaration) and tag.startswith("DOCTYPE"):
                return DocumentType(self.doc, tag)
                
        return None
    
    @property
    def implementation(self):
        pass
    
    @property
    def documentElement(self):
        return Element(self, self.doc.find('html'))
    
    def createElement(self, tagname):        
        return Element(self, BeautifulSoup.Tag(self.doc, tagname))
    
    def createDocumentFragment(self):
        return DocumentFragment(self)
    
    def createTextNode(self, data):
        return Text(self, data)
    
    def createComment(self, data):
        return Comment(self, data)
    
    def createCDATASection(self, data):
        return CDATASection(self, data)
    
    def createProcessingInstruction(self, target, data):
        return ProcessingInstruction(self, target, data)
    
    def createAttribute(self, name):
        pass
    
    def createEntityReference(self, name):
        return EntityReference(self, name)
    
    def getElementsByTagName(self, tagname):
        pass
    
class DOMImplementation(Document):
    def hasFeature(feature, version):
        pass    
    
def getDOMImplementation():
    return DOMImplementation()
    
def parseString(html):
    return DOMImplementation(BeautifulSoup.BeautifulSoup(html))
    
def parse(file):
    if isinstance(file, StringTypes):
        with open(file, 'r') as f:
            return parseString(f.read())
    
    return parseString(file.read())
    
import unittest

class DocumentTest(unittest.TestCase):
    def setUp(self):
        self.doc = parseString("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <!-- This is a comment -->
        <title>this is a test</title>
        <script type="text/javascript"> 
        //<![CDATA[
        function load()
        {
            alert("load");
        }
        function unload()
        {
            alsert("unload");
        }
        //]]>
        </script>         
    </head>
    <body onload="load()" onunload="unload()">
        <p1>Hello World!</p1>
    </body>
</html>""")
        
        self.assert_(self.doc)
        
    def testNode(self):
        self.assertEquals(Node.DOCUMENT_NODE, self.doc.nodeType)
        self.assertEquals("#document", self.doc.nodeName)
        self.failIf(self.doc.nodeValue)
        
        html = self.doc.documentElement
        
        self.assert_(html)        
        self.assertEquals(Node.ELEMENT_NODE, html.nodeType)
        self.assertEquals("html", html.nodeName)
        self.failIf(html.nodeValue)
        
        attr = html.getAttributeNode("xmlns")
        
        self.assert_(attr)

        self.assertEquals(Node.ATTRIBUTE_NODE, attr.nodeType)
        self.assertEquals("xmlns", attr.nodeName)
        self.assertEquals("http://www.w3.org/1999/xhtml", attr.nodeValue)
        
    def testDocument(self):
        pass
    
    def testDocumentType(self):
        doctype = self.doc.doctype
        
        self.assert_(doctype)
        
        self.assertEquals("html", doctype.name)
                
    def testElement(self):
        html = self.doc.documentElement
        
        self.assertEquals("html", html.tagName)
        self.assertEquals("http://www.w3.org/1999/xhtml", html.getAttribute("xmlns"))
        self.assert_(html.getAttributeNode("xmlns"))
        
        
    def testAttr(self):
        html = self.doc.documentElement
        
        attr = html.getAttributeNode("xmlns")
        
        self.assert_(attr)
        
        self.assertEquals(html, attr.parentNode)
        self.assert_(attr.childNodes)
        self.failIf(attr.firstChild)
        self.failIf(attr.lastChild)
        self.failIf(attr.previousSibling)
        self.failIf(attr.nextSibling)
        self.failIf(attr.attributes)
        
        self.assertFalse(attr.hasChildNodes())        
        
        self.assertEquals(self.doc, attr.ownerDocument)

        self.assertEquals("xmlns", attr.name)        
        self.assert_(True, attr.specified)
        
        self.assertEquals("http://www.w3.org/1999/xhtml", attr.value)
        
        attr.value = "test"
        
        self.assertEquals("test", attr.value)
        self.assertEquals("test", html.getAttribute("xmlns"))
        
        body = html.getElementsByTagName("body").item(0)
        
        self.assert_(body)
        
        onload = body.getAttributeNode("onload")
        onunload = body.getAttributeNode("onunload")
        
        self.assert_(onload)
        self.assert_(onunload)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG if "-v" in sys.argv else logging.WARN,
                        format='%(asctime)s %(levelname)s %(message)s')
    
    unittest.main()