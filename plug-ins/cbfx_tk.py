import sys
import os
import pymel.core as pm
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

#setup main window and vars
main_window = pm.language.melGlobals['gMainWindow']
menu_obj = 'cbfx_toolkit'
menu_label = 'CBFX'


# Command
CmdName_StudioLib = "cbfx_studiolib"
class Studiolib(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self, argList):
        if not os.path.exists(r'\\cbone-file-07\pipeline\etc\maya\scripts\studiolibrary-2.7.1\src'):
            raise IOError(r'The source path "\\cbone-file-07\pipeline\etc\maya\scripts\studiolibrary-2.7.1\src" does not exist!')

        if r'\\cbone-file-07\pipeline\etc\maya\scripts\studiolibrary-2.7.1\src' not in sys.path:
            sys.path.insert(0, r'\\cbone-file-07\pipeline\etc\maya\scripts\studiolibrary-2.7.1\src')

        libraries = [   {"name":"Default", "path":r"P:\qg1\assets\chess-board\anim\work\data\studiolibraries\Default", "default":True},
                        {"name":"Scratch", "path":r"P:\qg1\assets\chess-board\anim\work\data\studiolibraries\Scratch"}
                    ]
        import studiolibrary
        studiolibrary.setLibraries(libraries)
        studiolibrary.main()

# Creator
def cmdCreator_StudioLib():
    return OpenMayaMPx.asMPxPtr( Studiolib() )

################################################################################

# Command
CmdName_CreateRest = "cbfx_createrest"
class CreateRest(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self, argList):
        from cbfxmayalibs import create_rest_position
        create_rest_position.execute()


# Creator
def cmdCreator_CreateRest():
    return OpenMayaMPx.asMPxPtr( CreateRest() )

################################################################################

# Command
CmdName_ExportAlembic = "cbfx_exportalembic"
class ExportAlembic(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self, argList):
        print "dude2"

# Creator
def cmdCreator_ExportAlembic():
    return OpenMayaMPx.asMPxPtr( ExportAlembic() )

################################################################################

# Command
CmdName_Help = "cbfx_help"
class Help(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    # Invoked when the command is run.
    def doIt(self, argList):
        tmp = argList.asString(0)
        url = ''
        import webbrowser
        if tmp == 'shotgun':
            url = "https://cbfx.shotgunstudio.com/"
        if tmp == 'wiki':
            url = "http://wiki"

        if url != '':
            webbrowser.open(url=url, new=1)

# Creator
def cmdCreator_Help():
    return OpenMayaMPx.asMPxPtr( Help() )

################################################################################
def removeMenu(menu_obj):
    #check if the menu exists and if so remove it
    if pm.menu(menu_obj, label=menu_label, exists=True, parent=main_window):
        pm.deleteUI(pm.menu(menu_obj, e=True, deleteAllItems=True))

def createMenu(main_window, menu_obj, menu_label):
    #check to see if the menu exsists already
    removeMenu(menu_obj)

    #Create the top menu item
    cbfx_main_menu = pm.menu(menu_obj, label=menu_label, parent=main_window, tearOff=True)

    #Create Help submenu
    pm.menuItem(label="Help", subMenu=True, parent=cbfx_main_menu, tearOff=False)
    pm.menuItem(label="Shotgun", command="cmds.cbfx_help('shotgun')")
    pm.menuItem(label="Wiki", command="cmds.cbfx_help('wiki')")
    pm.setParent("..", menu=True)

    #seperator
    pm.menuItem(divider=True)

    #Create animation Sub Menu
    pm.menuItem(label="Animation", subMenu=True, parent=cbfx_main_menu, tearOff=False)
    pm.menuItem(label="Studio Library", command="cmds.cbfx_studiolib()")
    pm.menuItem(label="ZShotMask", command="from zshotmask_ui import ZShotMask, ZShotMaskUi; ZShotMaskUi.display()")
    pm.menuItem(label="Import Vehicle AutoRig", command="cmds.file('P:/qg1/pipeline/maya/toolsets/vehicle_autorig/vehicle_autorig_v002.ma', i=True )")
    pm.setParent("..", menu=True)

    # Create Modeling Sub Menu
    pm.menuItem(label="Modeling", subMenu=True, parent=cbfx_main_menu, tearOff=False)
    pm.menuItem(label="Generate Rest Position", command="cmds.cbfx_createrest()")
    pm.setParent("..", menu=True)

    # Create Modeling Sub Menu
    pm.menuItem(label="Export", subMenu=True, parent=cbfx_main_menu, tearOff=False)
    pm.menuItem(label="Export Alembic", command="cmds.cbfx_exportalembic()")
    pm.setParent("..", menu=True)

################################################################################

# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    createMenu(main_window, menu_obj, menu_label)
    try:
        mplugin.registerCommand( CmdName_StudioLib, cmdCreator_StudioLib )
        mplugin.registerCommand( CmdName_CreateRest, cmdCreator_CreateRest )
        mplugin.registerCommand( CmdName_ExportAlembic, cmdCreator_ExportAlembic )
        mplugin.registerCommand( CmdName_Help, cmdCreator_Help )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( CmdName_StudioLib )
        mplugin.deregisterCommand( CmdName_CreateRest )
        mplugin.deregisterCommand( CmdName_ExportAlembic )
        mplugin.deregisterCommand( CmdName_Help )
        removeMenu(menu_obj)
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
