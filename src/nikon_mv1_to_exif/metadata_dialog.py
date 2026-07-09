"""Dialog for viewing TIFF EXIF and XMP metadata."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from nikon_mv1_to_exif.metadata_reader import TiffMetadata, read_metadata_from_tiff


class MetadataDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TIFF Metadata Viewer")
        self.resize(820, 620)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Select a TIFF file to inspect its EXIF and XMP metadata.")
        header.setWordWrap(True)
        layout.addWidget(header)

        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        browse_button = QPushButton("Choose TIFF…")
        browse_button.clicked.connect(self._browse_tiff)
        file_row.addWidget(self.file_label, stretch=1)
        file_row.addWidget(browse_button)
        layout.addLayout(file_row)

        self.tabs = QTabWidget()
        self.exif_table = self._create_metadata_table()
        self.xmp_table = self._create_metadata_table()
        self.tabs.addTab(self.exif_table, "EXIF")
        self.tabs.addTab(self.xmp_table, "XMP")
        layout.addWidget(self.tabs, stretch=1)

        self.summary_label = QLabel("")
        self.summary_label.setObjectName("subtitleLabel")
        layout.addWidget(self.summary_label)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_metadata_table(self) -> QTableWidget:
        table = QTableWidget(0, 2)
        table.setHorizontalHeaderLabels(["Tag", "Value"])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        table.setColumnWidth(0, 280)
        return table

    def _browse_tiff(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TIFF file",
            "",
            "TIFF files (*.tif *.tiff);;All files (*.*)",
        )
        if not path:
            return
        self.show_metadata_for_file(Path(path))

    def show_metadata_for_file(self, tiff_path: Path) -> None:
        try:
            metadata = read_metadata_from_tiff(tiff_path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Could not read metadata",
                f"Failed to read metadata from:\n{tiff_path}\n\n{exc}",
            )
            return

        self.file_label.setText(str(tiff_path))
        self._populate_table(self.exif_table, metadata.exif)
        self._populate_table(self.xmp_table, metadata.xmp)
        self.summary_label.setText(
            f"EXIF tags: {len(metadata.exif)} | XMP tags: {len(metadata.xmp)}"
        )
        self.tabs.setTabText(0, f"EXIF ({len(metadata.exif)})")
        self.tabs.setTabText(1, f"XMP ({len(metadata.xmp)})")

    def _populate_table(self, table: QTableWidget, tags: dict[str, str]) -> None:
        table.setRowCount(len(tags))
        for row, (tag, value) in enumerate(tags.items()):
            tag_item = QTableWidgetItem(tag)
            value_item = QTableWidgetItem(value)
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, tag_item)
            table.setItem(row, 1, value_item)


def open_metadata_viewer(parent: QWidget | None = None) -> None:
    """Open the metadata viewer dialog."""
    dialog = MetadataDialog(parent)
    dialog.exec()
