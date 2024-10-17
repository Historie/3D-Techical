import maya.cmds as cmds
import os

def get_project_root():
    return os.path.normpath(cmds.workspace(q=True, rootDirectory=True))

def get_all_asset_files():
    project_root = get_project_root()
    asset_files = []

    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(('.ma', '.mb')):
                file_path = os.path.join(root, file)
                asset_files.append(file_path)
    return asset_files

def create_open_file_tool_ui():
    if cmds.window("openFileToolWindow", exists=True):
        cmds.deleteUI("openFileToolWindow")

    window = cmds.window("openFileToolWindow", title="Open File Tool", widthHeight=(400, 600))
    main_layout = cmds.columnLayout(adjustableColumn=True)



    # 选择 Asset 或 Shot
    cmds.text(label="Select Asset or Shot:")
    cmds.optionMenu('assetShotMenu')
    cmds.menuItem(label='Asset')
    cmds.menuItem(label='Shot')

    # Asset 选项布局
    cmds.frameLayout('assetFrame', label="Asset Options", collapsable=False)
    cmds.columnLayout()
    cmds.text(label="Select Asset Type:")
    cmds.optionMenu('assetTypeMenu')
    cmds.text(label="Select Asset Name:")
    cmds.optionMenu('assetNameMenu')
    cmds.setParent('..')
    cmds.setParent('..')

    # Shot 选项布局
    cmds.frameLayout('shotFrame', label="Shot Options", collapsable=False)
    cmds.columnLayout()
    cmds.text(label="Select Sequence:")
    cmds.optionMenu('sequenceMenu')
    cmds.text(label="Select Shot:")
    cmds.optionMenu('shotMenu')
    cmds.setParent('..')
    cmds.setParent('..')

    # 部门选择
    cmds.text(label="Select Department:")
    cmds.optionMenu('departmentMenu')
    departments = ['model', 'rig', 'animation', 'layout', 'light']
    for dept in departments:
        cmds.menuItem(label=dept)

    # 文件类型选择
    cmds.text(label="Select File Type:")
    cmds.optionMenu('wipPublishMenu')
    cmds.menuItem(label='wip')
    cmds.menuItem(label='publish')

    # 版本列表，显示所有资产文件
    cmds.text(label="All Asset Files:")
    cmds.textScrollList('versionList', numberOfRows=20, allowMultiSelection=False, height=400)

    # 刷新按钮
    cmds.button(label='Refresh', command=refresh_version_list)

    # 打开按钮
    cmds.button(label='Open Selected File', command=open_selected_file)

    cmds.showWindow(window)

    # 初始化版本列表
    refresh_version_list()

def refresh_version_list(*args):
    cmds.textScrollList('versionList', edit=True, removeAll=True)
    asset_files = get_all_asset_files()
    for file_path in asset_files:
        cmds.textScrollList('versionList', edit=True, append=file_path)

def open_selected_file(*args):
    selected_files = cmds.textScrollList('versionList', query=True, selectItem=True)
    if selected_files:
        file_path = selected_files[0]
        if os.path.exists(file_path):
            if cmds.file(q=True, modified=True):
                result = cmds.confirmDialog(
                    title='Unsaved Changes',
                    message='Current scene has unsaved changes. Do you want to save?',
                    button=['Yes', 'No', 'Cancel'],
                    defaultButton='Yes',
                    cancelButton='Cancel',
                    dismissString='Cancel'
                )
                if result == 'Cancel':
                    return
                elif result == 'Yes':
                    cmds.file(save=True)
            cmds.file(file_path, open=True, force=True)
            print("Opened file:", file_path)
        else:
            cmds.warning("File does not exist!")
    else:
        cmds.warning("Please select a file first!")

# 运行工具
create_open_file_tool_ui()
