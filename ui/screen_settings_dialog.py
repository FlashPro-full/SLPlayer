"""
Screen Parameters Setting dialog redesigned to match the provided layout.
Populates controller list from local DB, supports NovaStar and Huidu presets.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem, QDialogButtonBox, QWidget, QGridLayout, QGroupBox, QHeaderView, QFormLayout
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont
from config.i18n import tr
from pathlib import Path
import json


class ScreenSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Screen Parameters Setting")
        self.setMinimumSize(740, 520)
        self._controllers = []
        self._build_ui()
        self._load_controllers_from_db()
        self._wire_events()
        self.series_combo.setCurrentText("Huidu")
        try:
            from core.controller_database import get_controller_database
            db = get_controller_database()
            seed_path = Path(__file__).parent.parent / "resources" / "controller_models_seed.json"
            if seed_path.exists():
                with open(seed_path, "r", encoding="utf-8") as f:
                    arr = json.load(f) or []
                seeds = {}
                for item in arr:
                    brand = item.get("brand")
                    model = item.get("model")
                    if not brand or not model:
                        continue
                    seeds[(brand, model)] = {
                        "range": item.get("range"),
                        "max_w": item.get("max_w"),
                        "max_h": item.get("max_h"),
                        "storage": item.get("storage"),
                        "gray": item.get("gray"),
                        "iface": item.get("iface"),
                        "other": item.get("other"),
                    }
                if seeds:
                    db.seed_models_if_empty(seeds)
        except Exception:
            pass
        self._populate_models()

    def _is_first_screen(self) -> bool:
        """Return True if this is the first screen (no programs exist)."""
        try:
            pm = getattr(self.parent(), "program_manager", None)
            return bool(pm is not None and not getattr(pm, "programs", []))
        except Exception:
            return False

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        self.setStyleSheet("""
            QDialog {
                background: #F5F7FA;
            }
            QLabel#HeaderLabel {
                font-size: 22px;
                font-weight: 700;
                color: #1F2937;
            }
            QGroupBox {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0px 4px;
                color: #6B7280;
                font-weight: 600;
                font-size: 18px;
            }
            QLabel {
                color: #374151;
                font-size: 12px;
            }
            QComboBox, QSpinBox, QLineEdit {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QCheckBox {
                font-size: 12px;
                color: #111827;
            }
            QTableWidget {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #E5E7EB;
                font-size: 12px;
            }
            QHeaderView::section {
                background: #F3F4F6;
                padding: 8px 10px;
                border: 0px;
                border-bottom: 1px solid #E5E7EB;
                color: #6B7280;
                font-weight: 600;
            }
            QDialogButtonBox QPushButton {
                padding: 6px 14px;
                border-radius: 6px;
                background: #2563EB;
                color: #FFFFFF;
                border: 1px solid #1D4ED8;
            }
            QDialogButtonBox QPushButton:hover {
                background: #1D4ED8;
                border-color: #1E40AF;
            }
            QDialogButtonBox QPushButton:disabled {
                background: #9CA3AF;
                border-color: #9CA3AF;
                color: #FFFFFF;
            }
        """)

        top_row = QHBoxLayout()
        top_label = QLabel(tr("screen.controller_list") or "Controller list")
        top_label.setToolTip("Controllers previously connected and stored locally")
        top_row.addWidget(top_label)
        self.controller_combo = QComboBox(self)
        self.controller_combo.setToolTip("Choose a connected controller from the local database")
        self.controller_combo.setEditable(False)
        top_row.addWidget(self.controller_combo, stretch=1)
        root.addLayout(top_row)

        self.header_label = QLabel("Controller Name", self)
        self.header_label.setObjectName("HeaderLabel")
        try:
            self.header_label.setIndent(300)
        except Exception:
            pass
        root.addWidget(self.header_label)

        left_group = QGroupBox("Configuration", self)
        form = QFormLayout(left_group)
        form.setContentsMargins(12, 8, 12, 12)
        form.setSpacing(20)
        try:
            form.setHorizontalSpacing(12)
            form.setVerticalSpacing(20)
        except Exception:
            pass

        self.use_controller_setting = QCheckBox(tr("screen.use_controller_setting") or "Use Controller Setting", left_group)
        try:
            self.use_controller_setting.setStyleSheet("margin-top: 10px;")
        except Exception:
            pass
        self.use_controller_setting.setToolTip("When enabled, parameters are derived from the selected controller")
        form.addRow(self.use_controller_setting)

        self.series_combo = QComboBox(left_group)
        self.series_combo.addItems(["NovaStar", "Huidu"])
        self.series_combo.setToolTip("Controller brand / series")
        self.model_combo = QComboBox(left_group)
        self.model_combo.setToolTip("Controller model")
        type_row = QWidget(left_group)
        type_row_layout = QHBoxLayout(type_row)
        type_row_layout.setContentsMargins(0, 0, 0, 0)
        type_row_layout.setSpacing(12)
        type_row_layout.addWidget(self.series_combo)
        type_row_layout.addWidget(self.model_combo)
        form.addRow(QLabel("Controller type", left_group), type_row)

        lbl_w = QLabel(tr("screen.width") or "Width", left_group)
        lbl_w.setToolTip("Screen width (pixels)")
        self.width_spin = QSpinBox(left_group)
        self.width_spin.setRange(8, 16384)
        self.width_spin.setValue(256)
        self.width_spin.setSingleStep(1)
        self.width_spin.setToolTip("Screen width in pixels")
        form.addRow(lbl_w, self.width_spin)

        lbl_h = QLabel(tr("screen.height") or "Height", left_group)
        lbl_h.setToolTip("Screen height (pixels)")
        self.height_spin = QSpinBox(left_group)
        self.height_spin.setRange(8, 16384)
        self.height_spin.setValue(480)
        self.height_spin.setSingleStep(1)
        self.height_spin.setToolTip("Screen height in pixels")
        form.addRow(lbl_h, self.height_spin)

        lbl_rot = QLabel(tr("screen.rotate") or "Rotate", left_group)
        lbl_rot.setToolTip("Rotate output orientation")
        self.rotate_combo = QComboBox(left_group)
        self.rotate_combo.addItems(["0", "90", "180", "270"])
        self.rotate_combo.setToolTip("Rotation in degrees")
        form.addRow(lbl_rot, self.rotate_combo)

        self.table = QTableWidget(7, 2, self)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(self.table.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(self.table.sizePolicy().Expanding, self.table.sizePolicy().Expanding)
        try:
            self.table.setMinimumSize(560, 380)
        except Exception:
            pass
        header = self.table.horizontalHeader()
        try:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass
        for r in range(7):
            self.table.setRowHeight(r, 44)
        labels = [
            tr("screen.suggested_range") or "Suggested range",
            tr("screen.max_width") or "Maximum width",
            tr("screen.max_height") or "Maximum height",
            tr("screen.storage_capacity") or "Storage capacity",
            tr("screen.gray_scale") or "Gray Scale",
            tr("screen.comm_interface") or "Communication Interface",
            tr("screen.other") or "Other",
        ]
        for i, l in enumerate(labels):
            self.table.setItem(i, 0, QTableWidgetItem(l))
            self.table.setItem(i, 1, QTableWidgetItem(""))

        mid_row = QHBoxLayout()
        mid_row.setSpacing(14)
        mid_row.addWidget(left_group, stretch=0)
        mid_row.addSpacing(20)
        right_panel = QWidget(self)
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.setContentsMargins(0, 0, 0, 0)
        rp_layout.setSpacing(0)
        rp_layout.addStretch(1)
        rp_layout.addWidget(self.table, alignment=Qt.AlignCenter)
        rp_layout.addStretch(1)
        mid_row.addWidget(right_panel, stretch=1)
        root.addLayout(mid_row, stretch=1)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        try:
            if self._is_first_screen():
                cancel_btn = self.buttons.button(self.buttons.StandardButton.Cancel)
                if cancel_btn:
                    cancel_btn.setEnabled(False)
                try:
                    self.setWindowFlag(Qt.WindowCloseButtonHint, False)
                    self.setWindowFlags(self.windowFlags())  # apply flag changes
                except Exception:
                    pass
        except Exception:
            pass
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        root.addWidget(self.buttons, alignment=Qt.AlignRight)

    def _wire_events(self):
        self.series_combo.currentTextChanged.connect(self._populate_models)
        self.model_combo.currentTextChanged.connect(self._apply_preset_from_selection)
        self.controller_combo.currentIndexChanged.connect(self._on_controller_selected)
        self.use_controller_setting.toggled.connect(self._on_use_controller_setting_toggled)

    def _load_controllers_from_db(self):
        """Load controllers from database and populate the combo box"""
        try:
            from core.controller_database import get_controller_database
            db = get_controller_database()
            self._controllers = db.get_all_controllers(active_only=False) or []
            self.controller_combo.clear()
            if not self._controllers:
                self.controller_combo.addItem("No controllers found", userData=None)
            else:
                for row in self._controllers:
                    device_name = row.get('device_name') or row.get('model') or ''
                    controller_id = row.get('controller_id', '')
                    if device_name:
                        display = f"{device_name}  ({controller_id})"
                    else:
                        display = controller_id
                    self.controller_combo.addItem(display, userData=row)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error loading controllers from database: {e}")
            self._controllers = []
            self.controller_combo.clear()
            self.controller_combo.addItem("Error loading controllers", userData=None)
    
    def showEvent(self, event: QEvent):
        """Refresh controller list when dialog is shown"""
        super().showEvent(event)
        self._load_controllers_from_db()

    def _populate_models(self):
        series = self.series_combo.currentText()
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        try:
            from core.controller_database import get_controller_database
            db = get_controller_database()
            models = db.get_models_by_brand(series)
            model_names = [m.get("model") for m in models if m.get("model")]
            if model_names:
                self.model_combo.addItems(model_names)
        except Exception:
            pass
        self.model_combo.blockSignals(False)
        if self.model_combo.count() > 0:
            self.model_combo.setCurrentIndex(0)
        self._apply_preset_from_selection()

    def _apply_preset_from_selection(self):
        series = self.series_combo.currentText()
        model = self.model_combo.currentText()
        preset = {}
        try:
            from core.controller_database import get_controller_database
            db = get_controller_database()
            row = db.get_model_spec(series, model)
            if row:
                preset = {
                    "range": row.get("suggested_range"),
                    "max_w": row.get("max_width"),
                    "max_h": row.get("max_height"),
                    "storage": row.get("storage_capacity"),
                    "gray": row.get("gray_scale"),
                    "iface": row.get("communication_interface"),
                    "other": row.get("other"),
                }
        except Exception:
            preset = {}
        try:
            if not self.use_controller_setting.isChecked():
                header = f"{series} · {model}" if model else series
                self.header_label.setText(header)
            else:
                pass
        except Exception:
            pass
        def set_row(idx, val):
            self.table.setItem(idx, 1, QTableWidgetItem(str(val) if val is not None else ""))
        if not self.use_controller_setting.isChecked():
            set_row(0, preset.get("range", ""))
            set_row(1, preset.get("max_w", ""))
            set_row(2, preset.get("max_h", ""))
            set_row(3, preset.get("storage", ""))
            set_row(4, preset.get("gray", ""))
            set_row(5, preset.get("iface", ""))
            set_row(6, preset.get("other", ""))
            
            max_w = preset.get("max_w")
            max_h = preset.get("max_h")
            if max_w:
                try:
                    max_w_int = int(max_w) if isinstance(max_w, (int, str)) else 16384
                    self.width_spin.setMaximum(max_w_int)
                except (ValueError, TypeError):
                    self.width_spin.setMaximum(16384)
            else:
                self.width_spin.setMaximum(16384)
            
            if max_h:
                try:
                    max_h_int = int(max_h) if isinstance(max_h, (int, str)) else 16384
                    self.height_spin.setMaximum(max_h_int)
                except (ValueError, TypeError):
                    self.height_spin.setMaximum(16384)
            else:
                self.height_spin.setMaximum(16384)
            
            range_str = preset.get("range", "")
            if range_str:
                try:
                    range_str = str(range_str).strip()
                    range_str = range_str.replace(',', 'x').replace(' ', '')
                    if 'x' in range_str.lower():
                        parts = range_str.lower().split('x')
                        if len(parts) == 2:
                            suggested_w = int(parts[0].strip())
                            suggested_h = int(parts[1].strip())
                            self.width_spin.setValue(min(suggested_w, self.width_spin.maximum()))
                            self.height_spin.setValue(min(suggested_h, self.height_spin.maximum()))
                except (ValueError, AttributeError, IndexError):
                    pass

    def _on_controller_selected(self, idx: int):
        data = self.controller_combo.itemData(idx)
        if not data:
            return
        if self.use_controller_setting.isChecked():
            self._apply_preset_from_controller(data)
            self._update_header_from_controller()
            return
        ctype = (data.get("controller_type") or "").lower()
        model = (data.get("model") or "") or (data.get("device_name") or "")
        if "nova" in ctype:
            self.series_combo.setCurrentText("NovaStar")
            self._select_model_if_present_db(model, "NovaStar")
        elif "huidu" in ctype or "hd-" in (model or "").lower():
            self.series_combo.setCurrentText("Huidu")
            self._select_model_if_present_db(model, "Huidu")

    def _select_model_if_present_db(self, model: str, brand: str):
        target = None
        if model:
            try:
                from core.controller_database import get_controller_database
                db = get_controller_database()
                models = db.get_models_by_brand(brand)
                for m in models:
                    name = m.get("model")
                    if name and name.lower() in model.lower():
                        target = name
                        break
            except Exception:
                target = None
        if target:
            self.model_combo.setCurrentText(target)

    def _on_use_controller_setting_toggled(self, checked: bool):
        if checked:
            data = self.controller_combo.currentData()
            if data:
                self._apply_preset_from_controller(data)
            for w in (self.series_combo, self.model_combo, self.width_spin, self.height_spin):
                w.setEnabled(False)
            self.rotate_combo.setEnabled(True)
            if data:
                self._update_header_from_controller()
            else:
                self.header_label.setText("")
                self._clear_properties_table()
        else:
            for w in (self.series_combo, self.model_combo, self.width_spin, self.height_spin):
                w.setEnabled(True)
            series = self.series_combo.currentText()
            model = self.model_combo.currentText()
            header = f"{series} · {model}" if model else series
            self.header_label.setText(header)
            self._apply_preset_from_selection()

    def _update_header_from_controller(self):
        try:
            idx = self.controller_combo.currentIndex()
            row = self.controller_combo.itemData(idx)
            display = None
            if row:
                display = row.get("device_name") or row.get("model") or row.get("controller_id")
            self.header_label.setText(str(display) if display else "")
        except Exception:
            pass

    def _apply_preset_from_controller(self, row: dict):
        ctype = (row.get("controller_type") or "").lower()
        model = (row.get("model") or "") or (row.get("device_name") or "")
        if "nova" in ctype:
            self.series_combo.setCurrentText("NovaStar")
            self._select_model_if_present_db(model, "NovaStar")
            self._apply_preset_from_selection()
        elif "huidu" in ctype or "hd-" in (model or "").lower():
            self.series_combo.setCurrentText("Huidu")
            self._select_model_if_present_db(model, "Huidu")
            self._apply_preset_from_selection()
        
        try:
            from core.controller_database import get_controller_database
            db = get_controller_database()
            series = self.series_combo.currentText()
            model_name = self.model_combo.currentText()
            if series and model_name:
                spec = db.get_model_spec(series, model_name)
                if spec:
                    max_w = spec.get("max_width")
                    max_h = spec.get("max_height")
                    if max_w:
                        try:
                            max_w_int = int(max_w) if isinstance(max_w, (int, str)) else 16384
                            self.width_spin.setMaximum(max_w_int)
                        except (ValueError, TypeError):
                            pass
                    if max_h:
                        try:
                            max_h_int = int(max_h) if isinstance(max_h, (int, str)) else 16384
                            self.height_spin.setMaximum(max_h_int)
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass
        
        res = row.get("display_resolution") or ""
        if isinstance(res, str) and "x" in res.lower():
            try:
                parts = res.lower().replace(" ", "").split("x")
                w, h = int(parts[0]), int(parts[1])
                self.width_spin.setValue(max(8, min(self.width_spin.maximum(), w)))
                self.height_spin.setValue(max(8, min(self.height_spin.maximum(), h)))
            except Exception:
                pass
        device_name = row.get("device_name") or row.get("model") or row.get("controller_id")
        try:
            if self.use_controller_setting.isChecked():
                self.header_label.setText(str(device_name) if device_name else "")
            else:
                series = self.series_combo.currentText()
                model = self.model_combo.currentText()
                header = f"{series} · {model}" if model else series
                self.header_label.setText(header)
        except Exception:
            self.header_label.setText("")

    def _clear_properties_table(self):
        """Clear right-side values (keep labels)."""
        try:
            for i in range(7):
                self.table.setItem(i, 1, QTableWidgetItem(""))
        except Exception:
            pass

    def reject(self):
        if self._is_first_screen():
            return
        return super().reject()

    def selected_size(self):
        return self.width_spin.value(), self.height_spin.value()

    def selected_series(self):
        return self.series_combo.currentText()

    def selected_model(self):
        return self.model_combo.currentText()
    
    def selected_rotate(self):
        """Get selected rotation value as integer"""
        try:
            return int(self.rotate_combo.currentText())
        except (ValueError, TypeError):
            return 0
    
    def selected_controller_id(self):
        """Get selected controller ID from combo box"""
        try:
            idx = self.controller_combo.currentIndex()
            row = self.controller_combo.itemData(idx)
            if row:
                return row.get("controller_id")
        except Exception:
            pass
        return None

    def accept(self):
        """Save selection to local DB and close."""
        try:
            from core.controller_database import get_controller_database
            from core.license_manager import LicenseManager
            from utils.logger import get_logger
            db = get_controller_database()
            license_manager = LicenseManager()
            logger = get_logger(__name__)
            ctrl_id = None
            try:
                idx = self.controller_combo.currentIndex()
                row = self.controller_combo.itemData(idx)
                if row:
                    ctrl_id = row.get("controller_id")
            except Exception:
                ctrl_id = None
            
            if ctrl_id:
                license_file = license_manager.get_license_file_path(ctrl_id)
                logger.info(f"Checking license file for {ctrl_id}: {license_file}")
                logger.info(f"License file exists: {license_file.exists()}")
                if license_file.exists():
                    license_data = license_manager.load_license_file(ctrl_id)
                    if license_data:
                        logger.info(f"License file exists and is valid for {ctrl_id}, skipping screen parameter save to DB")
                        return super().accept()
                    else:
                        logger.warning(f"License file exists but is invalid for {ctrl_id}, saving screen parameters to DB")
                else:
                    logger.info(f"License file does not exist for {ctrl_id}, saving screen parameters to DB")
            
            db.save_screen_parameters({
                "brand": self.selected_series(),
                "model": self.selected_model(),
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "rotate": int(self.rotate_combo.currentText() if self.rotate_combo.currentText().isdigit() else 0),
                "controller_id": ctrl_id
            })
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(__name__)
            logger.exception(f"Error in accept: {e}")
        super().accept()


