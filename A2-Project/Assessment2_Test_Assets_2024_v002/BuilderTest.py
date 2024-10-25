import maya.cmds as cmds
import os
import re

# 创建工具的用户界面
def create_builder_tool_ui():
    if cmds.window("builderToolWindow", exists=True):
        cmds.deleteUI("builderToolWindow")
    
    window = cmds.window("builderToolWindow", title="Builder Tool", widthHeight=(400, 600))
    cmds.columnLayout(adjustableColumn=True)
    
    sequence_name, shot_name = get_current_shot()
    if not shot_name:
        cmds.error("Cannot determine the current shot. Please open a shot scene first.")
        return
    cmds.text(label=f"Current Shot: {sequence_name}/{shot_name}", align='left')
    
    cmds.frameLayout(label="Select Asset Types to Load")
    cmds.checkBox('checkSet', label="Set", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkLayout', label="Layout (Camera)", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkCharacter', label="Character Animation Cache", value=True, changeCommand=update_asset_list)
    cmds.checkBox('checkProp', label="Prop Cache", value=False, changeCommand=update_asset_list)
    cmds.setParent('..')
    
    cmds.frameLayout(label="Available Assets")
    cmds.textScrollList('assetList', numberOfRows=8, allowMultiSelection=True, height=150, selectCommand=on_asset_selected)
    cmds.setParent('..')
    
    cmds.frameLayout(label="Select Version")
    cmds.optionMenu('versionMenu')
    cmds.menuItem(label='Please select an asset')
    cmds.setParent('..')
    
    cmds.button(label="Load Selected Assets", command=load_selected_assets)
    cmds.showWindow(window)
    update_asset_list()

# 全局变量，用于存储版本文件名与相对路径的映射
version_map = {}

# 获取当前项目的根目录
def get_project_root():
    project_root = os.path.normpath(cmds.workspace(query=True, rootDirectory=True))
    print(f"Project root directory: {project_root}")
    return project_root

# 获取当前镜头
def get_current_shot():
    # 获取当前打开的场景文件的完整路径
    current_file = cmds.file(query=True, sceneName=True)
    if not current_file:
        cmds.warning("No scene file is currently open.")
        return None, None
    current_file = os.path.normpath(current_file)

    # 获取项目的根目录
    project_root = get_project_root()
    relative_path = os.path.relpath(current_file, project_root)
    path_parts = relative_path.split(os.sep)
    print(f"Current file relative path: {relative_path}")

    # 查找路径中是否包含 sequence 目录
    if "sequence" in path_parts:
        # 获取 sequence 的索引
        seq_index = path_parts.index("sequence")
        # 确保 "sequence" 目录后面至少还有序列名和镜头名
        if len(path_parts) > seq_index + 2:
            # 获取序列名称和镜头名称
            sequence_name = path_parts[seq_index + 1]
            shot_name = path_parts[seq_index + 2]
            print(f"Detected sequence: {sequence_name}, shot: {shot_name}")
            # 返回序列名称和镜头名称
            return sequence_name, shot_name
    # 如果未能获取发出警告
    cmds.warning("Unable to determine the current shot from the scene path.")
    return None, None

# 获取可用的资产列表，基于选定的资产类型
def get_assets(asset_types):
    project_root = get_project_root()
    assets = []
    sequence_name, shot_name = get_current_shot()
    if not shot_name:
        cmds.error("Cannot determine the current shot. Please open a shot scene first.")
        return assets

    for asset_type in asset_types:
        if asset_type == 'layout':
            # Layout 资产 从镜头的 layout caches 目录加载
            asset_dir = os.path.join(project_root, 'publish', 'sequence', sequence_name, shot_name, 'layout', 'caches', 'alembic')
            print(f"Layout asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                asset_files = [f for f in os.listdir(asset_dir)
                               if os.path.isfile(os.path.join(asset_dir, f))]
                print(f"Found layout asset files: {asset_files}")
                assets.extend([f"{asset_type}/{f}" for f in asset_files])
            else:
                print(f"Layout asset directory does not exist: {asset_dir}")
        elif asset_type == 'character':
            # Character Animation Cache，从镜头的 animation caches alembic 目录加载
            asset_dir = os.path.join(project_root, 'publish', 'sequence', sequence_name, shot_name, 'animation', 'caches', 'alembic')
            print(f"Character asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                asset_files = [f for f in os.listdir(asset_dir)
                               if os.path.isfile(os.path.join(asset_dir, f))]
                print(f"Found character asset files: {asset_files}")
                assets.extend([f"{asset_type}/{f}" for f in asset_files])
            else:
                print(f"Character asset directory does not exist: {asset_dir}")
        else:
            # 处理其他资产类型
            asset_dir = os.path.join(project_root, 'publish', 'assets', asset_type)
            print(f"{asset_type.capitalize()} asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                asset_names = [d for d in os.listdir(asset_dir)
                               if os.path.isdir(os.path.join(asset_dir, d))]
                print(f"Found {asset_type} assets: {asset_names}")
                assets.extend([f"{asset_type}/{name}" for name in asset_names])
            else:
                print(f"{asset_type.capitalize()} asset directory does not exist: {asset_dir}")
    return assets

# 更新资产列表，当资产类型选择发生变化时调用
def update_asset_list(*args):
    asset_types = []
    if cmds.checkBox('checkSet', query=True, value=True):
        asset_types.append('set')
    if cmds.checkBox('checkLayout', query=True, value=True):
        asset_types.append('layout')
    if cmds.checkBox('checkCharacter', query=True, value=True):
        asset_types.append('character')
    if cmds.checkBox('checkProp', query=True, value=True):
        asset_types.append('prop')
    
    assets = get_assets(asset_types)
    cmds.textScrollList('assetList', edit=True, removeAll=True)
    cmds.textScrollList('assetList', edit=True, append=assets)

# 提取文件名中的版本号，用于排序
def extract_version_number(filename):
    match = re.search(r'[._]v(\d+)', filename)
    if match:
        version_number = int(match.group(1))
        print(f"Extracted version number {version_number} from {filename}")
        return version_number
    else:
        print(f"No version number found in {filename}")
        return 0

# 获取指定资产的所有可用版本
def get_versions(asset_type, asset_name):
    global version_map
    project_root = get_project_root()
    versions = []
    version_map = {}
    sequence_name, shot_name = get_current_shot()
    if not shot_name:
        cmds.error("Cannot determine the current shot.")
        return versions

    if asset_type == 'layout':
        # 资产的路径
        asset_path = os.path.join(
            project_root, 'publish', 'sequence', sequence_name, shot_name,
            'layout', 'caches', 'alembic', asset_name)
        print(f"Layout asset path: {asset_path}")
        if os.path.exists(asset_path):
            # 提取版本号 更新列表
            version_number = extract_version_number(asset_name)
            version_map[asset_name] = asset_name
            versions.append(asset_name)
        else:
            print(f"Asset file does not exist: {asset_path}")
    elif asset_type == 'character':
        # 角色资产的路径
        asset_path = os.path.join(
            project_root, 'publish', 'sequence', sequence_name, shot_name,
            'animation', 'caches', 'alembic', asset_name)
        print(f"Character asset path: {asset_path}")
        if os.path.exists(asset_path):            
            version_number = extract_version_number(asset_name)
            version_map[asset_name] = asset_name
            versions.append(asset_name)
        else:
            print(f"Asset file does not exist: {asset_path}")
    else:
        # 构建其他资产类型的路径
        asset_dir = os.path.join(
            project_root, 'publish', 'assets', asset_type, asset_name)
        print(f"Looking for versions in: {asset_dir}")

        version_info = []

        if os.path.exists(asset_dir):
            # 遍历资产目录，查找符合条件的文件
            for root, dirs, files in os.walk(asset_dir):
                for f in files:
                    if f == '.DS_Store':
                        continue
                    if f.endswith(('.ma', '.mb', '.abc', '.fbx')):
                        # 计算文件的相对路径
                        relative_dir = os.path.relpath(root, asset_dir)
                        version_path = os.path.join(relative_dir, f)
                        # 提取版本号
                        version_number = extract_version_number(f)
                        # 将版本信息添加到列表
                        version_info.append((version_number, f))
                        version_map[f] = version_path
                        print(f"Found file: {version_path}")
        else:
            print(f"Asset directory does not exist: {asset_dir}")

        # 按版本号从高到低排序
        version_info.sort(key=lambda x: x[0], reverse=True)
        # 提取排序后的文件名列表
        versions.extend([v[1] for v in version_info])
    return versions


# 当选择资产时，更新版本列表
def on_asset_selected(*args):
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    if selected_assets:
        asset = selected_assets[0]
        asset_type, asset_name = asset.split('/', 1)
        versions = get_versions(asset_type, asset_name)
        cmds.optionMenu('versionMenu', edit=True, deleteAllItems=True)
        if versions:
            for version in versions:
                cmds.menuItem(label=version, parent='versionMenu')
        else:
            cmds.menuItem(label='No Versions Found', parent='versionMenu')
    else:
        cmds.optionMenu('versionMenu', edit=True, deleteAllItems=True)

# 加载选定的资产和版本到当前场景中
def load_selected_assets(*args):
    global version_map
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    selected_version = cmds.optionMenu('versionMenu', query=True, value=True)
    if selected_assets and selected_version != 'No Versions Found':
        sequence_name, shot_name = get_current_shot()
        if not shot_name:
            cmds.error("Cannot determine the current shot.")
            return
        for asset in selected_assets:
            asset_type, asset_name = asset.split('/', 1)
            relative_path = version_map.get(selected_version)
            if not relative_path:
                cmds.warning(f"Version path not found for: {selected_version}")
                continue
            if asset_type == 'layout':
                file_path = os.path.join(get_project_root(), 'publish', 'sequence', sequence_name, shot_name, 'layout', 'caches', 'alembic', relative_path)
            elif asset_type == 'character':
                file_path = os.path.join(get_project_root(), 'publish', 'sequence', sequence_name, shot_name, 'animation', 'caches', 'alembic', relative_path)
            else:
                file_path = os.path.join(get_project_root(), 'publish', 'assets',
                                         asset_type, asset_name, relative_path)
            full_file_path = os.path.normpath(file_path)
            print(f"Loading asset from: {full_file_path}")
            if os.path.exists(full_file_path):
                try:
                    cmds.file(full_file_path, reference=True)
                    # 移除日志输出代码
                    # cmds.scrollField('infoField', edit=True,
                    #                  insertText=f"Loaded {asset} version {selected_version}\n")
                except Exception as e:
                    cmds.warning(f"Failed to load asset: {e}")
            else:
                cmds.warning(f"File not found: {full_file_path}")
    else:
        cmds.warning("No assets selected or invalid version.")

# 运行工具，创建用户界面
create_builder_tool_ui()
