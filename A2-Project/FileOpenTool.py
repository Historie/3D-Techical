import maya.cmds as cmds

# 示例项目数据
project_files = {
    "camera": ["buCamera1", "buCamera2"],
    "character": ["bugMonster", "characterHero"],
    "props": ["buildingProp", "bucket"],
    "environment": ["bigEnvironment", "bush", "beach"]
}

def create_file_open_ui():
    if cmds.window("fileOpenWindow", exists=True):
        cmds.deleteUI("fileOpenWindow")

    window = cmds.window("fileOpenWindow", title="File Open", widthHeight=(800, 600))

    cmds.columnLayout(adjustableColumn=True)

    # 左侧布局 - 文件结构和过滤器
    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth2=(200, 600))

    # 左侧文件结构
    cmds.frameLayout(label="Project File Structure", width=200)
    cmds.textScrollList('fileList', numberOfRows=10, allowMultiSelection=False, append=list(project_files.keys()), selectCommand=lambda: file_selected())
    cmds.setParent('..')

    # 右侧布局 - 筛选、状态和搜索区域
    cmds.columnLayout(adjustableColumn=True)

    # 筛选器区域
    cmds.frameLayout(label="Filter by Pipeline Step")
    cmds.checkBox('filter2D', label="2D", onCommand=lambda *args: update_file_list())
    cmds.checkBox('filter3D', label="3D", onCommand=lambda *args: update_file_list())
    cmds.checkBox('filterAnim', label="Animation", onCommand=lambda *args: update_file_list())
    cmds.checkBox('filterComp', label="Comp", onCommand=lambda *args: update_file_list())
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(100, 100))
    cmds.button(label="Select All", command=lambda *args: select_all_filters())
    cmds.button(label="Select None", command=lambda *args: deselect_all_filters())
    cmds.setParent('..')

    # 文件状态和版本选择
    cmds.frameLayout(label="File Status and Versions")
    cmds.rowLayout(numberOfColumns=4, adjustableColumn=2)
    cmds.text(label="Show:")
    cmds.radioButtonGrp('statusRadio', labelArray3=['All', 'Working', 'Publishes'], numberOfRadioButtons=3, select=1)
    cmds.setParent('..')

    # 版本选择
    cmds.optionMenuGrp('versionMenu', label='Version', columnAlign=(1, 'left'))
    cmds.menuItem(label='All Versions')
    cmds.menuItem(label='v001')
    cmds.menuItem(label='v002')
    cmds.menuItem(label='v003')
    cmds.setParent('..')

    # 搜索栏，监听回车键事件
    cmds.frameLayout(label="Search Files")
    cmds.textField('searchField', placeholderText="Search...", enterCommand=lambda *args: search_files())
    cmds.setParent('..')

    cmds.setParent('..')  # 回到主布局

    cmds.showWindow(window)

# 模拟选择文件的回
def file_selected():
    selected_file = cmds.textScrollList('fileList', query=True, selectItem=True)
    print(f"Selected file: {selected_file[0] if selected_file else 'None'}")

# 更新文件列表（根据过滤器和搜索词）
def update_file_list():
    filters = []
    if cmds.checkBox('filter2D', query=True, value=True):
        filters.append('2D')
    if cmds.checkBox('filter3D', query=True, value=True):
        filters.append('3D')
    if cmds.checkBox('filterAnim', query=True, value=True):
        filters.append('Animation')
    if cmds.checkBox('filterComp', query=True, value=True):
        filters.append('Comp')

    # 你可以在这里根据选中的过滤器更新文件列表
    print(f"Filters applied: {filters}")

# 搜索文件
def search_files():
    search_term = cmds.textField('searchField', query=True, text=True)
    print(f"Searching for: {search_term}")
    
    # 获取当前选中的过滤器（模拟的筛选逻辑）
    matching_files = []
    for category, files in project_files.items():
        for file in files:
            if search_term.lower() in file.lower():  # 根据搜索词匹配
                matching_files.append(category)

    # 更新文件结构中的列表
    cmds.textScrollList('fileList', edit=True, removeAll=True)
    cmds.textScrollList('fileList', edit=True, append=matching_files)

# 选择所有过滤器
def select_all_filters():
    cmds.checkBox('filter2D', edit=True, value=True)
    cmds.checkBox('filter3D', edit=True, value=True)
    cmds.checkBox('filterAnim', edit=True, value=True)
    cmds.checkBox('filterComp', edit=True, value=True)
    update_file_list()

# 取消选择所有过滤器
def deselect_all_filters():
    cmds.checkBox('filter2D', edit=True, value=False)
    cmds.checkBox('filter3D', edit=True, value=False)
    cmds.checkBox('filterAnim', edit=True, value=False)
    cmds.checkBox('filterComp', edit=True, value=False)
    update_file_list()

# 运行窗口
create_file_open_ui()
