import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitServices")

from Autodesk.Revit.DB import Transaction, ElementId, FamilyInstance

doc = __revit__.ActiveUIDocument.Document

# Cutter and target IDs
CUTTER_IDS = [3226674,3226675]
TARGET_IDS = [3226676,3226677,3226678,3226679,3226680,3226681,3226682,3226683,3226684,3226685,3226686,3226687,3226688,3226689
    ,3226690,3226691,3226692,3226693,3226694,3226695,3226696,3226697,3226698,3226699,3226700,3226701,3226702,3226703,3226704,3226705,3226706,3226707,3226708
]


# Get elements
cutters = [doc.GetElement(ElementId(i)) for i in CUTTER_IDS if doc.GetElement(ElementId(i)) is not None]
targets = [doc.GetElement(ElementId(i)) for i in TARGET_IDS if doc.GetElement(ElementId(i)) is not None]

print("Cutters found: {}".format([c.Id.IntegerValue for c in cutters]))
print("Targets found: {}".format([t.Id.IntegerValue for t in targets]))

# Start transaction
t = Transaction(doc, "Apply Beam Coping")
t.Start()

results = []

try:
    for target in targets:
        # Check if element has AddCoping method
        if not hasattr(target, "AddCoping"):
            print("Target {} cannot be coped".format(target.Id.IntegerValue))
            results.append((target.Id.IntegerValue, None, "Cannot cope"))
            continue

        for cutter in cutters:
            if not hasattr(cutter, "AddCoping") and not isinstance(cutter, FamilyInstance):
                print("Cutter {} cannot be used for coping".format(cutter.Id.IntegerValue))
                results.append((target.Id.IntegerValue, cutter.Id.IntegerValue, "Cutter invalid"))
                continue

            try:
                print("Applying coping: {} -> {}".format(target.Id.IntegerValue, cutter.Id.IntegerValue))
                target.AddCoping(cutter)
                results.append((target.Id.IntegerValue, cutter.Id.IntegerValue, "Success"))
            except Exception as e:
                print("Failed coping: {} -> {} : {}".format(target.Id.IntegerValue, cutter.Id.IntegerValue, e))
                results.append((target.Id.IntegerValue, cutter.Id.IntegerValue, "Failed: {}".format(e)))
finally:
    t.Commit()
    print("Transaction committed.")

OUT = results
print("Total coping attempts: {}".format(len(results)))
