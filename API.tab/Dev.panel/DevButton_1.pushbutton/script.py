# -*- coding: utf-8 -*-
__title__ = "NEXT"
__doc__ = "Version = 1.0"

from Autodesk.Revit.DB import (
    BuiltInParameter, BuiltInCategory, IUpdater, UpdaterId, UpdaterRegistry,
    ElementCategoryFilter, ChangePriority, Element, ChangeType, FilteredElementCollector, ElementId,
    ParameterValueProvider, FilterDoubleRule, ElementParameterFilter, LogicalAndFilter, LogicalOrFilter
)
from Autodesk.Revit.DB import FilterNumericGreater, FilterNumericLess
from System import Guid

guid = Guid("355e2cde-11c1-1235-111d-99e9ef994b98")

doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
print("je to tam!")


class SimpleUpdater(IUpdater):
    def Execute(self, data):
        try:
            from Autodesk.Revit.DB import BuiltInParameter
            doc = __revit__.ActiveUIDocument.Document
            selection = __revit__.ActiveUIDocument.Selection

            if selection.GetElementIds():
                for element_id in selection.GetElementIds():
                    element = doc.GetElement(element_id)
                    view = doc.ActiveView
                    bounding_box = element.get_BoundingBox(view)
                    if not bounding_box:
                        continue

                    # Calculate elevation values (for display or additional use)
                    max_elevation = bounding_box.Max.Z
                    min_elevation = bounding_box.Min.Z
                    feets_to_meters_max = max_elevation * 0.3048
                    feets_to_meters_min = min_elevation * 0.3048
                    max_elevation_str = '{:.3f}'.format(feets_to_meters_max)
                    min_elevation_str = '{:.3f}'.format(feets_to_meters_min)

                    # Retrieve custom parameters and the built-in level parameter
                    elevation_ok_param = element.LookupParameter("Elevation_OK")
                    elevation_uk_param = element.LookupParameter("Elevation_UK")
                    uk_uber_ebene_param = element.LookupParameter("UK über Ebene")
                    level_param = element.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM)

                    print("BEFORE_uk_uber_ebene_param (m):", uk_uber_ebene_param.AsDouble() * 0.3048)
                    print("BEFORE_LEVEL_PARAM (m):", level_param.AsDouble() * 0.3048)

                    # Process only if level parameter is nonzero
                    if level_param.AsDouble() != 0:
                        # Compute new UK über Ebene value (both parameters are in feet; convert to meters for computation)
                        level_m = level_param.AsDouble() * 0.3048
                        uk_uber_ebene_m = uk_uber_ebene_param.AsDouble() * 0.3048
                        value_level_elev = level_m + uk_uber_ebene_m

                        # Update: set level parameter to 0 (marking as processed) and update UK über Ebene.
                        # Convert computed value back to feet when setting.
                        level_param.Set(0)
                        uk_uber_ebene_param.Set(value_level_elev / 0.3048)

                        print("After update - LEVEL_PARAM (m):", level_param.AsDouble() * 0.3048)
                        print("After update - uk_uber_ebene_param (m):", uk_uber_ebene_param.AsDouble() * 0.3048)
                        print("Computed value level elev (m):", value_level_elev)

                        if elevation_ok_param and elevation_uk_param:
                            elevation_ok_param.Set(max_elevation_str)
                            elevation_uk_param.Set(min_elevation_str)
                            print("Updated Element {}: Elevation_OK -> {} | Elevation_UK -> {}"
                                  .format(element.Id, max_elevation_str, min_elevation_str))
                        else:
                            print("Element {} is missing custom elevation parameters.".format(element.Id))
                    else:
                        print("Element {} already updated (level parameter is 0).".format(element.Id))
            else:
                print("No elements are currently selected.")

            print("Updater was triggered!")
        except Exception as e:
            print("Error in Execute method:", e)

    def GetUpdaterId(self):
        return self.updater_id

    def GetUpdaterName(self):
        return 'jbmnt123'

    def GetAdditionalInformation(self):
        return 'A simple updater for testing purposes'

    def GetChangePriority(self):
        return ChangePriority.Annotations

    def Initialize(self):
        pass

    def Uninitialize(self):
        pass


updater = SimpleUpdater()
updater_id = UpdaterId(app.ActiveAddInId, guid)
updater.updater_id = updater_id

# Create a ParameterValueProvider for the built-in level parameter
pvp = ParameterValueProvider(ElementId(BuiltInParameter.INSTANCE_ELEVATION_PARAM))

# Create a rule to allow elements with level > 0.001
positive_rule = FilterDoubleRule(pvp, FilterNumericGreater(), 0.001, 0.0001)
positive_filter = ElementParameterFilter(positive_rule)

# Create a rule to allow elements with level < -0.001
negative_rule = FilterDoubleRule(pvp, FilterNumericLess(), -0.001, 0.0001)
negative_filter = ElementParameterFilter(negative_rule)

# Combine the two filters using a Logical OR so that elements with |level| > 0.001 are allowed
from Autodesk.Revit.DB import LogicalOrFilter, LogicalAndFilter

combined_param_filter = LogicalOrFilter(positive_filter, negative_filter)

# Create a category filter for Generic Model elements
cat_filter = ElementCategoryFilter(BuiltInCategory.OST_GenericModel)

# Combine the category filter with the parameter filter using Logical AND
combined_filter = LogicalAndFilter(cat_filter, combined_param_filter)

if not UpdaterRegistry.IsUpdaterRegistered(updater_id, doc):
    UpdaterRegistry.RegisterUpdater(updater, doc)
    UpdaterRegistry.AddTrigger(updater_id, combined_filter, Element.GetChangeTypeGeometry())
