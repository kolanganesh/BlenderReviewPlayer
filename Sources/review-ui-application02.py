import sys
import os
import shutil
import json
import subprocess
import platform
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class DragDropWidget(QWidget):
    filesDropped = Signal(list)
    
    def __init__(self, parent=None, label_text="Drag & Drop Videos Here"):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.files = []
        
        # Setup layout
        layout = QVBoxLayout(self)
        
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignCenter)
        
        self.listWidget = QListWidget()
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        layout.addWidget(self.label)
        layout.addWidget(self.listWidget)
        
        # Set widget appearance
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            border: 2px dashed #aaa;
            border-radius: 5px;
            background-color: #16181d;
            color: white;
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            
            files_dropped = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext in ['.mov', '.mp4']:
                    self.files.append(file_path)
                    files_dropped.append(file_path)
                    self.listWidget.addItem(os.path.basename(file_path))
            
            self.filesDropped.emit(files_dropped)
        else:
            event.ignore()
    
    def showContextMenu(self, position):
        context_menu = QMenu(self)
        add_action = context_menu.addAction("Add")
        delete_action = context_menu.addAction("Delete")
        
        action = context_menu.exec_(self.listWidget.viewport().mapToGlobal(position))
        
        if action == add_action:
            self.addFiles()
        elif action == delete_action:
            self.deleteSelectedFiles()
    
    def addFiles(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Video Files")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Video files (*.mov *.mp4)")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            files_added = []
            
            for file_path in file_paths:
                self.files.append(file_path)
                files_added.append(file_path)
                self.listWidget.addItem(os.path.basename(file_path))
            
            self.filesDropped.emit(files_added)
    
    def deleteSelectedFiles(self):
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            return
        
        for item in selected_items:
            row = self.listWidget.row(item)
            file_name = item.text()
            
            # Find the file path in self.files that matches the item text
            for i, file_path in enumerate(self.files):
                if os.path.basename(file_path) == file_name:
                    self.files.pop(i)
                    break
            
            self.listWidget.takeItem(row)
    
    def clear(self):
        self.files = []
        self.listWidget.clear()
    
    def getFiles(self):
        return self.files


class ReviewUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Review UI")
        self.setMinimumSize(800, 600)
        
        # Set dark theme background color
        background_color = "rgb(22, 24, 29)"  # RGB: 0.086, 0.095, 0.114
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background-color: {background_color}; color: white; }}
            
            QListWidget::item:selected {{
                background-color: rgb(128, 128, 128);  /* RGB: 0.5, 0.5, 0.5 */
                color: black;
            }}
            
            QComboBox {{ 
                background-color: #2a2d37; 
                color: white;
                border: 1px solid #444;
                padding: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: #2a2d37;
                color: white;
                selection-background-color: rgb(128, 128, 128);
                selection-color: black;
            }}
            
            QPushButton {{
                background-color: #3c4152;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            
            QPushButton:hover {{
                background-color: #4a5066;
            }}
            
            QPushButton:pressed {{
                background-color: #2d3241;
            }}
            
            QGroupBox {{
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            
            QLabel {{
                color: white;
            }}
        """)
        
        # Main widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)
        
        # Mode selection group
        selectionGroup = QGroupBox("Selection Options")
        selectionLayout = QHBoxLayout(selectionGroup)
        
        self.modeSelector = QComboBox()
        self.modeSelector.addItems(["Sequence", "Compare"])
        self.modeSelector.currentTextChanged.connect(self.onModeChanged)
        selectionLayout.addWidget(self.modeSelector)
        
        mainLayout.addWidget(selectionGroup)
        
        # Sequence widget container
        self.sequenceContainer = QGroupBox("Sequence")
        sequenceLayout = QVBoxLayout(self.sequenceContainer)
        self.sequenceWidget = DragDropWidget(label_text="Drag & Drop Video Files for Sequence")
        sequenceLayout.addWidget(self.sequenceWidget)
        mainLayout.addWidget(self.sequenceContainer)
        
        # Compare widgets container
        self.compareContainer = QGroupBox("Compare")
        compareMainLayout = QVBoxLayout(self.compareContainer)
        
        # Compare mode options
        compareModeGroup = QGroupBox("Compare Mode Options")
        compareModeLayout = QHBoxLayout(compareModeGroup)
        self.compareModeSelector = QComboBox()
        self.compareModeSelector.addItems(["Switch A by B", "Overlay", "Side by Side", "Difference"])
        compareModeLayout.addWidget(self.compareModeSelector)
        compareMainLayout.addWidget(compareModeGroup)
        
        # Compare widgets
        compareWidgetsLayout = QHBoxLayout()
        
        # Compare Widget 1
        compareWidget1Group = QGroupBox("Compare Widget 1")
        compareWidget1Layout = QVBoxLayout(compareWidget1Group)
        self.compareWidget1 = DragDropWidget(label_text="Compare Widget 1")
        compareWidget1Layout.addWidget(self.compareWidget1)
        compareWidgetsLayout.addWidget(compareWidget1Group)
        
        # Compare Widget 2
        compareWidget2Group = QGroupBox("Compare Widget 2")
        compareWidget2Layout = QVBoxLayout(compareWidget2Group)
        self.compareWidget2 = DragDropWidget(label_text="Compare Widget 2")
        compareWidget2Layout.addWidget(self.compareWidget2)
        compareWidgetsLayout.addWidget(compareWidget2Group)
        
        compareMainLayout.addLayout(compareWidgetsLayout)
        mainLayout.addWidget(self.compareContainer)
        
        # Button
        self.openBlenderButton = QPushButton("Open Review play")
        self.openBlenderButton.clicked.connect(self.openBlender)
        mainLayout.addWidget(self.openBlenderButton)
        
        # Set default mode to Sequence
        self.modeSelector.setCurrentText("Sequence")
        self.onModeChanged("Sequence")
    
    def onModeChanged(self, mode):
        # Clear all widgets when switching modes
        self.sequenceWidget.clear()
        self.compareWidget1.clear()
        self.compareWidget2.clear()
        
        if mode == "Sequence":
            self.sequenceContainer.setVisible(True)
            self.compareContainer.setVisible(False)
        else:  # Compare
            self.sequenceContainer.setVisible(False)
            self.compareContainer.setVisible(True)
    
    def openBlender(self):
        current_mode = self.modeSelector.currentText()
        
        try:
            if current_mode == "Sequence":
                files1 = self.sequenceWidget.getFiles()
                if not files1:
                    QMessageBox.critical(self, "Error", "No files added in Sequence widget to play.")
                    return
                
                # Just pass the file list directly, don't send to Blender yet
                print("Sequence Mode Files:")
                for file in files1:
                    print(f" - {file}")

                self.openFilesInBlender(files1, files2=None, compare_mode=None)
                
            else:  # Compare mode
                files1 = self.compareWidget1.getFiles()
                files2 = self.compareWidget2.getFiles()
                
                if not files1 or not files2:
                    QMessageBox.critical(self, "Error", "No files added in one or both Compare widgets.")
                    return
                
                if len(files1) != len(files2):
                    QMessageBox.critical(self, "Error", "Files length not matching in Compare Widget 1 and Compare Widget 2.")
                    return
                
                # Print the lists separately
                print("Compare Mode - List 1:")
                for file in files1:
                    print(f" - {file}")
                
                print("Compare Mode - List 2:")
                for file in files2:
                    print(f" - {file}")
                
                compare_mode = self.compareModeSelector.currentText()
                self.openFilesInBlender(files1, files2, compare_mode)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed too open Blender: {str(e)}")


    def openFilesInBlender(self, files1=None, files2=None, compare_mode=None):
        # Temp path Genration
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # Detect OS and set project path accordingly
        #if platform.system() == "Windows":
        project = os.path.join(CURRENT_DIR, "sequencer.blend")
        script_path = os.path.join(CURRENT_DIR, "sequencer01.py")
        # Optional: convert slashes properly for Blender/Windows
        project = os.path.normpath(project)
        script_path = os.path.normpath(script_path)
        # else:
        #     project = "/tech/INSIDE_MAYA/Blender/Sources/sequencer.blend"
        #     script_path = "/tech/INSIDE_MAYA/Blender/Sources/sequencer01.py"
        # Extract file name and set temp dir
        file_name = os.path.splitext(os.path.basename(files1[0]))[0]
        temp_dir = os.path.join(os.path.expanduser("~"), "temp", file_name)
        os.makedirs(temp_dir, exist_ok=True)



        json_file_name = file_name + ".json"
        temp_sequncerblindfilename = file_name + ".blend"

        temp_sequencer_blend_path  = os.path.join(temp_dir, temp_sequncerblindfilename)
        json_file_path = os.path.join(temp_dir, json_file_name)

        shutil.copy(project, temp_sequencer_blend_path )
  
        data = {"media_file_path_list1" : files1, "media_file_path_list2": files2, "compare_mode" : compare_mode}
        with open(json_file_path, 'w') as f:
            json.dump(data, f)

        print("temp_sequencer_blend_path ", temp_sequencer_blend_path )
        print("json_file_path", json_file_path)

        
        # with open(script_path, "w") as f:
        #     f.write(script_content)


        # Find Blender executable
        blender_path = self.findBlenderPath()
        if not blender_path:
            QMessageBox.critical(self, "Error", "Blender executable not found.")
            return
        
        # Launch Blender with the Python script
        subprocess.Popen([blender_path, temp_sequencer_blend_path , "--python", script_path])

    
    def findBlenderPath(self):
        system = platform.system()
        
        if system == "Windows":
            # Common installation paths on Windows
            paths = [
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
                r"C:\Program Files (x86)\Blender Foundation\Blender\blender.exe"
            ]
            
            # Also check in Program Files for different versions
            program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
            for i in range(2, 5):  # Check for Blender 2.x, 3.x, 4.x
                for j in range(10):
                    version = f"{i}.{j}"
                    path = os.path.join(program_files, "Blender Foundation", f"Blender {version}", "blender.exe")
                    paths.append(path)
        
        elif system == "Linux":
            # Common installation paths on Linux
            paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
                "/snap/bin/blender"
            ]
        
        else:  # macOS or other
            paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "/usr/local/bin/blender"
            ]
        
        # Check if any of the paths exist
        for path in paths:
            if os.path.exists(path):
                return path
        
        # If Blender is in PATH, return "blender"
        try:
            subprocess.run(["blender", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=False)
            return "blender"
        except:
            return None


def run():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a consistent look
    
    window = ReviewUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
