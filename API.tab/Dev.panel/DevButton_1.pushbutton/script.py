# -*- coding: utf-8 -*-
__title__   = "START"

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import Selection
from Autodesk.Revit.DB.Architecture import Room

app    = __revit__.Application
uidoc  = __revit__.ActiveUIDocument
doc    = __revit__.ActiveUIDocument.Document #type:Document

selection = uidoc.Selection #type: Selection
#selected_elements = selection.GetElementIds()

#for e_id in selected_elements:
#    e = doc.GetElement(e_id)
#    print(e_id, e)
#
#    if type(e) == Room:
#        print ("room")
#    elif type(e) == Wall:
#        print ("wall")

selected_elements = selection.PickElementsByRectangle("abcdef")
print (selected_elements)



