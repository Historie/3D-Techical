import maya.cmds as cmds
import os

# Base directory
WIP_DIR = "/Users/edbertyoung/Documents/maya/projects/Assessment2/wip"

def determine_save_path(department, asset_type, asset_name):
    """
    Determine the correct save path based on the department and asset type.
    """
    base_path = os.path.join(WIP_DIR, "assets", asset_type, asset_name)
    
    department_path_map = {
        "model": os.path.join(base_path, "model/source/"),
        "rig": os.path.join(base_path, "rig/source/"),
        "anim": os.path.join(base_path, "anim/source/")
    }
    
    save_path = department_path_map.get(department, base_path)
    
    # Ensure the directory exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    return save_path

def get_next_version(file_path, file_name):
    """
    Get the next available version number for the file.
    """
    version = 1
    while os.path.exists(f"{file_path}/{file_name}_v{str(version).zfill(3)}.ma"):
        version += 1
    return str(version).zfill(3)

def save_file(department, asset_type, asset_name, file_name):
    """
    Save the file with automatic versioning.
    """
    save_path = determine_save_path(department, asset_type, asset_name)
    version = get_next_version(save_path, file_name)
    full_file_name = f"{file_name}_v{version}.ma"
    full_file_path = os.path.join(save_path, full_file_name)
    
    cmds.file(rename=full_file_path)
    cmds.file(save=True, type="mayaAscii")
    
    cmds.inform("File saved successfully: " + full_file_name)
    return full_file_name

# UI for Save Tool
def create_save_tool_ui():
    if cmds.window("saveToolWindow", exists=True):
        cmds.deleteUI("saveToolWindow")

    window = cmds.window("saveToolWindow", title="Save Tool", widthHeight=(400, 200))

    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Save Tool (Week 8)")

    # Asset Info
    cmds.textFieldGrp('assetName', label='Asset Name')
    cmds.textFieldGrp('fileName', label='File Name')

    # Department Selector
    cmds.optionMenuGrp('departmentMenu', label='Department')
    cmds.menuItem(label='model')
    cmds.menuItem(label='rig')
    cmds.menuItem(label='anim')

    # Asset Type Selector
    cmds.optionMenuGrp('assetTypeMenu', label='Asset Type')
    cmds.menuItem(label='prop')
    cmds.menuItem(label='character')
    cmds.menuItem(label='environment')

    cmds.button(label="Save", command=lambda *args: save_file(
        cmds.optionMenuGrp('departmentMenu', query=True, value=True),
        cmds.optionMenuGrp('assetTypeMenu', query=True, value=True),
        cmds.textFieldGrp('assetName', query=True, text=True),
        cmds.textFieldGrp('fileName', query=True, text=True)
    ))

    cmds.showWindow(window)

# Run the UI
create_save_tool_ui()
