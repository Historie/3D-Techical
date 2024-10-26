import maya.cmds as cmds
import os
import re

# Base directories for WIP and Publish
def get_project_root():
    return os.path.normpath(cmds.workspace(q=True, rootDirectory=True))

WIP_DIR = os.path.join(get_project_root(), "wip")
PUBLISH_DIR = os.path.join(get_project_root(), "publish")

# Helper function: Ensure directory exists
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Get save path based on department and asset type
def determine_save_path(department, asset_type, asset_name, is_publish=False):
    base_path = PUBLISH_DIR if is_publish else WIP_DIR
    if department in ["model", "rig", "anim"]:
        save_path = os.path.join(base_path, "assets", asset_type, asset_name, department, "source")
    else:
        save_path = os.path.join(base_path, "sequence", asset_name, department, "source")
    
    ensure_directory_exists(save_path)
    return save_path

# Get next version number for a file
def get_next_version(file_path, file_name):
    version = 1
    while os.path.exists(f"{file_path}/{file_name}_v{str(version).zfill(3)}.ma"):
        version += 1
    return str(version).zfill(3)

# Save file with versioning and user prompt in WIP directory
def save_file(department, asset_type, asset_name, file_name):
    if not all([department, asset_type, asset_name, file_name]):
        cmds.warning("Please fill in all required fields.")
        return
    
    save_path = determine_save_path(department, asset_type, asset_name)
    version = get_next_version(save_path, file_name)
    full_file_name = f"{file_name}_v{version}.ma"
    full_file_path = os.path.join(save_path, full_file_name)
    
    cmds.file(rename=full_file_path)
    cmds.file(save=True, type="mayaAscii")
    
    cmds.confirmDialog(title="Save Successful", message=f"File saved as {full_file_name} in WIP", button=["OK"])
    return full_file_name, version

# Publish file to the publish folder and export formats, with confirmation dialog
def publish_file(department, asset_type, asset_name, file_name, frame_range="1 24"):
    full_file_name, version = save_file(department, asset_type, asset_name, file_name)
    
    # Define publish paths for source and caches
    publish_source_path = determine_save_path(department, asset_type, asset_name, is_publish=True)
    publish_cache_path_abc = os.path.join(PUBLISH_DIR, "caches/abc")
    publish_cache_path_fbx = os.path.join(PUBLISH_DIR, "caches/fbx")
    ensure_directory_exists(publish_cache_path_abc)
    ensure_directory_exists(publish_cache_path_fbx)

    # Copy WIP file to Publish source
    wip_save_path = determine_save_path(department, asset_type, asset_name)
    saved_file = os.path.join(wip_save_path, full_file_name)
    published_file = os.path.join(publish_source_path, full_file_name)
    
    if os.path.exists(published_file):
        overwrite = cmds.confirmDialog(title="File Exists", message="Published file already exists. Overwrite?", button=["Yes", "No"])
        if overwrite == "No":
            return

    cmds.sysFile(saved_file, copy=published_file)

    # Export Alembic (.abc) and FBX (.fbx) files
    alembic_path = os.path.join(publish_cache_path_abc, f"{file_name}_v{version}.abc")
    fbx_path = os.path.join(publish_cache_path_fbx, f"{file_name}_v{version}.fbx")
    cmds.AbcExport(j=f"-file {alembic_path} -ftr -fr {frame_range}")
    cmds.file(fbx_path, force=True, options="v=0;", type="FBX export", exportAll=True)
    
    cmds.confirmDialog(title="Publish Successful", message=f"File published as {full_file_name}", button=["OK"])

# Documentation dialog
def show_documentation():
    cmds.confirmDialog(title="Save & Publish Tool - Documentation",
                       message="Usage:\n1. Enter Asset Name and File Name.\n2. Select Department and Asset Type.\n3. Click Save (WIP) or Publish (final).\n\nVersioning is automatic.",
                       button=["OK"])

# UI setup
def create_save_publish_tool_ui():
    if cmds.window("savePublishToolWindow", exists=True):
        cmds.deleteUI("savePublishToolWindow")

    window = cmds.window("savePublishToolWindow", title="Save & Publish Tool", widthHeight=(500, 350))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Save & Publish Tool", align="center", height=30)

    # Asset Information
    cmds.frameLayout(label="Asset Information", collapsable=True)
    cmds.textFieldGrp('assetName', label='Asset Name')
    cmds.textFieldGrp('fileName', label='File Name')

    # Department Selector
    cmds.optionMenuGrp('departmentMenu', label='Department')
    cmds.menuItem(label='model')
    cmds.menuItem(label='rig')
    cmds.menuItem(label='animation')
    cmds.menuItem(label='layout')
    
    # Asset Type Selector
    cmds.optionMenuGrp('assetTypeMenu', label='Asset Type')
    cmds.menuItem(label='setPiece')
    cmds.menuItem(label='set')
    cmds.menuItem(label='character')
    cmds.menuItem(label='prop')
    cmds.setParent('..')

    # Save and Publish Buttons with options to view versions
    cmds.frameLayout(label="Actions", collapsable=True)
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(110, 110, 110, 110), adjustableColumn=3)
    cmds.button(label="Save (WIP)", width=110, command=lambda *args: save_file(
        cmds.optionMenuGrp('departmentMenu', query=True, value=True),
        cmds.optionMenuGrp('assetTypeMenu', query=True, value=True),
        cmds.textFieldGrp('assetName', query=True, text=True),
        cmds.textFieldGrp('fileName', query=True, text=True)
    ))
    cmds.button(label="Publish (Final)", width=110, command=lambda *args: publish_file(
        cmds.optionMenuGrp('departmentMenu', query=True, value=True),
        cmds.optionMenuGrp('assetTypeMenu', query=True, value=True),
        cmds.textFieldGrp('assetName', query=True, text=True),
        cmds.textFieldGrp('fileName', query=True, text=True)
    ))
    cmds.button(label="List Versions", width=110, command=list_versions)
    cmds.button(label="Documentation", width=110, command=show_documentation)
    cmds.setParent('..')
    
    cmds.showWindow(window)

# List file versions for selected asset in WIP folder
def list_versions(*args):
    asset_type = cmds.optionMenuGrp('assetTypeMenu', query=True, value=True)
    asset_name = cmds.textFieldGrp('assetName', query=True, text=True)
    department = cmds.optionMenuGrp('departmentMenu', query=True, value=True)
    save_path = determine_save_path(department, asset_type, asset_name)
    
    versions = sorted([f for f in os.listdir(save_path) if re.match(rf"{asset_name}_v\d+.ma", f)], reverse=True)
    if versions:
        print(f"Versions for {asset_name} (WIP):")
        for v in versions:
            print(v)
    else:
        cmds.warning(f"No versions found for {asset_name} in {save_path}.")

# Run the Save & Publish Tool UI
create_save_publish_tool_ui()

