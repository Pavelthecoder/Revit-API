# -*- coding: utf-8 -*-
__title__   = ("Wall Layer Info + Preview Export")
__doc__     = """Version = 1.0 """

import clr
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import ObjectType

clr.AddReference("System.Drawing")
import System
from System.Drawing import Bitmap
from System.IO import FileStream, FileMode

uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document

# ----------------------------------------------------------
# 1) Pick element
# ----------------------------------------------------------
ref = uidoc.Selection.PickObject(ObjectType.Element)
element = doc.GetElement(ref)

# Get its WallType (ElementType)
type_id = element.GetTypeId()
el_type = doc.GetElement(type_id)

# ----------------------------------------------------------
# 2) Read compound structure layers
# ----------------------------------------------------------
structure = el_type.GetCompoundStructure()
layers = structure.GetLayers()

print("\n=== WALL LAYERS ===\n")

for layer in layers:
    mat_id = layer.MaterialId
    mat = doc.GetElement(mat_id)
    mat_name = mat.Name if mat else "<No Material>"

    # Layer function
    fun_enum = layer.Function
    fun_name = fun_enum.ToString()

    # Width
    width_ft = layer.Width
    width_cm = UnitUtils.ConvertFromInternalUnits(width_ft, UnitTypeId.Centimeters)

    print("Material: {:<25}  Width: {:>6.2f} cm  Function: {}".format(
          mat_name, width_cm, fun_name))

# ----------------------------------------------------------
# 3) Export wall type preview image
# ----------------------------------------------------------
try:
    size = System.Drawing.Size(512, 512)
    preview = el_type.GetPreviewImage(size)

    if preview:
        output_path = r"C:\Users\pavel\Documents\WallTypePreview.png"
        preview.Save(output_path)
        print("\nPreview image exported to:")
        print(output_path)
    else:
        print("\nNo preview image available for this element type.")

except Exception as e:
    print("\nERROR exporting preview:", e)
