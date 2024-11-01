import maya.cmds as cmds
import os

    # ------------GUI---------------------↓
def clear_option_menu(menu_name):
    menu_items = cmds.optionMenu(menu_name, query=True, itemListLong=True)
    if menu_items:
        for item in menu_items:
            cmds.deleteUI(item)

def create_open_file_tool_ui():
    if cmds.window("openFileWindow", exists=True):
        cmds.deleteUI("openFileWindow")

    window = cmds.window("openFileWindow", title="Open File Tool", widthHeight=(400, 600))
    main_layout = cmds.columnLayout(adjustableColumn=True)

    global asset_types, assets_dict, sequences, shots_dict
    asset_types, assets_dict, sequences, shots_dict = scan_project()

    cmds.text(label="Select Asset or Shot:")
    cmds.optionMenu('assetShotMenu', changeCommand=update_asset_shot_selection)
    cmds.menuItem(label='Asset')
    cmds.menuItem(label='Shot')

    # Asset layout
    cmds.frameLayout('assetFrame', label="Asset Options", collapsable=False)
    cmds.columnLayout()
    cmds.text(label="Select Asset Type:")
    cmds.optionMenu('assetTypeMenu', changeCommand=update_asset_names)
    cmds.text(label="Select Asset Name:")
    cmds.optionMenu('assetNameMenu', changeCommand=update_versions)
    cmds.setParent('..')
    cmds.setParent('..')

    # Shot layout
    cmds.frameLayout('shotFrame', label="Shot Options", collapsable=False)
    cmds.columnLayout()
    cmds.text(label="Select Sequence:")
    cmds.optionMenu('sequenceMenu', changeCommand=update_shots)
    cmds.text(label="Select Shot:")
    cmds.optionMenu('shotMenu', changeCommand=update_versions)
    cmds.setParent('..')
    cmds.setParent('..')

    cmds.text(label="Select Department:")
    cmds.optionMenu('departmentMenu', changeCommand=update_versions)
    departments = ['model', 'rig', 'animation', 'layout', 'light']
    for dept in departments:
        cmds.menuItem(label=dept)

    cmds.text(label="Select File Type:")
    cmds.optionMenu('wipPublishMenu', changeCommand=update_versions)
    cmds.menuItem(label='wip')
    cmds.menuItem(label='publish')

    cmds.text(label="Select Version:")
    cmds.textScrollList('versionList', numberOfRows=8, allowMultiSelection=False, height=150)
    cmds.button(label='Open', command=open_selected_file)

    cmds.showWindow(window)

    update_asset_shot_selection()
    
    # ------------GUI---------------------↑
def get_project_root():
    # 标准化项目根目录路径
    return os.path.normpath(cmds.workspace(q=True, rootDirectory=True))

def scan_project():
    project_root = get_project_root()
    asset_types = set()
    assets_dict = {}  # {asset_type: set(asset_names)}
    sequences = set()
    shots_dict = {}   # {sequence_name: set(shot_names)}

    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith(('.ma', '.mb')):
                relative_path = os.path.relpath(root, project_root)
                path_parts = relative_path.split(os.sep)
                # print("Processing file:", file)
                # print("Path parts:", path_parts)
                if "assets" in path_parts:
                    assets_index = path_parts.index("assets")
                    if len(path_parts) > assets_index + 2:
                        asset_type = path_parts[assets_index + 1]
                        asset_name = path_parts[assets_index + 2]
                        asset_types.add(asset_type)
                        if asset_type not in assets_dict:
                            assets_dict[asset_type] = set()
                        assets_dict[asset_type].add(asset_name)
                elif "sequence" in path_parts or "sequences" in path_parts:
                    if "sequence" in path_parts:
                        seq_index = path_parts.index("sequence")
                    else:
                        seq_index = path_parts.index("sequences")
                    if len(path_parts) > seq_index + 2:
                        sequence_name = path_parts[seq_index + 1]
                        shot_name = path_parts[seq_index + 2]
                        sequences.add(sequence_name)
                        if sequence_name not in shots_dict:
                            shots_dict[sequence_name] = set()
                        shots_dict[sequence_name].add(shot_name)
                        
    # print("Asset Types:", asset_types)
    # print("Assets Dict:", assets_dict)
    # print("Sequences:", sequences)
    # print("Shots Dict:", shots_dict)
    return sorted(asset_types), assets_dict, sorted(sequences), shots_dict
    # ------------Get the Project folder---------------------↑
    # Update GUI
def update_asset_shot_selection(*args):
    selected = cmds.optionMenu('assetShotMenu', query=True, value=True)
    if selected == 'Asset':
        cmds.frameLayout('assetFrame', edit=True, visible=True)
        cmds.frameLayout('shotFrame', edit=True, visible=False)
        update_asset_types()
    else:
        cmds.frameLayout('assetFrame', edit=True, visible=False)
        cmds.frameLayout('shotFrame', edit=True, visible=True)
        update_sequences()

def update_asset_types(*args):
    clear_option_menu('assetTypeMenu')
    for asset_type in asset_types:
        cmds.menuItem(label=asset_type, parent='assetTypeMenu')
    update_asset_names()

def update_asset_names(*args):
    asset_type = cmds.optionMenu('assetTypeMenu', query=True, value=True)
    asset_names = assets_dict.get(asset_type, [])
    clear_option_menu('assetNameMenu')
    for name in asset_names:
        cmds.menuItem(label=name, parent='assetNameMenu')
    update_versions()

def update_sequences(*args):
    clear_option_menu('sequenceMenu')
    for seq in sequences:
        cmds.menuItem(label=seq, parent='sequenceMenu')
    update_shots()

def update_shots(*args):
    sequence_name = cmds.optionMenu('sequenceMenu', query=True, value=True)
    shot_names = shots_dict.get(sequence_name, [])
    clear_option_menu('shotMenu')
    for name in shot_names:
        cmds.menuItem(label=name, parent='shotMenu')
    update_versions()

def update_versions(*args):
    cmds.textScrollList('versionList', edit=True, removeAll=True)
    wip_publish = cmds.optionMenu('wipPublishMenu', query=True, value=True)
    department = cmds.optionMenu('departmentMenu', query=True, value=True)
    project_root = get_project_root()

    if cmds.optionMenu('assetShotMenu', query=True, value=True) == 'Asset':
        asset_type = cmds.optionMenu('assetTypeMenu', query=True, value=True)
        asset_name = cmds.optionMenu('assetNameMenu', query=True, value=True)
        # 搜索source目录
        search_path = os.path.join(project_root, wip_publish, 'assets', asset_type, asset_name, department, 'source')
    else:
        sequence_name = cmds.optionMenu('sequenceMenu', query=True, value=True)
        shot_name = cmds.optionMenu('shotMenu', query=True, value=True)
        search_path = os.path.join(project_root, wip_publish, 'sequence', sequence_name, shot_name, department, 'source')

    # 标准化搜索路径
    search_path = os.path.normpath(search_path)
    print("Search Path:", search_path)

    if os.path.exists(search_path):
        versions = []
        for file in os.listdir(search_path):
            if file.endswith(('.ma', '.mb')):
                versions.append(file)
        versions.sort()
        for version in versions:
            file_path = os.path.join(search_path, version)
            # 显示文件名
            cmds.textScrollList('versionList', edit=True, append=version)
    else:
        print("Search path does not exist.")
        
    # Open file
def open_selected_file(*args):
    # 从'versionList'文本滚动列表中获取用户选择的文件版本
    selected_files = cmds.textScrollList('versionList', query=True, selectItem=True)
    
    # 检查是否有选择的文件版本
    if selected_files:
        # 获取第一个选择的版本名称
        version = selected_files[0]
        wip_publish = cmds.optionMenu('wipPublishMenu', query=True, value=True)
        department = cmds.optionMenu('departmentMenu', query=True, value=True)
        
        # 用get_project_root获取项目根目录路径
        project_root = get_project_root()

        # 检查是否选择了资产
        if cmds.optionMenu('assetShotMenu', query=True, value=True) == 'Asset':
            asset_type = cmds.optionMenu('assetTypeMenu', query=True, value=True)
            asset_name = cmds.optionMenu('assetNameMenu', query=True, value=True)
            file_path = os.path.join(project_root, wip_publish, 'assets', asset_type, asset_name, department, 'source', version)
        else:
            sequence_name = cmds.optionMenu('sequenceMenu', query=True, value=True)
            shot_name = cmds.optionMenu('shotMenu', query=True, value=True)
            file_path = os.path.join(project_root, wip_publish, 'sequence', sequence_name, shot_name, department, 'source', version)
        
        # 标准化路径
        file_path = os.path.normpath(file_path)

        # 检查文件是否存在
        if os.path.exists(file_path):
            cmds.file(file_path, open=True, force=True)
            print("Opened file:", file_path)
        else:
            cmds.warning("File does not exist!")
    else:
        cmds.warning("Please select a version first!")

# 运行工具
create_open_file_tool_ui()
