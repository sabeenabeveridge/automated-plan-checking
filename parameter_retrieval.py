"""
The function to extract parameters from the specified DICOM file.
"""

# We import the pydicom library to use it's DICOM reading methods
import pydicom as dicom

# TODO investigate whther it's ok to just look for the first item of the sequences
first_sequence_item = 0

def main():
    extract_parameters("./Documents/Input/YellowLvlIII_7a.dcm",6)

def extract_parameters(filepath, case):
    dataset = dicom.read_file(filepath, force=True)
    # print(dataset)
    
    parameters = ['mode req', 'prescription dose/#', 'prescription point', 'isocentre point', 'override', 'collimator',
                  'gantry', 'SSD', 'couch', 'field size', 'wedge', 'meas', 'energy']
    parameter_values = {'mode req': '', 'prescription dose/#': '', 'prescription point': '', 'isocentre point': '',
                        'override': '', 'collimator': '', 'gantry': '', 'SSD': '', 'couch': '', 'field size': '',
                        'wedge': '', 'meas': '', 'energy': ''}

    file_type = ''
    ssd_list = []

    ## Number of Beams
    i = 0
    while i < len(dataset.BeamSequence):
        if dataset.BeamSequence[i].BeamDescription != "SETUP beam":

            # WRITE code for mode_req parameter here:

            # Total Prescription Dose
            # We still need to figure out how to format so we can check it against truth table
            total_prescription_dose = str(int(dataset.DoseReferenceSequence[0].TargetPrescriptionDose))

            # number of fractions
            number_of_fractions = str(dataset.FractionGroupSequence[0].NumberOfFractionsPlanned)

            # WRITE code for perscription_point parameter here:

            # WRITE code for isocentre_point parameter here:
            # Isocenter Position TODO:Figuring out what does "SoftTiss" etc means
            # parameter_values["Isocenter Position"] = dataset.BeamSequence[i].ControlPointSequence[0].IsocenterPosition

            # WRITE code for override parameter here:
            # I suspect override is at (3008, 0066)

            # WRITE code for collimator parameter here:         TODO:according to Andrew it seems should be Beam Limiting Device Angle
            parameter_values['collimator'] = str(
                int(dataset.BeamSequence[i].ControlPointSequence[0].BeamLimitingDeviceAngle))

            ## GantryAngle
            try:
                if int(dataset.BeamSequence[i].ControlPointSequence[0].GantryAngle) != int(
                        dataset.BeamSequence[i].ControlPointSequence[1].GantryAngle):
                    parameter_values['gantry'] = 'VMAT File'
                    file_type = 'VMAT'
                else:
                    gantry_instance = str(int(dataset.BeamSequence[i].ControlPointSequence[0].GantryAngle))
                    if parameter_values['gantry'] == '':
                        parameter_values['gantry'] = gantry_instance
                    else:
                        parameter_values['gantry'] += "," + gantry_instance
            except:
                parameter_values['gantry'] = '-'

            # SSD in centimetres
            try:
                ssd_instance = dataset.BeamSequence[i].ControlPointSequence[0].SourceToSurfaceDistance / 10
                ssd_list.append(ssd_instance)
            except:
                parameter_values['SSD'] = '-'

            # WRITE code for couch parameter here:

            # WRITE code for field size parameter here:

            # can't figure out how to find wedge angle unless there are no wedges
            # the tag is (300a,00D5) for wedge angle or (0014,5107)
            num_wedges = int(dataset.BeamSequence[i].NumberOfWedges)
            if parameter_values['wedge'] == '':
                if num_wedges == 0:
                    parameter_values['wedge'] += '0'
                elif num_wedges == 1:
                    parameter_values['wedge'] += str(int(dataset.BeamSequence[0].WedgeSequence[0].WedgeAngle))
            else:
                if num_wedges == 0:
                    parameter_values['wedge'] += ',0'
                elif num_wedges == 1:
                    parameter_values['wedge'] += ',' + str(int(dataset.BeamSequence[0].WedgeSequence[0].WedgeAngle))
            # write an else statement for cases where wedge angles exist

            # WRITE code for meas parameter here:

            #TODO extra LVL3 files given by client are still showing all STANDARD; need to confirm that one of them really 
            #      is meant to be FFF so we can say this parameter is a bust or some other method is required.
            # Nominal Beam Energy (MV) + Fluence Mode(STANDARD/NONSTANDARD)
            parameter_values["energy"] = dataset.BeamSequence[i].ControlPointSequence[first_sequence_item].NominalBeamEnergy
            # Fluence Mode, which may indicate if dose is Flattening Filter Free (but might not! DICOM standard defines it as optional)
            #  -STANDARD     -> not FFF
            #  -NON_STANDARD -> check Fluence Mode ID for a short description of the fluence mode (could be FFF)
            if dataset.BeamSequence[i].PrimaryFluenceModeSequence[first_sequence_item].FluenceMode != 'STANDARD':
                parameter_values["energy"] += dataset.BeamSequence[i].PrimaryFluenceModeSequence[first_sequence_item].FluenceModeID

            # The monitor units is:
            # dataset.FractionGroupSequence[0].ReferencedBeamSequence[i].BeamMeterset

        i += 1

    # print(parameter_values)

    if len(ssd_list) > 0:
        if len(ssd_list) == 1:
            if abs(ssd_list[0] - 100) <= 1:
                parameter_values['SSD'] = '100'
            elif abs(ssd_list[0] - 86) <= 1:
                parameter_values['SSD'] = '86'
            elif abs(ssd_list[0] - 93) <= 1:
                parameter_values['SSD'] = '93'
            elif abs(ssd_list[0] - 90) <= 1:
                parameter_values['SSD'] = '90'
            else:
                parameter_values['SSD'] = str(ssd_list[0])
        elif len(ssd_list) == 3:
            if abs(ssd_list[0] - 86) <= 1 and abs(ssd_list[1] - 93) <= 1 and abs(ssd_list[2] - 86) <= 1:
                parameter_values['SSD'] = '86,93,86'
            else:
                parameter_values['SSD'] = "non valid ssd"
        elif len(ssd_list) == 5:
            if abs(ssd_list[1] - 89) <= 1 and abs(ssd_list[2] - 93) <= 1 and abs(ssd_list[3] - 89) <= 1:
                parameter_values['SSD'] = '?,89,93,89,?'
            else:
                parameter_values['SSD'] = "non valid ssd"

    parameter_values['prescription dose/#'] = total_prescription_dose
    if total_prescription_dose == '24':
        parameter_values['prescription dose/#'] = '24/' + number_of_fractions
    elif total_prescription_dose == '48':
        parameter_values['prescription dose/#'] = '48/' + number_of_fractions
    elif total_prescription_dose == '50':
        parameter_values['prescription dose/#'] = '50/' + number_of_fractions
    elif total_prescription_dose == '900' and dataset.BeamSequence[0].PrimaryDosimeterUnit == 'MU':
        parameter_values['prescription dose/#'] = '900/' + number_of_fractions + ' MU'

    return parameter_values, file_type


def evaluate_parameters(parameters, case, file_type):

    truth_table_dict = {
        "case": ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17'],
        "mode req": ['False', 'False', 'False', 'False', 'False', 'True', 'True', 'True', 'False', 'True', 'True',
                     'True', 'True', 'True', 'True', 'True', 'True'],
        "prescription dose/#": ['2', '2', '2', '2', '50/25', '50/25', '50/25', '50/25', '900/3 MU', '45/3', '24/2',
                                '48/4', '3', '3', '20', '20', '20'],
        "prescription point": ['1 or 3', '5', '3', '3', 'chair', 'CShape', 'CShape', 'C8Target', '-', 'SoftTissTarget',
                               'SpineTarget', 'LungTarget', '1', '1', 'PTV_c14_c15', '-', '-'],
        "isocentre point": ['surf', '3', '3', '3', '3', '3', '3', '3', 'SoftTiss', 'SoftTiss', 'Spine', 'Lung', '1',
                            '1', '1', '-', '-'],
        "override": ['bone', 'no override', 'no override', 'no override', 'no override', 'lungs', 'no override',
                     'no override', 'lungs', 'lungs', 'no override', 'no override', 'central cube', 'central cube',
                     'central cube', 'central cube', 'central cube'],
        "collimator": ['0', '-', '-', '-', '0', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
        "gantry": ['0', '270,0,90', '90', '90', '0', '150,60,0,300,210', '150,60,0,300,210', '150,60,0,300,210', '-',
                   '-', '-', '-', '-', '-', '-', '-', '-'],
        "SSD": ['100', '86,93,86', '86', '86', '93', '?,89,93,89,?', '?,89,93,89,?', '?,89,93,89,?', '90', '-', '-',
                '-', '-', '-', '-', '-', '-'],
        'couch': ['-', '-', '-', '-', '-', 'couch?', 'couch?', 'couch?', '-', 'couch?', 'couch?', 'couch?', '-', '-',
                  'couch?', 'couch?', 'couch?'],
        'field size': ['10x10', '10x6,10x12,10x6', '10x12', '10x12', '-', '-', '-', '-', '3x3,2x2,1x1', '-', '-', '-',
                       '3x3', '1.5x1.5', '-', '-', '-'],
        'wedge': ['0', '30,0,30', '0', '60', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
        'meas': ["'1','3','10','-','-','-','-','-','-'",
                 "'5_RLAT','8_RLAT','5_AP','8_AP','5_LLAT','8_LLAT','-','-','-'", "'3','5','-','-','-','-','-','-','-'",
                 "'3','5','-','-','-','-','-','-','-'", "'11','12','13','14','15','18','19','20','21'",
                 "'11','12','13','14','15','16','17','-','-'", "'11','12','13','14','15','16','17','-','-'",
                 "'11','12','13','14','15','17','18','-','-'",
                 "'SoftTiss_3','SoftTiss_2','SoftTiss_1','-','-','-','-','-','-'",
                 "'SoftTiss','-','-','-','-','-','-','-','-'", "'Spine2Inf','Spine1Sup','Cord','-','-','-','-','-','-'",
                 "'Lung','-','-','-','-','-','-','-','-'", "'1_3','1_4','-','-','-','-','-','-','-'",
                 "'1_1.5','4_1.5','-','-','-','-','-','-','-'", "'1','3','-','-','-','-','-','-','-'",
                 "'1','3','-','-','-','-','-','-','-'", "'1','2','3','-','-','-','-','-','-'"],
        'energy': ["6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18",
                   "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18",
                   "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18",
                   "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18", "6,6FFF,10,10FFF,18",
                   "6,6FFF,10,10FFF,18"]}

    case = int(case)
    pass_fail_values = {}
    if case in range(1, 18):
        #print(case)
        for param in parameters:
            #print(param)
            if truth_table_dict[param][case - 1] == parameters[param] or truth_table_dict[param][
                case - 1] == '-' or (file_type == 'VMAT' and (param == 'gantry' or param == 'SSD')):
                pass_fail_values[param] = "PASS"
            else:
                if parameters[param] != '':
                    pass_fail_values[param] = "FAIL"
                else:
                    pass_fail_values[param] = truth_table_dict[param][case - 1]
    return pass_fail_values

if __name__ == "__main__":
    main() 