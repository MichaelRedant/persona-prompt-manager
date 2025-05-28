from PySide6.QtWidgets import QFileDialog, QMessageBox
import json

def export_personas(self):
    try:
        file_name, _ = QFileDialog.getSaveFileName(self, "Export persona's", "personas.json", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.personas], f, indent=2, ensure_ascii=False)
    except Exception as e:
        QMessageBox.critical(self, "Fout bij exporteren", str(e))

def export_prompts(self):
    try:
        file_name, _ = QFileDialog.getSaveFileName(self, "Export prompts", "prompts.json", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self.prompts], f, indent=2, ensure_ascii=False)
    except Exception as e:
        QMessageBox.critical(self, "Fout bij exporteren", str(e))
