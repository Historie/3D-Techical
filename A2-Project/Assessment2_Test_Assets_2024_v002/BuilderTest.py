import maya.cmds as cmds
import os

def get_project_root():
    return cmds.workspace(query=True, rootDirectory=True)

def get_shot_list():
    project_root = get_project_root()
    shots_dir = os.path.join(project_root, 'publish', 'sequence')
    shots = []
    if os.path.exists(shots_dir):
        shots = [d for d in os.listdir(shots_dir) if os.path.isdir(os.path.join(shots_dir, d))]
    return shots

def get_assets_for_shot(shot, asset_types):
    project_root = get_project_root()
    assets = []
    for asset_type in asset_types:
        asset_dir = os.path.join(project_root, 'publish', 'assets', asset_type)
        if os.path.exists(asset_dir):
            asset_names = [d for d in os.listdir(asset_dir) if os.path.isdir(os.path.join(asset_dir, d))]
            assets.extend([f"{asset_type}/{name}" for name in asset_names])
    return assets

def update_asset_list(*args):
    selected_shot = cmds.optionMenu('shotMenu', query=True, value=True)
    asset_types = []
    if cmds.checkBox('checkSet', query=True, value=True):
        asset_types.append('set')
    if cmds.checkBox('checkLayout', query=True, value=True):
        asset_types.append('layout')
    if cmds.checkBox('checkCharacter', query=True, value=True):
        asset_types.append('character')
    if cmds.checkBox('checkProp', query=True, value=True):
        asset_types.append('prop')
    
    assets = get_assets_for_shot(selected_shot, asset_types)
    cmds.textScrollList('assetList', edit=True, removeAll=True)
    cmds.textScrollList('assetList', edit=True, append=assets)

def clear_option_menu(menu_name):
    option_menu = cmds.optionMenuGrp(menu_name, query=True, childArray=True)[0]
    menu_items = cmds.optionMenu(option_menu, query=True, itemListLong=True)
    if menu_items:
        for item in menu_items:
            cmds.deleteUI(item)

def on_asset_selected():
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    if selected_assets:
        asset = selected_assets[0]
        asset_type, asset_name = asset.split('/')
        versions = get_versions(asset_type, asset_name)
        clear_option_menu('versionMenu')
        option_menu = cmds.optionMenuGrp('versionMenu', query=True, childArray=True)[0]
        if versions:
            for version in versions:
                cmds.menuItem(label=version, parent=option_menu)
        else:
            # 添加一个默认选项，表示没有版本
            cmds.menuItem(label='Default Version', parent=option_menu)
    else:
        clear_option_menu('versionMenu')

def get_versions(asset_type, asset_name):
    project_root = get_project_root()
    asset_path = os.path.join(project_root, 'publish', 'assets', asset_type, asset_name)
    versions = []
    if os.path.exists(asset_path):
        versions = [f for f in os.listdir(asset_path) if f.endswith(('.ma', '.mb', '.abc', '.fbx'))]
    if not versions:
        # 如果没有找到版本，尝试使用默认的资产文件
        default_file = asset_name + '.ma'  # 或者 .mb，取决于您的文件格式
        default_path = os.path.join(asset_path, default_file)
        if os.path.exists(default_path):
            versions.append(default_file)
    versions.sort(reverse=True)
    return versions

def get_asset_file_path(asset_type, asset_name, version):
    project_root = get_project_root()
    return os.path.join(project_root, 'publish', 'assets', asset_type, asset_name, version)

def load_selected_assets(*args):
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    selected_version = cmds.optionMenuGrp('versionMenu', query=True, value=True)
    if selected_assets:
        for asset in selected_assets:
            asset_type, asset_name = asset.split('/')
            if selected_version == 'Default Version':
                # 使用默认的资产文件名
                version = asset_name + '.ma'  # 或者 .mb，取决于您的文件格式
            else:
                version = selected_version
            file_path = get_asset_file_path(asset_type, asset_name, version)
            if file_path and os.path.exists(file_path):
                cmds.file(file_path, reference=True)
                cmds.scrollField('infoField', edit=True, insertText=f"Loaded {asset} version {version}\n")
            else:
                cmds.warning(f"File not found: {file_path}")
    else:
        cmds.warning("No assets selected.")

def check_for_updates(*args):
    # 实现更新检查功能
    pass

def create_builder_tool_ui():
    if cmds.window("builderToolWindow", exists=True):
        cmds.deleteUI("builderToolWindow")
    
    window = cmds.window("builderToolWindow", title="Builder Tool", widthHeight=(400, 600))
    cmds.columnLayout(adjustableColumn=True)
    
    # 镜头选择
    cmds.frameLayout(label="Select Shot")
    cmds.optionMenu('shotMenu', changeCommand=update_asset_list)
    shots = get_shot_list()
    if not shots:
        cmds.menuItem(label="No Shots Found")
    else:
        for shot in shots:
            cmds.menuItem(label=shot)
    cmds.setParent('..')
    
    # 资产类型选择
    cmds.frameLayout(label="Select Asset Types to Load")
    cmds.checkBox('checkSet', label="Set", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkLayout', label="Layout (Camera)", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkCharacter', label="Character Animation Cache", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkProp', label="Prop Cache", value=False, changeCommand=update_asset_list)
    cmds.setParent('..')
    
    # 资产列表
    cmds.frameLayout(label="Available Assets")
    cmds.textScrollList('assetList', numberOfRows=8, allowMultiSelection=True, height=150, selectCommand=on_asset_selected)
    cmds.setParent('..')
    
    # 版本选择
    cmds.frameLayout(label="Select Version")
    cmds.optionMenuGrp('versionMenu', label="Version")
    cmds.setParent('..')
    
    # 加载按钮
    cmds.button(label="Load Selected Assets", command=load_selected_assets)
    
    # 信息显示区域
    cmds.scrollField('infoField', editable=False, wordWrap=True, height=100)
    
    cmds.showWindow(window)
    
    # 初始化资产列表
    update_asset_list()

# 运行工具
create_builder_tool_ui()
