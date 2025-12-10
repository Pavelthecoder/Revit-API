# -*- coding: utf-8 -*-
import clr
clr.AddReference("RevitAPI")

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import StructuralFramingUtils

# Current Revit document
doc = __revit__.ActiveUIDocument.Document

# Beam IDs you want to process
BEAM_IDS = [
    3225855, 3225856, 3225857, 3225858, 3225859, 3225860, 3225861,
    3225862, 3225863, 3225864, 3225865, 3225866, 3225867, 3225868,
    3225869, 3225870, 3225871, 3225872, 3225873, 3225874, 3225875,
    3225876, 3225877, 3226061, 3226062, 3226063, 3226064, 3226065,
    3226066, 3226067, 3226068, 3226069, 3226070, 3226071, 3226072
]

# Convert IDs into elements
beams = [doc.GetElement(ElementId(i)) for i in BEAM_IDS]

# Start transaction
t = Transaction(doc, "Disallow Beam Joins")
t.Start()

results = []
for beam in beams:
    if isinstance(beam, FamilyInstance):
        try:
            StructuralFramingUtils.DisallowJoinAtEnd(beam, 0)  # start
            StructuralFramingUtils.DisallowJoinAtEnd(beam, 1)  # end
            results.append("Disallowed joins for beam: {}".format(beam.Id))
        except Exception as e:
            results.append("Failed on {}: {}".format(beam.Id, e))
    else:
        results.append("Element {} is not a beam".format(beam.Id))

t.Commit()

# Print to pyRevit console
for r in results:
    print(r)
