import bpy
import random
import xml.etree.ElementTree as et

Pi = 3.141592653589793238462643383279502884 # 180 degrees

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

def ListToMatrix( inList, inWidth ):
    '''Reshapes the input list into a rectangular matrix'''
    outList = []
    for i in range(0, int(len(inList)/inWidth)):
        outList.append( inList[i*inWidth:(i+1)*inWidth] )
    return outList

def ReadLayer( layers, layerName):
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


def GetNodes( root, nodeName ):
    '''Returns a list of trees(children of root)
    whose tags correspond to the nodeName '''
    nodes = []
    for child in root:
        if ( child.tag == nodeName ):
            nodes.append(child)
    return nodes


def GetPrefabName( tilesets, layerName, tileID ):
    '''Returs a name of the 3D object, corresponding to
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


def getFirstGID( root, tilesetName ):
    '''Returns id of the first tile in the tileset.'''
    fgid = 0
    for child in root.findall('tileset'):
        if ( child.get('name') == tilesetName ):
            fgid = child.get('firstgid')
    return int(fgid)
 
# getting the file name to process. Should come in from the command line args
mapFileName = "c:/Users/seldon/Documents/My Games/Design/GOLD/BGETest/tmx/testMap.tmx"
 
mapTree = et.parse(mapFileName)
root = mapTree.getroot()
# determining the size of the map
mapWidth = int( root.get('width') )
mapHeight = int( root.get('height') )

# the list of tilesets used
#!: there must one tileset per layer :!
tilesets = GetNodes( root, "tileset" )
# the list of layers present in the map
#!: there must one tileset per layer :!
layers = GetNodes( root, "layer")

#========================= FLOOR ==============================================================
floorLayer = ReadLayer( layers, "floorTiles" )
floorLayer = ListToMatrix( floorLayer, mapWidth )
# Converting floor layer from matrix of id's
# into matrices of prefab names
firstID = getFirstGID(root, 'floorTiles')
for i in range(0, mapWidth):
    for j in range(0, mapHeight):
        floorLayer[i][j] = GetPrefabName( tilesets, "floorTiles", floorLayer[i][j] - firstID )
#========================= END OF FLOOR =====================================================


#========================== WALLS ===========================================================
# reading North, South, East, and West walls layers
wallLayerN = ReadLayer( layers, "wallTilesN" )
wallLayerN = ListToMatrix( wallLayerN, mapWidth )

wallLayerS = ReadLayer( layers, "wallTilesS" )
wallLayerS = ListToMatrix( wallLayerS, mapWidth )

wallLayerE = ReadLayer( layers, "wallTilesE" )
wallLayerE = ListToMatrix( wallLayerE, mapWidth )

wallLayerW = ReadLayer( layers, "wallTilesW" )
wallLayerW = ListToMatrix( wallLayerW, mapWidth )

#wallBoxLayer = ReadLayer( layers, "wallBoxes" )
#wallBoxLayer = ListToMatrix( wallBoxLayer, mapWidth )
#
#wallChainLayer = ReadLayer( layers, "chainTiles" )
#wallChainLayer = ListToMatrix( wallChainLayer, mapWidth )
#
#wallTorchLayer = ReadLayer( layers, "torchTiles" )
#wallTorchLayer = ListToMatrix( wallTorchLayer, mapWidth )

# Converting wall layers from matrix of id's
# into matrices of prefab names
firstID = getFirstGID(root, 'wallTiles')
for i in range(0, mapWidth):
    for j in range(0, mapHeight):
        wallLayerN[i][j] = GetPrefabName( tilesets, "wallTiles", wallLayerN[i][j] - firstID )
        wallLayerS[i][j] = GetPrefabName( tilesets, "wallTiles", wallLayerS[i][j] - firstID )
        wallLayerE[i][j] = GetPrefabName( tilesets, "wallTiles", wallLayerE[i][j] - firstID )
        wallLayerW[i][j] = GetPrefabName( tilesets, "wallTiles", wallLayerW[i][j] - firstID )
        # NOTE: wall boxes are stored in the same tileset as wall tiles
        # same goes for the torch holders
        # I think they belong together
        #wallBoxLayer[i][j] = GetPrefabName( tilesets, "wallTiles", wallBoxLayer[i][j] - firstID )
        #wallTorchLayer[i][j] = GetPrefabName( tilesets, "wallTiles", wallTorchLayer[i][j] - firstID )


# Converting wall chain layers from matrix of id's
# into matrices of prefab names
#firstID = getFirstGID(root, 'chainTiles')
#for i in range(0, mapWidth):
#    for j in range(0, mapHeight):
#        wallChainLayer[i][j] = GetPrefabName( tilesets, "chainTiles", wallChainLayer[i][j] - firstID )
#============================== END OF WALLS ================================================


#=============================== COLUMNS ====================================================
columnLayer = ReadLayer( layers, "columns" )
columnLayer = ListToMatrix( columnLayer, mapWidth )
# Converting column layer from matrix of id's
# into matrices of prefab names
firstID = getFirstGID(root, 'columnTiles')
for i in range(0, mapWidth):
    for j in range(0, mapHeight):
        columnLayer[i][j] = GetPrefabName( tilesets, "columnTiles", columnLayer[i][j] - firstID )        

#=============================== END OF COLUMNS ==============================================


##=============================== CEILING BARS ===================================================
#ceilingBarLayer = ReadLayer( layers, "ceilingBars" )
#ceilingBarLayer = ListToMatrix( ceilingBarLayer, mapWidth )
## Converting ceiling bar layer from matrix of id's
## into matrices of prefab names
#firstID = getFirstGID(root, 'ceilingBars')
#for i in range(0, mapWidth):
#    for j in range(0, mapHeight):
#        ceilingBarLayer[i][j] = GetPrefabName( tilesets, "ceilingBars", ceilingBarLayer[i][j] - firstID )      
##=============================== END OF CEILING BARS ===============================================


#================================ CEILING =========================================================
ceilingLayer = ReadLayer( layers, "ceilingTiles" )
ceilingLayer = ListToMatrix( ceilingLayer, mapWidth )
# Converting ceiling layer from matrix of id's
# into matrices of prefab names
# TODO: GetFirstID ! to subtract properly!
firstID = getFirstGID(root, 'ceilingTiles')
for i in range(0, mapWidth):
    for j in range(0, mapHeight):
        ceilingLayer[i][j] = GetPrefabName( tilesets, "ceilingTiles", ceilingLayer[i][j] - firstID )      
#=============================== END OF CEILING ===================================================


floorTileSize = 3.67267 #3.0

duplicateLinked = False
#making sure nothing is selected in the scene
bpy.ops.object.select_all(action='DESELECT')


# ++++++++++++++++++++++++ POPULATING LAYERS +++++++++++++++++++++++++++++++++++++++++++++++

# Scene layers' masks
floor = [False]*20 # none of the layers are active
floor[1] = True

wall = [False]*20
wall[2] = True

column = [False]*20
column[3] = True

ceiling = [False]*20
ceiling[4] = True

# Object groups for easier mass-handling of all objects
floorObjects = []
wallObjects = []
columnObjects = []
ceilingObjects = []

#---------------------------------------------------------------------------------------------
# FLOOR: populating floor layer
# setting active scene layer

activeScene = 'level01'

bpy.data.scenes[activeScene].layers = floor
for i in range( 0, mapWidth ):
   for j in range( 0, mapHeight ):
        if (floorLayer[i][j] != "None"):            
            bpy.data.objects[floorLayer[i][j]].select = True
            bpy.ops.object.duplicate()
            bpy.context.selected_objects[0].location = (j*floorTileSize, -i*floorTileSize, 0)
            floorObjects.append(bpy.context.selected_objects[0])
            # adding abject to a group
            #bpy.ops.object.group_link( group = "floorGroup" )
            bpy.ops.object.select_all(action='DESELECT')

# END FLOOR --------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------
#WALL: populating wall layer
# setting active scene layer
displ = floorTileSize/2

bpy.data.scenes[activeScene].layers = wall
for wallLayer in [wallLayerN, wallLayerS, wallLayerE, wallLayerW]:#, wallBoxLayer, wallChainLayer, wallTorchLayer]:
    for i in range( 0, mapWidth ):
        for j in range( 0, mapHeight ):
            if (wallLayer[i][j] != "None"):
                bpy.data.objects[wallLayer[i][j]].select = True
                bpy.ops.object.duplicate()
                # calculating additional displacements for wall tiles
                displX, displY, displZ = [0, 0, 0]
                # checking the last two digits in the prefab name for the 
                # correct displacement of North, West, South, and East wall tiles
                if (wallLayer == wallLayerN):
                    displY = -displ
                if (wallLayer == wallLayerW):
                    displX = displ
                    bpy.context.selected_objects[0].rotation_euler = (0.0, 0.0, Pi/2)
                if (wallLayer == wallLayerS):
                    displY = displ
                    bpy.context.selected_objects[0].rotation_euler = (0.0, 0.0, Pi)
                if (wallLayer == wallLayerE):
                    displX = -displ
                    bpy.context.selected_objects[0].rotation_euler = (0.0, 0.0, -Pi/2)
                bpy.context.selected_objects[0].location = (j*floorTileSize+displX, -i*floorTileSize+displY, displZ)
                # walls will be occluding in game
#                bpy.context.selected_objects[0].game.physics_type = "OCCLUDE"
                wallObjects.append(bpy.context.selected_objects[0])
                bpy.ops.object.select_all(action='DESELECT')

# END FLOOR --------------------------------------------------------------------------------------------------



# COLUMN populating column layer
# setting active scene layer
bpy.data.scenes[activeScene].layers = column
for i in range( 0, mapWidth ):
   for j in range( 0, mapHeight ):
        if (columnLayer[i][j] != "None"):            
            bpy.data.objects[columnLayer[i][j]].select = True
            bpy.ops.object.duplicate()
            displX, displY, displZ = [floorTileSize/2.0, -floorTileSize/2.0, 0]            
            bpy.context.selected_objects[0].location = (j*floorTileSize+displX, -i*floorTileSize+displY, displZ)
            columnObjects.append(bpy.context.selected_objects[0])
#            bpy.context.selected_objects[0].game.physics_type = "OCCLUDE"
            bpy.ops.object.select_all(action='DESELECT')

# END COLUMN --------------------------------------------------------------------------------------------            
            
##---------------------------------------------------------------------------------------------------            
## CEILING BARs populating ceiling bars layer
## setting active scene layer
#bpy.data.scenes['Scene'].layers = ceilingBar
#for i in range( 0, mapWidth ):
#   for j in range( 0, mapHeight ):
#        if (ceilingBarLayer[i][j] != "None"):            
#            bpy.data.objects[ceilingBarLayer[i][j]].select = True
#            bpy.ops.object.duplicate()
#            displX, displY, displZ = [0, 0, 0]
#            if (ceilingBarLayer[i][j] == "ceilingBar01"):
#                displX = -floorTileSize/2.0
#            if (ceilingBarLayer[i][j] == "ceilingBar02"):
#                displY = floorTileSize/2.0            
#            bpy.context.selected_objects[0].location = (j*floorTileSize+displX, -i*floorTileSize+displY, displZ)
#            ceilingBarObjects.append(bpy.context.selected_objects[0])
#            bpy.ops.object.select_all(action='DESELECT')
#
## END CEILING BARS -----------------------------------------------------------------------------------
            

#----------------------------------------------------------------------------------------------------
# CEILING populating ceiling layer
# setting active scene layer
ceilingHeight = 3.0
bpy.data.scenes[activeScene].layers = ceiling
for i in range( 0, mapWidth ):
   for j in range( 0, mapHeight ):
        if (ceilingLayer[i][j] != "None"):            
            bpy.data.objects[ceilingLayer[i][j]].select = True
            bpy.ops.object.duplicate()
            bpy.context.selected_objects[0].location = (j*floorTileSize, -i*floorTileSize, ceilingHeight)
            ceilingObjects.append(bpy.context.selected_objects[0])
            bpy.ops.object.select_all(action='DESELECT')
# END CEILING ---------------------------------------------------------------------------------------


# selecting all the layers with the dungeon
layers = [False]*20
layers[1:5] = [True, True, True, True]
bpy.data.scenes[activeScene].layers = layers
