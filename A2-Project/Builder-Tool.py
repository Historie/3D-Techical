import maya.cmds as cmds

def create_scene_builder_ui():
    if cmds.window("sceneBuilderWindow", exists=True):
        cmds.deleteUI("sceneBuilderWindow")

    window = cmds.window("sceneBuilderWindow", title="Scene Builder", widthHeight=(500, 400))
    
    cmds.columnLayout(adjustableColumn=True)

    # 资产选择区
    cmds.frameLayout(label="Select Assets to Load", width=500)
    cmds.checkBox('checkSet', label="Set")
    cmds.checkBox('checkLayout', label="Layout (Camera)")
    cmds.checkBox('checkCharacter', label="Character Animation Cache")
    cmds.checkBox('checkProp', label="Prop Cache")
    cmds.setParent('..')

    # 版本选择
    cmds.frameLayout(label="Select Version")
    cmds.optionMenuGrp('versionMenu', label='Version', columnAlign=(1, 'left'))
    cmds.menuItem(label='Latest')
    cmds.menuItem(label='v001')
    cmds.menuItem(label='v002')
    cmds.setParent('..')

    # 加载按钮
    cmds.button(label="Load Selected Assets", command=lambda *args: load_assets())

    # 信息反馈区域
    cmds.scrollField('infoField', wordWrap=True, editable=False, height=100)

    cmds.showWindow(window)

# 模拟加载资产功能
def load_assets():
    assets_to_load = []
    if cmds.checkBox('checkSet', query=True, value=True):
        assets_to_load.append("Set")
    if cmds.checkBox('checkLayout', query=True, value=True):
        assets_to_load.append("Layout (Camera)")
    if cmds.checkBox('checkCharacter', query=True, value=True):
        assets_to_load.append("Character Animation Cache")
    if cmds.checkBox('checkProp', query=True, value=True):
        assets_to_load.append("Prop Cache")
    
    version = cmds.optionMenuGrp('versionMenu', query=True, value=True)

    cmds.scrollField('infoField', edit=True, insertText=f"Loading assets: {assets_to_load}, Version: {version}\n")

# 运行窗口
create_scene_builder_ui()
