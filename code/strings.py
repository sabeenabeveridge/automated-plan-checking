''' strings Module - A collection of commonly used strings throughout the project

Why have this module?:
- Standardise string format: e.g. <"10x12" vs "10 x 12"> 
    Although they both look reasonable, format must be consistent throughout the project for equality comparisons.
- Easier changes: If a string were to be changed, it can be done with one change in this file.
- More descriptive variable names to add meaning to symbolic strings e.g '-' which accept any value can be called ANY_VALUE
'''

# Parameters
case = "case"
mode = "mode"
prescription_dose = "prescription dose/#"
prescription_point = "prescription point"
isocenter_point = "isocentre point"
override = "override"
collimator = "collimator"
gantry = "gantry"
SSD = "SSD"
couch = "couch"
field_size = "field size"
wedge = "wedge"
meas = "meas"
energy = "energy"

# Parameter values (which are directly used in code)
ANY_SSD = "?" # In truth table, SSD sometimes in the format "?,89,93,89,?" with "?" accepting any value
TRUTH_TABLE_ERROR = "Error: Check truth table format"
VMAT = "VMAT"
not_VMAT = "not VMAT"
IMRT = "IMRT"
VMAT_unknown = "VMAT unknown"
SETUP_beam = "SETUP beam"
no_wedge = "no wedge"
STANDARD_FLUENCE = "STANDARD" # When fluence mode is listed as "STANDARD" in dicom, it is not FFF
FFF = "FFF"
ANY_VALUE = "-" # Truth table uses hyphen to denote any value is acceptable
FAIL = "FAIL"
PASS = "PASS"
NOT_IMPLEMENTED= "NOT IMPLEMENTED"
NOT_APPLICABLE = "NOT APPLICABLE"
Not_Extracted = "Not Extracted"