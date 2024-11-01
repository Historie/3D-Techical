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
        cmds.error("open a shot scene first.")
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

# 全局变量  用于存储资产与其版本的映射
asset_versions_map = {}
# 全局变量  用于存储版本文件名与相对路径的映射
version_map = {}

# 获取当前项目的根目录
def get_project_root():
    project_root = os.path.normpath(cmds.workspace(query=True, rootDirectory=True))
    print(f"Project root directory: {project_root}")
    return project_root

# 获取当前镜头
def get_current_shot():
    current_file = cmds.file(query=True, sceneName=True)
    if not current_file:
        return None, None

    current_file = os.path.normpath(current_file)
    project_root = get_project_root()
    relative_path = os.path.relpath(current_file, project_root)
    # 将相对路径分割成各个路径部分
    path_parts = relative_path.split(os.sep)
    print(f"path of the current file: {relative_path}")

    if "sequence" in path_parts:
        seq_index = path_parts.index("sequence")
        # 在 sequence 后检测至少两个元素，获取序列和镜头名称
        if len(path_parts) > seq_index + 2:
            # 序列名称为 sequence 后的第一个路径部分
            sequence_name = path_parts[seq_index + 1]
            # 镜头名称为 sequence 后的路径
            shot_name = path_parts[seq_index + 2]
            print(f"Detected sequence: {sequence_name}, shot: {shot_name}")
            return sequence_name, shot_name

    return None, None


# 提取资产的基础名称和版本号
def extract_base_name_and_version(filename):
    match = re.match(r'(.+?)[._]v(\d+)', filename)
    if match:
        base_name = match.group(1)
        version_number = int(match.group(2))
        print(f"Extracted base name: {base_name}, version number: {version_number} from {filename}")
        return base_name, version_number
    else:
        print(f"No version number found in {filename}")
        base_name = os.path.splitext(filename)[0]
        return base_name, 0

# 获取可用的资产列表
def get_assets(asset_types):
    global asset_versions_map
    project_root = get_project_root()
    assets = set()
    asset_versions_map = {}
    sequence_name, shot_name = get_current_shot()
    if not shot_name:
        cmds.error("Cannot determine the current shot. Please open a shot scene first.")
        return assets

    for asset_type in asset_types:
        if asset_type == 'layout':
            # 处理 layout 资产
            asset_dir = os.path.join(project_root, 'publish', 'sequence', sequence_name, shot_name, 'layout', 'caches', 'alembic')
            print(f"Layout asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                asset_files = [f for f in os.listdir(asset_dir)
                               if os.path.isfile(os.path.join(asset_dir, f))]
                for f in asset_files:
                    base_name, _ = extract_base_name_and_version(f)
                    assets.add(f"{asset_type}/{base_name}")
                    asset_versions_map.setdefault((asset_type, base_name), []).append(f)
            else:
                print(f"Layout directory does not exist: {asset_dir}")
        elif asset_type == 'character':
            # 处理 character 资产
            asset_dir = os.path.join(project_root, 'publish', 'sequence', sequence_name, shot_name, 'animation', 'caches', 'alembic')
            print(f"Character asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                asset_files = [f for f in os.listdir(asset_dir)
                               if os.path.isfile(os.path.join(asset_dir, f))]
                for f in asset_files:
                    base_name, _ = extract_base_name_and_version(f)
                    assets.add(f"{asset_type}/{base_name}")
                    asset_versions_map.setdefault((asset_type, base_name), []).append(f)
            else:
                print(f"No character asset directory: {asset_dir}")
        else:
            # 对于 'prop'、'set' 等资产类型
            asset_dir = os.path.join(project_root, 'publish', 'assets', asset_type)
            print(f"{asset_type.capitalize()} asset directory: {asset_dir}")
            if os.path.exists(asset_dir):
                for asset_name in os.listdir(asset_dir):
                    asset_path = os.path.join(asset_dir, asset_name)
                    if os.path.isdir(asset_path):
                        assets.add(f"{asset_type}/{asset_name}")
                        # 初始化资产版本映射
                        asset_versions_map[(asset_type, asset_name)] = []
           
    return sorted(list(assets))

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

# 获取指定资产的所有可用版本
def get_versions(asset_type, base_name):
    global version_map
    project_root = get_project_root()
    versions = []
    version_map = {}
    sequence_name, shot_name = get_current_shot()
    if not shot_name:
        cmds.error("Cannot determine the current shot.")
        return versions

    if asset_type in ['layout', 'character']:
        key = (asset_type, base_name)
        if key in asset_versions_map:
            files = asset_versions_map[key]
            version_info = []
            for f in files:
                file_name = os.path.basename(f)
                base, version_number = extract_base_name_and_version(file_name)
                if base == base_name:
                    version_info.append((version_number, f))
                    version_map[file_name] = f  # 将文件名映射到相对路径
            version_info.sort(key=lambda x: x[0], reverse=True)
            versions.extend([os.path.basename(v[1]) for v in version_info])
        else:
            print(f"No versions found for asset {asset_type}/{base_name}")
    else:
        asset_dir = os.path.join(project_root, 'publish', 'assets', asset_type, base_name)
        if os.path.exists(asset_dir):
            for dept in os.listdir(asset_dir):  # 部门可能是 'model'、'rig' 等
                dept_path = os.path.join(asset_dir, dept)
                if os.path.isdir(dept_path):
                    source_dir = os.path.join(dept_path, 'source')
                    if os.path.exists(source_dir):
                        files = [f for f in os.listdir(source_dir) if f.endswith(('.ma', '.mb', '.abc', '.fbx'))]
                        for f in files:
                            base, version_number = extract_base_name_and_version(f)
                            # 使用部门和文件名作为版本标签
                            version_label = f"{dept}/{f}"
                            versions.append(version_label)
                            relative_path = os.path.relpath(os.path.join(source_dir, f), asset_dir)
                            version_map[version_label] = relative_path
        else:
            print(f"No versions found for asset {asset_type}/{base_name}")
    return sorted(versions, reverse=True)

# 当选择资产时，更新版本列表
def on_asset_selected(*args):
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    if selected_assets:
        asset = selected_assets[0]
        asset_type, base_name = asset.split('/', 1)
        versions = get_versions(asset_type, base_name)
        cmds.optionMenu('versionMenu', edit=True, deleteAllItems=True)
        if versions:
            for version in versions:
                cmds.menuItem(label=version, parent='versionMenu')
        else:
            cmds.menuItem(label='No versions found', parent='versionMenu')
    else:
        cmds.optionMenu('versionMenu', edit=True, deleteAllItems=True)

# 加载选定的资产和版本到当前场景中
def load_selected_assets(*args):
    global version_map
    selected_assets = cmds.textScrollList('assetList', query=True, selectItem=True)
    selected_version = cmds.optionMenu('versionMenu', query=True, value=True)
    
    if selected_assets and selected_version and selected_version != 'No versions found':
        sequence_name, shot_name = get_current_shot()
        if not shot_name:
            cmds.error("Cannot determine the current shot.")
            return

        for asset in selected_assets:
            asset_type, base_name = asset.split('/', 1)
            relative_path = version_map.get(selected_version)
            
            if not relative_path:
                cmds.warning(f"Version path not found: {selected_version}")
                continue

            # 根据资产类型构建文件路径
            if asset_type == 'layout':
                file_path = os.path.join(get_project_root(), 'publish', 'sequence', sequence_name, shot_name, 'layout', 'caches', 'alembic', relative_path)
            elif asset_type == 'character':
                file_path = os.path.join(get_project_root(), 'publish', 'sequence', sequence_name, shot_name, 'animation', 'caches', 'alembic', relative_path)
            else:
                asset_dir = os.path.join(get_project_root(), 'publish', 'assets', asset_type, base_name)
                file_path = os.path.join(asset_dir, relative_path)

            # 标准化路径
            full_file_path = os.path.normpath(file_path)
            print(f"Loading asset from: {full_file_path}")

            if os.path.exists(full_file_path):
                namespace = base_name
                existing_refs = cmds.ls(type='reference')
                ref_node = None
                ref_file = None
                
                for ref in existing_refs:
                    try:
                        ref_file = cmds.referenceQuery(ref, filename=True)
                        ref_namespace = cmds.referenceQuery(ref, namespace=True)
                        
                        if ref_namespace.strip(':') == namespace:
                            ref_node = ref
                            break
                    except:
                        continue

                if ref_node:
                    try:
                        cmds.file(full_file_path, loadReference=ref_node)
                        print(f"Replaced reference: {ref_node}, new file: {full_file_path}")
                    except Exception as e:
                        print(f"Failed to replace reference: {e}")
                else:
                    try:
                        ref_node = cmds.file(full_file_path, reference=True, namespace=namespace, returnNewNodes=False, referenceNode=True)
                        print(f"Loaded asset: {asset}, version: {selected_version}")
                    except Exception as e:
                        print(f"Failed to load asset: {e}")
            else:
                cmds.warning(f"File not found: {full_file_path}")

# 运行工具，创建用户界面
create_builder_tool_ui()
