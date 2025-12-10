
# -*- coding: utf-8 -*-
__title__ = "Wall Layer Info + UI Preview"
__doc__   = "Shows a small UI with the wall type preview and layer properties"

import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

# WinForms & Drawing references
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

import System
from System import Environment
from System.Drawing import Size, Color, Font, FontStyle
from System.Windows.Forms import (
    Form, PictureBox, ListView, ColumnHeader, Button,
    Label, DockStyle, ListViewItem, BorderStyle, View,
    Padding, SaveFileDialog, FormStartPosition, MessageBox,
    DialogResult
)

# Revit handles
uidoc = __revit__.ActiveUIDocument
doc   = uidoc.Document


# ---------------------------
# Helpers
# ---------------------------
def to_cm(internal_feet_value):
    """Convert Revit internal feet to centimeters (Revit 2026 UnitTypeId)."""
    return UnitUtils.ConvertFromInternalUnits(internal_feet_value, UnitTypeId.Centimeters)

def get_type_name(el_type):
    """Robustly get the element type's name."""
    from Autodesk.Revit.DB import BuiltInParameter
    if el_type is None:
        return u"—"
    # Try CLR property first
    try:
        return el_type.Name
    except:
        pass
    # Fallback to built-in parameter
    try:
        p = el_type.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM)
        if p:
            s = p.AsString()
            if s:
                return s
    except:
        pass
    # Last resort: Id
    try:
        return str(el_type.Id.IntegerValue)
    except:
        return u"Unknown Type"

def pick_element_and_get_type():
    """Pick an element and return its ElementType (or None)."""
    try:
        ref = uidoc.Selection.PickObject(ObjectType.Element)
    except Exception:
        return None
    element = doc.GetElement(ref)
    if element is None:
        return None
    type_id = element.GetTypeId()
    el_type = doc.GetElement(type_id)
    return el_type

def get_compound_layers(el_type):
    """Return (material_name, width_cm, function_name) for the type's compound structure."""
    structure = el_type.GetCompoundStructure()
    if not structure:
        return []
    rows = []
    for layer in structure.GetLayers():
        # Material
        mat_id = layer.MaterialId
        mat = doc.GetElement(mat_id)
        mat_name = mat.Name if mat else "<No Material>"
        # Width (cm)
        width_cm = to_cm(layer.Width)
        # Function
        fun_name = layer.Function.ToString()
        rows.append((mat_name, width_cm, fun_name))
    return rows

def get_type_preview_bitmap(el_type, size_px=512):
    """Get a System.Drawing.Bitmap preview for the element type, if available."""
    try:
        sz = Size(size_px, size_px)
        bmp = el_type.GetPreviewImage(sz)
        return bmp
    except:
        return None


# ---------------------------
# Windows Forms UI
# ---------------------------
class WallInfoForm(Form):
    def __init__(self, el_type, rows, preview_bmp):
        Form.__init__(self)
        self.Text = "Wall Type Info"
        self.BackColor = Color.FromArgb(248, 248, 248)
        self.Padding = Padding(10)
        self.StartPosition = FormStartPosition.CenterScreen
        self.Width, self.Height = 820, 600

        # Title
        self.lblTitle = Label()
        self.lblTitle.Text = "Type: {}".format(get_type_name(el_type))
        self.lblTitle.Font = Font("Segoe UI", 11, FontStyle.Bold)
        self.lblTitle.AutoSize = True
        self.lblTitle.Dock = DockStyle.Top
        self.Controls.Add(self.lblTitle)

        # Preview (left)
        self.pic = PictureBox()
        self.pic.Width, self.pic.Height = 512, 512
        self.pic.BorderStyle = BorderStyle.FixedSingle
        self.pic.BackColor = Color.White
        if preview_bmp:
            self.pic.Image = preview_bmp
        self.pic.Top, self.pic.Left = 40, 10
        self.Controls.Add(self.pic)

        # Layers list (right)
        self.lv = ListView()
        self.lv.View = View.Details
        self.lv.FullRowSelect = True
        self.lv.GridLines = True
        self.lv.Width, self.lv.Height = 260, 512
        self.lv.Top, self.lv.Left = 40, self.pic.Right + 10

        # Columns — add individually (simpler & IronPython-safe)
        self.colMat = ColumnHeader();  self.colMat.Text = "Material";    self.colMat.Width = 130
        self.colWidth = ColumnHeader(); self.colWidth.Text = "Width (cm)"; self.colWidth.Width = 80
        self.colFun = ColumnHeader();   self.colFun.Text = "Function";    self.colFun.Width = 80
        self.lv.Columns.Add(self.colMat)
        self.lv.Columns.Add(self.colWidth)
        self.lv.Columns.Add(self.colFun)

        # Rows
        if rows:
            for (mat_name, width_cm, fun_name) in rows:
                item = ListViewItem(mat_name)
                item.SubItems.Add("{:.2f}".format(width_cm))
                item.SubItems.Add(fun_name)
                self.lv.Items.Add(item)
        else:
            item = ListViewItem("No compound layers"); item.SubItems.Add(""); item.SubItems.Add("")
            self.lv.Items.Add(item)

        self.Controls.Add(self.lv)

        # Buttons
        self.btnExport = Button()
        self.btnExport.Text = "Export Preview…"
        self.btnExport.Width = 140
        self.btnExport.Top, self.btnExport.Left = self.pic.Bottom + 10, 10
        self.btnExport.Click += self._on_export
        self.Controls.Add(self.btnExport)

        self.btnClose = Button()
        self.btnClose.Text = "Close"
        self.btnClose.Width = 100
        self.btnClose.Top, self.btnClose.Left = self.pic.Bottom + 10, self.btnExport.Right + 10
        self.btnClose.Click += self._on_close
        self.Controls.Add(self.btnClose)

        self._bmp = preview_bmp

    def _on_export(self, sender, args):
        if not self._bmp:
            MessageBox.Show("No preview image available.", "Export Preview")
            return
        sfd = SaveFileDialog()
        sfd.Title = "Save Preview PNG"
        sfd.Filter = "PNG Image (*.png)|*.png"
        sfd.InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments)
        sfd.FileName = "WallTypePreview.png"
        if sfd.ShowDialog() == DialogResult.OK:
            try:
                self._bmp.Save(sfd.FileName)
                MessageBox.Show("Saved:\n{}".format(sfd.FileName), "Export Preview")
            except Exception as e:
                MessageBox.Show("Error saving preview:\n{}".format(e), "Export Preview")

    def _on_close(self, sender, args):
        self.Close()


# ---------------------------
# Entry point
# ---------------------------
def main():
    el_type = pick_element_and_get_type()
    if el_type is None:
        MessageBox.Show("Selection canceled or invalid element.", "Wall Type Info")
        return

    rows = []
    try:
        rows = get_compound_layers(el_type)
    except Exception as e:
        MessageBox.Show("Could not read compound layers:\n{}".format(e), "Wall Type Info")

    try:
        preview_bmp = get_type_preview_bitmap(el_type, 512)
    except:
        preview_bmp = None

    WallInfoForm(el_type, rows, preview_bmp).ShowDialog()

if __name__ == "__main__":
    main()
