from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit, QListWidget,
    QRadioButton)


class FindDialog(QDialog):
    alphabetical = [
        dict(type="alphabetical", allowPseudoUnicode=True)
    ]

    def __init__(self, currentGlyph, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(self.tr("Find…"))
        self._sortedGlyphNames = currentGlyph.font.unicodeData.sortGlyphNames(
            currentGlyph.layer.keys(), self.alphabetical)

        layout = QGridLayout(self)
        self.glyphLabel = QLabel(self.tr("Glyph:"), self)
        self.glyphEdit = QLineEdit(self)
        self.glyphEdit.textChanged.connect(self.updateGlyphList)
        self.glyphEdit.event = self.lineEvent
        self.glyphEdit.keyPressEvent = self.lineKeyPressEvent

        self.beginsWithBox = QRadioButton(self.tr("Begins with"), self)
        self.containsBox = QRadioButton(self.tr("Contains"), self)
        self.beginsWithBox.setChecked(True)
        self.beginsWithBox.toggled.connect(self.updateGlyphList)

        self.glyphList = QListWidget(self)
        self.glyphList.itemDoubleClicked.connect(self.accept)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        l = 0
        layout.addWidget(self.glyphLabel, l, 0, 1, 2)
        layout.addWidget(self.glyphEdit, l, 2, 1, 4)
        l += 1
        layout.addWidget(self.beginsWithBox, l, 0, 1, 3)
        layout.addWidget(self.containsBox, l, 3, 1, 3)
        l += 1
        layout.addWidget(self.glyphList, l, 0, 1, 6)
        l += 1
        layout.addWidget(buttonBox, l, 0, 1, 6)
        self.setLayout(layout)
        self.updateGlyphList()

    def lineEvent(self, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            if self.beginsWithBox.isChecked():
                self.containsBox.toggle()
            else:
                self.beginsWithBox.toggle()
            return True
        else:
            return QLineEdit.event(self.glyphEdit, event)

    def lineKeyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up or key == Qt.Key_Down:
            self.glyphList.keyPressEvent(event)
        else:
            QLineEdit.keyPressEvent(self.glyphEdit, event)

    def updateGlyphList(self):
        beginsWith = self.beginsWithBox.isChecked()
        self.glyphList.clear()
        if not self.glyphEdit.isModified():
            self.glyphList.addItems(self._sortedGlyphNames)
        else:
            text = self.glyphEdit.text()
            if beginsWith:
                glyphs = [glyphName for glyphName in self._sortedGlyphNames
                          if glyphName and glyphName.startswith(text)]
            else:
                glyphs = [glyphName for glyphName in self._sortedGlyphNames
                          if glyphName and text in glyphName]
            self.glyphList.addItems(glyphs)
        self.glyphList.setCurrentRow(0)

    @classmethod
    def getNewGlyph(cls, parent, currentGlyph):
        dialog = cls(currentGlyph, parent)
        result = dialog.exec_()
        currentItem = dialog.glyphList.currentItem()
        newGlyph = None
        if currentItem is not None:
            newGlyphName = currentItem.text()
            if newGlyphName in currentGlyph.layer:
                newGlyph = currentGlyph.layer[newGlyphName]
        return (newGlyph, result)


class AddComponentDialog(FindDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("Add component…"))
        self._sortedGlyphNames.remove(args[0].name)
        self.updateGlyphList()


class LayerActionsDialog(QDialog):

    def __init__(self, currentGlyph, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(self.tr("Layer actions…"))
        self._workableLayers = []
        for layer in currentGlyph.layerSet:
            if layer != currentGlyph.layer:
                self._workableLayers.append(layer)

        copyBox = QRadioButton(self.tr("Copy"), self)
        moveBox = QRadioButton(self.tr("Move"), self)
        swapBox = QRadioButton(self.tr("Swap"), self)
        self.otherCheckBoxes = (moveBox, swapBox)
        copyBox.setChecked(True)

        self.layersList = QListWidget(self)
        self.layersList.addItems(
            layer.name for layer in self._workableLayers)
        if self.layersList.count():
            self.layersList.setCurrentRow(0)
        self.layersList.itemDoubleClicked.connect(self.accept)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QGridLayout(self)
        l = 0
        layout.addWidget(copyBox, l, 0, 1, 2)
        layout.addWidget(moveBox, l, 2, 1, 2)
        layout.addWidget(swapBox, l, 4, 1, 2)
        l += 1
        layout.addWidget(self.layersList, l, 0, 1, 6)
        l += 1
        layout.addWidget(buttonBox, l, 0, 1, 6)
        self.setLayout(layout)

    @classmethod
    def getLayerAndAction(cls, parent, currentGlyph):
        dialog = cls(currentGlyph, parent)
        result = dialog.exec_()
        currentItem = dialog.layersList.currentItem()
        newLayer = None
        if currentItem is not None:
            newLayerName = currentItem.text()
            for layer in dialog._workableLayers:
                if layer.name == newLayerName:
                    newLayer = layer
        action = "Copy"
        for checkBox in dialog.otherCheckBoxes:
            if checkBox.isChecked():
                action = checkBox.text()
        return (newLayer, action, result)


class RenameDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowTitle(self.tr("Rename…"))

        nameLabel = QLabel(self.tr("Name:"), self)
        self.nameEdit = QLineEdit(self)
        self.nameEdit.setFocus(Qt.OtherFocusReason)

        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QGridLayout(self)
        l = 0
        layout.addWidget(nameLabel, l, 0)
        layout.addWidget(self.nameEdit, l, 1, 1, 3)
        l += 1
        layout.addWidget(buttonBox, l, 3)
        self.setLayout(layout)

    @classmethod
    def getNewName(cls, parent, name=None):
        dialog = cls(parent)
        dialog.nameEdit.setText(name)
        dialog.nameEdit.selectAll()
        result = dialog.exec_()
        name = dialog.nameEdit.text()
        return (name, result)
