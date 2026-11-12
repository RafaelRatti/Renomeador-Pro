import sys
import os
import cv2
import shutil
import ctypes
import base64
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QListWidget, 
                             QListWidgetItem, QLabel, QLineEdit, QSpinBox, 
                             QMessageBox, QAbstractItemView, QDialog, QTableWidget, 
                             QTableWidgetItem, QMenu, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QImage

# --- ÍCONE DE XÍCARA DE CAFÉ EMBUTIDO ---
ICON_B64 = b'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'

STYLE_SHEET = """
QMainWindow {
    background-color: #1e1e1e;
}
QWidget {
    color: #e0e0e0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
QLabel {
    font-size: 13px;
}
QPushButton {
    background-color: #333333;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 6px 12px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #444444;
}
QPushButton:pressed {
    background-color: #222222;
}
QPushButton#btn_rename {
    background-color: #0078D7;
    color: white;
    font-weight: bold;
    border: none;
    padding: 8px 16px;
}
QPushButton#btn_rename:hover {
    background-color: #1084ea;
}
QLineEdit, QSpinBox {
    background-color: #2d2d2d;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    font-size: 13px;
}
QListWidget {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 5px;
    outline: none;
}
QListWidget::item {
    border-radius: 5px;
    padding: 5px;
}
QListWidget::item:selected {
    background-color: #0078D7;
    color: white;
}
QMenu {
    background-color: #2d2d2d;
    border: 1px solid #555;
}
QMenu::item:selected {
    background-color: #0078D7;
}
QTableWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    gridline-color: #555555;
    border: 1px solid #555555;
}
QHeaderView::section {
    background-color: #333333;
    color: white;
    border: 1px solid #555555;
    padding: 4px;
}
"""

IMG_EXT = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif']
VID_EXT = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_icon_if_needed():
    try:
        if os.path.exists("icon.ico"):
            os.remove("icon.ico")
    except:
        pass
    
    with open("icon.ico", "wb") as f:
        f.write(base64.b64decode(ICON_B64))

class IconTextDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        try:
            option.decorationPosition = QStyleOptionViewItem.Position.Top
            option.displayAlignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        except AttributeError:
            pass

class ThumbnailWorker(QThread):
    thumb_ready = pyqtSignal(str, QIcon)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        for path in self.file_paths:
            ext = os.path.splitext(path)[1].lower()
            icon = QIcon()
            try:
                if ext in IMG_EXT:
                    pixmap = QPixmap(path)
                    icon = QIcon(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                elif ext in VID_EXT:
                    cap = cv2.VideoCapture(path)
                    ret, frame = cap.read()
                    if ret:
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = frame.shape
                        bytes_per_line = ch * w
                        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                        pixmap = QPixmap.fromImage(qimg)
                        icon = QIcon(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    cap.release()
            except Exception:
                pass 
            self.thumb_ready.emit(path, icon)

class DraggableListWidget(QListWidget):
    files_dropped = pyqtSignal(list)
    order_updated = pyqtSignal()
    items_removed = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        
        self.setViewMode(QListWidget.ViewMode.ListMode)  
        self.setFlow(QListWidget.Flow.LeftToRight)       
        self.setWrapping(True)                           
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setWordWrap(True)
        
        self.setItemDelegate(IconTextDelegate(self))
        
        self.setSpacing(10)
        self.setIconSize(QSize(120, 120))
        self.setGridSize(QSize(150, 180)) 
        
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        else:
            super().keyPressEvent(event)

    def show_context_menu(self, position):
        if not self.selectedItems():
            return
        menu = QMenu()
        remove_action = menu.addAction("Remover da Seleção (Delete)")
        action = menu.exec(self.mapToGlobal(position))
        if action == remove_action:
            self.remove_selected()

    def remove_selected(self):
        removed_paths = []
        for item in self.selectedItems():
            path = item.data(Qt.ItemDataRole.UserRole)
            removed_paths.append(path)
            self.takeItem(self.row(item))
            
        if removed_paths:
            self.items_removed.emit(removed_paths)
            self.order_updated.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls]
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
            self.order_updated.emit()


class PreviewDialog(QDialog):
    def __init__(self, preview_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pré-visualização")
        self.resize(700, 450)
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget(len(preview_data), 3)
        self.table.setHorizontalHeaderLabels(["Nome Original", "Novo Nome", "Destino"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        for row, (old, new, dest) in enumerate(preview_data):
            self.table.setItem(row, 0, QTableWidgetItem(os.path.basename(old)))
            self.table.setItem(row, 1, QTableWidgetItem(new))
            self.table.setItem(row, 2, QTableWidgetItem(dest))
            
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_confirm = QPushButton("Confirmar e Executar")
        btn_confirm.setObjectName("btn_rename")
        btn_confirm.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Renomeador Pro em Lote")
        self.resize(950, 650)
        
        self.setStyleSheet(STYLE_SHEET)
        
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.loaded_files = {} 
        self.worker = None

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        top_bar = QHBoxLayout()
        btn_add_files = QPushButton("Adicionar Arquivos")
        btn_add_files.clicked.connect(self.add_files)
        
        btn_add_folder = QPushButton("Adicionar Pasta")
        btn_add_folder.clicked.connect(self.add_folder)
        
        btn_clear = QPushButton("Limpar Lista")
        btn_clear.clicked.connect(self.clear_list)
        
        self.lbl_count = QLabel("Arquivos carregados: 0")
        
        top_bar.addWidget(btn_add_files)
        top_bar.addWidget(btn_add_folder)
        top_bar.addWidget(btn_clear)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_count)
        main_layout.addLayout(top_bar)

        self.list_widget = DraggableListWidget(self)
        self.list_widget.files_dropped.connect(self.process_new_files)
        self.list_widget.order_updated.connect(self.update_count)
        self.list_widget.items_removed.connect(self.remove_tracked_files)
        main_layout.addWidget(self.list_widget)

        bottom_layout = QVBoxLayout()
        
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Pasta de Destino (Opcional):"))
        self.txt_dest_folder = QLineEdit()
        self.txt_dest_folder.setPlaceholderText("Manter na pasta original (Padrão)")
        self.txt_dest_folder.setReadOnly(True)
        dest_layout.addWidget(self.txt_dest_folder)
        
        btn_browse_dest = QPushButton("Procurar...")
        btn_browse_dest.clicked.connect(self.choose_dest_folder)
        btn_clear_dest = QPushButton("Limpar Destino")
        btn_clear_dest.clicked.connect(self.txt_dest_folder.clear)
        
        dest_layout.addWidget(btn_browse_dest)
        dest_layout.addWidget(btn_clear_dest)
        bottom_layout.addLayout(dest_layout)
        
        rename_layout = QHBoxLayout()
        rename_layout.addWidget(QLabel("Nome base:"))
        self.txt_base_name = QLineEdit()
        self.txt_base_name.setPlaceholderText("Ex: FOTOS_VIAGEM")
        rename_layout.addWidget(self.txt_base_name)
        
        # --- NOVO CAMPO: NÚMERO INICIAL ---
        rename_layout.addWidget(QLabel("Nº Inicial:"))
        self.spin_start_num = QSpinBox()
        self.spin_start_num.setRange(0, 999999) # Suporta até 999.999
        self.spin_start_num.setValue(0)         # Começa em 0 por padrão
        rename_layout.addWidget(self.spin_start_num)
        
        rename_layout.addWidget(QLabel("Dígitos:"))
        self.spin_digits = QSpinBox()
        self.spin_digits.setRange(1, 6)
        self.spin_digits.setValue(3)
        rename_layout.addWidget(self.spin_digits)
        
        btn_preview = QPushButton("Visualizar / Renomear")
        btn_preview.setObjectName("btn_rename")
        btn_preview.clicked.connect(self.prepare_rename)
        rename_layout.addWidget(btn_preview)
        
        bottom_layout.addLayout(rename_layout)
        main_layout.addLayout(bottom_layout)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos", "", "Mídia (*.jpg *.jpeg *.png *.webp *.bmp *.gif *.mp4 *.avi *.mov *.mkv *.wmv)")
        if files:
            self.process_new_files(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if folder:
            files = []
            for f in os.listdir(folder):
                ext = os.path.splitext(f)[1].lower()
                if ext in IMG_EXT or ext in VID_EXT:
                    files.append(os.path.join(folder, f))
            self.process_new_files(files)

    def choose_dest_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Destino")
        if folder:
            self.txt_dest_folder.setText(folder)

    def process_new_files(self, paths):
        valid_paths = [p for p in paths if os.path.splitext(p)[1].lower() in (IMG_EXT + VID_EXT) and p not in self.loaded_files]
        
        if not valid_paths:
            return

        for path in valid_paths:
            item = QListWidgetItem(os.path.basename(path))
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.list_widget.addItem(item)
            self.loaded_files[path] = item
        
        self.update_count()
        
        self.worker = ThumbnailWorker(valid_paths)
        self.worker.thumb_ready.connect(self.apply_thumbnail)
        self.worker.start()

    def apply_thumbnail(self, path, icon):
        if path in self.loaded_files:
            item = self.loaded_files[path]
            item.setIcon(icon)

    def remove_tracked_files(self, paths):
        for p in paths:
            if p in self.loaded_files:
                del self.loaded_files[p]

    def clear_list(self):
        self.list_widget.clear()
        self.loaded_files.clear()
        self.update_count()

    def update_count(self):
        self.lbl_count.setText(f"Arquivos carregados: {self.list_widget.count()}")

    def prepare_rename(self):
        if self.list_widget.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo na lista.")
            return
            
        base_name = self.txt_base_name.text().strip()
        if not base_name:
            QMessageBox.warning(self, "Aviso", "Digite um nome base para os arquivos.")
            return

        digits = self.spin_digits.value()
        start_num = self.spin_start_num.value() # Pega o valor do novo campo
        dest_folder = self.txt_dest_folder.text().strip()
        
        preview_data = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            original_path = item.data(Qt.ItemDataRole.UserRole)
            ext = os.path.splitext(original_path)[1]
            
            current_num = start_num + i # Soma a posição ao número inicial
            new_name = f"{base_name}-{str(current_num).zfill(digits)}{ext}"
            target_dir = dest_folder if dest_folder else os.path.dirname(original_path)
            
            preview_data.append((original_path, new_name, target_dir))
            
        dialog = PreviewDialog(preview_data, self)
        if dialog.exec():
            self.execute_rename(preview_data)

    def execute_rename(self, preview_data):
        success_count = 0
        errors = []

        for original_path, new_name, target_dir in preview_data:
            new_path = os.path.join(target_dir, new_name)
            
            if os.path.exists(new_path) and original_path.lower() != new_path.lower():
                reply = QMessageBox.question(self, "Conflito de Arquivo", 
                                             f"O arquivo '{new_name}' já existe na pasta de destino.\nDeseja sobrescrever?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return 

        for original_path, new_name, target_dir in preview_data:
            new_path = os.path.join(target_dir, new_name)
            
            try:
                shutil.move(original_path, new_path)
                success_count += 1
            except Exception as e:
                errors.append(f"{os.path.basename(original_path)}: {str(e)}")

        if errors:
            QMessageBox.warning(self, "Concluído com erros", f"{success_count} processados. Erros:\n" + "\n".join(errors[:5]))
        else:
            QMessageBox.information(self, "Sucesso", f"{success_count} arquivos renomeados com sucesso!")
        
        self.clear_list()

if __name__ == '__main__':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('fornecedor.renomeadorpro.1.0')
    
    app = QApplication(sys.argv)
    
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())