import xml.etree.ElementTree as et

#Pi = 3.141592653589793238462643383279502884 # 180 degrees

#====================================================
# NOTE: gid = 0 means no tile is associated with it
# gid = 1 is the 0th tile from the tileset, it 
# corresponds to "id = 0" in the tileset description
# So we need to subtract 1 from gid's, thus getting 
# gid = -1 for no tile
#====================================================

# Map file structure:
# MAP
#   PROPERTIES
#      property 1 (name, value)
#      property 2 (name, value)
#      .........
#      property i (name, value)
#   TILESET #1 (firstgid <-- index of the first tile, name <-- name of the tileset
#      image (source, widthPX, heightPX)
#      tile 1 (id)
#         PROPERTIES
#            property 1 (name, value) # E.g. name = "prefabName", value="floorTIle01"
#            property 2 (name, value)
#            .........
#            property j (name, value)
#      tile 2 (id)
#      ......
#      tile k (id)
#   TILESET #2
#   .........
#   TILESET #N
#   LAYER #1 (name = "floor", "wall", "ceiling" etc)
#      data
#         tile 1 (gid)
#         tile 2
#         ......
#         tile p
#   LAYER #2
#   .........
#   LAYER #M

# CONVENTIONS:
# 1. single tileset per layer
# 2. tileset name is the same as layer's name and the same as image file name
# EXCEPTION: wall layers: wallTilesN, wallTilesS, wallTilesE, wallTilesW
# read a dubgeon TXT file and create a blender mesh for it
#the file has

class DungeonFileReader():
    '''Class responsible for reading the description of the dungeon and 
    creating structures describing the dungeon (floor, walls, ceiling etc.)'''
    def __init__(self):
        self.mapFileName = ""
        self.mapWidth = 1
        self.mapHeight = 1
        # XML-tree describing the map
        self.mapTree = 0
        # root of the map-tree
        self.root = 0
        
        # the list of tilesets (as trees) used
        #!NOTE: there must ONE tileset per layer :!
        # however same tileset may be used in different 
        # layers
        self.tilesets = []
        
        # the list of layers (as trees) present in the map
        #NOTE!: there must one tileset per layer :!
        self.layers = []
        self.floorLayer = []
        # North, South, East, and West walls layers
        self.wallLayerN = []
        self.wallLayerS = []
        self.wallLayerE = []
        self.wallLayerW = []
        
        self.columnLayer = []
        self.ceilingLayer = []
        
        #"actual" size of the floor tile in meters
        self.floorTileSize = 3.67267
        self.ceilingHeight = 3.0
        

    def readDungeonFromFile( self, fileName ):
        '''Process XML tree, describing the structure of the dungeon
        in the file and create arrays of models: floor, wall, ceiling etc'''
        self.mapFileName = fileName
        self.mapTree = et.parse(self.mapFileName)
        self.root = self.mapTree.getroot()
        self.mapWidth = int( self.root.get('width') )
        self.mapHeight = int( self.root.get('height') )
        self.tilesets = self.getNodes( self.root, "tileset" )
        self.layers = self.getNodes( self.root, "layer" )
        
        # processing floor layer
        #========================= FLOOR ==============================================================
        self.floorLayer = self.readLayer( self.layers, "floorTiles" )
        #TODO: Incorporade listToMatrix into the readLayer?
        self.floorLayer = self.listToMatrix( self.floorLayer, self.mapWidth )
        # Converting floor layer from matrix of id's
        # into matrices of prefab/model names
        firstID = self.getFirstGID( self.root, 'floorTiles' )
        for i in range( 0, self.mapWidth ):
            for j in range( 0, self.mapHeight ):
                self.floorLayer[i][j] = self.getPrefabName( self.tilesets, "floorTiles", self.floorLayer[i][j] - firstID )
        #========================= END OF FLOOR =====================================================
        
        # processing wall layer
        #========================== WALLS ===========================================================
        # reading North, South, East, and West walls layers
        self.wallLayerN = self.readLayer( self.layers, "wallTilesN" )
        self.wallLayerN = self.listToMatrix( self.wallLayerN, self.mapWidth )
        
        self.wallLayerS = self.readLayer( self.layers, "wallTilesS" )
        self.wallLayerS = self.listToMatrix( self.wallLayerS, self.mapWidth )
        
        self.wallLayerE = self.readLayer( self.layers, "wallTilesE" )
        self.wallLayerE = self.listToMatrix( self.wallLayerE, self.mapWidth )
        
        self.wallLayerW = self.readLayer( self.layers, "wallTilesW" )
        self.wallLayerW = self.listToMatrix( self.wallLayerW, self.mapWidth )        
        
        # Converting wall layers from matrix of id's
        # into matrices of prefab/model names
        # ID of the first tile from the wallTiles tileset
        firstID = self.getFirstGID( self.root, 'wallTiles' )
        for i in range( 0, self.mapWidth ):
            for j in range( 0, self.mapHeight ):
                self.wallLayerN[i][j] = self.getPrefabName( self.tilesets, "wallTiles", self.wallLayerN[i][j] - firstID )
                self.wallLayerS[i][j] = self.getPrefabName( self.tilesets, "wallTiles", self.wallLayerS[i][j] - firstID )
                self.wallLayerE[i][j] = self.getPrefabName( self.tilesets, "wallTiles", self.wallLayerE[i][j] - firstID )
                self.wallLayerW[i][j] = self.getPrefabName( self.tilesets, "wallTiles", self.wallLayerW[i][j] - firstID )        
        #============================== END OF WALLS ================================================
        
        #processing column layer
        #=============================== COLUMNS ====================================================
        self.columnLayer = self.readLayer( self.layers, "columns" )
        self.columnLayer = self.listToMatrix( self.columnLayer, self.mapWidth )
        # Converting column layer from matrix of id's
        # into matrices of prefab/model names
        firstID = self.getFirstGID( self.root, 'columnTiles' )
        for i in range( 0, self.mapWidth ):
            for j in range( 0, self.mapHeight ):
                self.columnLayer[i][j] = self.getPrefabName( self.tilesets, "columnTiles", self.columnLayer[i][j] - firstID )                
        #=============================== END OF COLUMNS ==============================================
        
        # processing ceiling layer
        #================================ CEILING =========================================================
        self.ceilingLayer = self.readLayer( self.layers, "ceilingTiles" )
        self.ceilingLayer = self.listToMatrix( self.ceilingLayer, self.mapWidth )
        # Converting ceiling layer from matrix of id's
        # into matrices of prefab names        
        firstID = self.getFirstGID( self.root, 'ceilingTiles' )
        for i in range( 0, self.mapWidth ):
            for j in range( 0, self.mapHeight ):
                self.ceilingLayer[i][j] = self.getPrefabName( self.tilesets, "ceilingTiles", self.ceilingLayer[i][j] - firstID )      
        #=============================== END OF CEILING ===================================================

    
    def listToMatrix( self, inList, inWidth ):
        '''Reshapes the input list into a rectangular matrix (list of lists) 
        of a specified width'''
        outList = []
        for i in range(0, int(len(inList)/inWidth)):
            outList.append( inList[i*inWidth:(i+1)*inWidth] )
        return outList
        
    def readLayer( self, layers, layerName ):
        '''Extracts a list, representing a map of 
        a particular layer, from a list of layers' trees '''
        layer = []
        for i in layers:
            if (i.get('name') == layerName):
                for j in i:
                    if (j.tag == "data"):
                        for k in j:
                            layer.append( int(k.get('gid')) ) # see NOTE in the head of this file
        return layer
        
    def getNodes( self, root, nodeName ):
        '''Returns a list of trees(children of root)
        whose tags correspond to the nodeName '''
        nodes = []
        for child in root:
            if ( nodeName == child.tag ):
                nodes.append(child)
        return nodes
    
    def getPrefabName( self, tilesets, layerName, tileID ):
        '''Returs a string-name of the 3D object, corresponding to
        a given tile ID. This object is used in constructing a level'''
        prefabName = "None"
        for t in tilesets:
            if ( t.get("name") == layerName ):
                for i in t.findall("tile"):
                    if ( int(i.get("id")) == tileID ):
                        for j in i.findall("properties"):
                            for k in j.findall("property"):
                                if ( k.get("name") == "prefabName" ):
                                    prefabName = k.get("value")
        return prefabName
    
    def getFirstGID( self, root, tilesetName ):
        '''Returns id of the first tile in the tileset.'''
        fgid = 0
        for child in root.findall('tileset'):
            if ( child.get('name') == tilesetName ):
                fgid = child.get('firstgid')
        return int(fgid)

