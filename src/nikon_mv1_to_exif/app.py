"""PyQt6 desktop application."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nikon_mv1_to_exif.matcher import FrameMatch, match_frames_to_tiffs
from nikon_mv1_to_exif.metadata_dialog import MetadataDialog
from nikon_mv1_to_exif.parser import parse_mv1_file
from nikon_mv1_to_exif.processor import ProcessResult, process_mv1_folder
from nikon_mv1_to_exif.styles import DARK_STYLESHEET


class ProcessWorker(QThread):
    finished = pyqtSignal(object, object, object)
    failed = pyqtSignal(str)

    def __init__(
        self,
        mv1_path: Path,
        tiff_folder: Path,
        output_dir: Path | None,
        overwrite: bool,
    ) -> None:
        super().__init__()
        self.mv1_path = mv1_path
        self.tiff_folder = tiff_folder
        self.output_dir = output_dir
        self.overwrite = overwrite

    def run(self) -> None:
        try:
            result = process_mv1_folder(
                self.mv1_path,
                self.tiff_folder,
                output_dir=self.output_dir,
                overwrite=self.overwrite,
            )
            self.finished.emit(*result)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Nikon MV-1 to EXIF")
        self.resize(980, 720)
        self._worker: ProcessWorker | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Nikon MV-1 to EXIF")
        title.setObjectName("titleLabel")
        subtitle = QLabel(
            "Apply exposure, date, and camera metadata from an MV-1 text file to scanned TIFF images."
        )
        subtitle.setObjectName("subtitleLabel")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        inputs_group = QGroupBox("Inputs")
        inputs_layout = QVBoxLayout(inputs_group)

        self.mv1_edit = QLineEdit()
        self.mv1_edit.setPlaceholderText("Select MV-1 text file (e.g. n00032.txt)")
        mv1_row = self._file_row(self.mv1_edit, self._browse_mv1)
        inputs_layout.addLayout(mv1_row)

        self.tiff_edit = QLineEdit()
        self.tiff_edit.setPlaceholderText("Select folder containing TIFF scans")
        tiff_row = self._file_row(self.tiff_edit, self._browse_tiff_folder)
        inputs_layout.addLayout(tiff_row)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText(
            "Optional output folder (leave empty to update TIFFs in place)"
        )
        output_row = self._file_row(self.output_edit, self._browse_output_folder)
        inputs_layout.addLayout(output_row)

        self.overwrite_check = QCheckBox("Overwrite existing output files")
        self.overwrite_check.setChecked(True)
        inputs_layout.addWidget(self.overwrite_check)

        layout.addWidget(inputs_group)

        actions_row = QHBoxLayout()
        self.preview_button = QPushButton("Preview Matches")
        self.preview_button.clicked.connect(self.preview_matches)
        self.process_button = QPushButton("Apply EXIF")
        self.process_button.setObjectName("primaryButton")
        self.process_button.clicked.connect(self.start_processing)
        self.view_metadata_button = QPushButton("View TIFF Metadata…")
        self.view_metadata_button.clicked.connect(self.view_tiff_metadata)
        actions_row.addWidget(self.preview_button)
        actions_row.addWidget(self.process_button)
        actions_row.addWidget(self.view_metadata_button)
        actions_row.addStretch()
        layout.addLayout(actions_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        preview_group = QGroupBox("Frame Matching Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Frame", "Date/Time", "Exposure", "TIFF File", "Match Method"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        preview_layout.addWidget(self.table)
        layout.addWidget(preview_group, stretch=2)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        log_layout.addWidget(self.log)
        layout.addWidget(log_group, stretch=1)

    def _file_row(self, line_edit: QLineEdit, browse_handler) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(line_edit, stretch=1)
        browse_button = QPushButton("Browse…")
        browse_button.clicked.connect(browse_handler)
        row.addWidget(browse_button)
        return row

    def _browse_mv1(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MV-1 file",
            "",
            "MV-1 files (*.txt);;All files (*.*)",
        )
        if path:
            self.mv1_edit.setText(path)

    def _browse_tiff_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select TIFF folder")
        if path:
            self.tiff_edit.setText(path)

    def _browse_output_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select output folder")
        if path:
            self.output_edit.setText(path)

    def _validate_inputs(self) -> tuple[Path, Path, Path | None] | None:
        mv1_path = Path(self.mv1_edit.text().strip())
        tiff_folder = Path(self.tiff_edit.text().strip())
        output_text = self.output_edit.text().strip()
        output_dir = Path(output_text) if output_text else None

        if not mv1_path.is_file():
            QMessageBox.warning(self, "Missing file", "Please select a valid MV-1 text file.")
            return None
        if not tiff_folder.is_dir():
            QMessageBox.warning(self, "Missing folder", "Please select a valid TIFF folder.")
            return None
        if output_dir is not None and output_dir.exists() and not output_dir.is_dir():
            QMessageBox.warning(self, "Invalid output", "The output path must be a folder.")
            return None
        return mv1_path, tiff_folder, output_dir

    def _append_log(self, message: str) -> None:
        self.log.append(message)

    def _set_busy(self, busy: bool) -> None:
        self.preview_button.setEnabled(not busy)
        self.process_button.setEnabled(not busy)
        self.view_metadata_button.setEnabled(not busy)
        self.progress.setValue(0 if busy else self.progress.value())

    def view_tiff_metadata(self) -> None:
        dialog = MetadataDialog(self)
        dialog.exec()

    def preview_matches(self) -> None:
        validated = self._validate_inputs()
        if validated is None:
            return
        mv1_path, tiff_folder, _ = validated
        try:
            data = parse_mv1_file(mv1_path)
            matches = match_frames_to_tiffs(data, tiff_folder)
            self._populate_table(matches)
            matched = sum(1 for match in matches if match.tiff_path is not None)
            self._append_log(
                f"Preview: {matched}/{len(matches)} frames matched in {tiff_folder}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Preview failed", str(exc))

    def _populate_table(self, matches: list[FrameMatch]) -> None:
        self.table.setRowCount(len(matches))
        for row, match in enumerate(matches):
            frame = match.frame
            exposure = f"1/{frame.shutter_speed} {frame.aperture} {frame.focal_length}mm"
            datetime_text = f"{frame.date} {frame.time}"
            tiff_name = match.tiff_path.name if match.tiff_path else "—"
            values = [
                f"{frame.frame_number:02d}",
                datetime_text,
                exposure,
                tiff_name,
                match.match_method,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if match.tiff_path is None:
                    item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, column, item)

    def start_processing(self) -> None:
        validated = self._validate_inputs()
        if validated is None:
            return
        mv1_path, tiff_folder, output_dir = validated
        self._set_busy(True)
        self._append_log("Processing started…")
        self._worker = ProcessWorker(
            mv1_path,
            tiff_folder,
            output_dir,
            self.overwrite_check.isChecked(),
        )
        self._worker.finished.connect(self._on_process_finished)
        self._worker.failed.connect(self._on_process_failed)
        self._worker.start()

    def _on_process_finished(self, data, matches, results) -> None:
        self._populate_table(matches)
        success_count = sum(1 for result in results if result.success)
        self.progress.setValue(100)
        for result in results:
            status = "OK" if result.success else "FAIL"
            self._append_log(
                f"[{status}] Frame {result.frame_number:02d}: {result.message}"
            )
        self._append_log(f"Done. {success_count}/{len(results)} files updated.")
        self._set_busy(False)
        QMessageBox.information(
            self,
            "Processing complete",
            f"Updated {success_count} of {len(results)} frames.",
        )

    def _on_process_failed(self, message: str) -> None:
        self._set_busy(False)
        self._append_log(f"ERROR: {message}")
        QMessageBox.critical(self, "Processing failed", message)


def run_app() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLESHEET)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run_app())
