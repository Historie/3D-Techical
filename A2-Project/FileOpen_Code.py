DEFINE FileOpenTool():
    # Step 1: Create Window
    CREATE window with title "File Open Tool"
    SET window size to (width, height)

    # Step 2: Files Option
    CREATE textField for filePath
    CREATE button "Browse" for file selection
    
    ON "Browse" button click:
        OPEN file dialog
        IF user selects a file THEN
            SET textField value to selected file path

    # Step 3: version selection drop-down box
    GET available versions from file system
    CREATE dropdown list for versions
    SET dropdown list to display available versions

    # Step 4: Open Button
    CREATE button "Open File"
    
    ON "Open File" button click:
        GET filePath from textField
        GET selected version from dropdown

    # Step 5: Error
    ON invalidPathError:
        SHOW error "File path is invalid"
    
    # Step 6: Supported Type
    IF fileType is not supported (e.g., not Maya, FBX, Alembic, or USD) THEN
        SHOW error "Unsupported file type"
    
    END FileOpenTool
