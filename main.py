import sys
import os
import cv2
import shutil
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QListWidget, 
                             QListWidgetItem, QLabel, QLineEdit, QSpinBox, 
                             QMessageBox, QAbstractItemView, QDialog, QTableWidget, 
                             QTableWidgetItem, QMenu, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QImage

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
    """ Retorna o caminho absoluto para o recurso, compatível com o PyInstaller (_MEIPASS) """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
        
        # Carrega o ícone pelo caminho absoluto, seja no dev ou no EXE compilado
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
        dest_folder = self.txt_dest_folder.text().strip()
        
        preview_data = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            original_path = item.data(Qt.ItemDataRole.UserRole)
            ext = os.path.splitext(original_path)[1]
            
            new_name = f"{base_name}-{str(i).zfill(digits)}{ext}"
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
    # Diz ao Windows que este é um app único (desanexa do python.exe padrão)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('fornecedor.renomeadorpro.1.0')
    
    app = QApplication(sys.argv)
    
    # Aplica o ícone global na aplicação
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())