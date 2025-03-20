import numpy as np
import nibabel as nib
import string
import os
import sys
import argparse
import itertools as itt
from tabulate import tabulate
import pandas as pd
import subprocess
import xml.etree.ElementTree as ET


class color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    CBLACK = '\33[30m'
    CRED = '\33[31m'
    CGREEN = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE = '\33[36m'
    CWHITE = '\33[37m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def nifti_fields():
    """return dict with all field description from: https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h """
    fields = {'sizeof_hdr': 'int, MUST be 348',
              'data_type': 'char, ++UNUSED++',
              'db_name': 'char, ++UNUSED++',
              'extents': 'int, ++UNUSED++',
              'session_error': 'char, ++UNUSED++',
              'regular': 'char, ++UNUSED++',
              'dim_info': 'char, MRI slice ordering',
              'dim': 'short, Data array dimensions',
              'intent_p1': 'float, 1st intent parameter',
              'intent_p2': 'float, 2nd intent parameter',
              'intent_p3': 'float, 3rd intent parameter',
              'intent_code': 'short, NIFTI_INTENT_* code',
              'datatype': 'short, Defines data type!',
              'bitpix': 'short, Number bits/voxel',
              'slice_start': 'short, First slice index',
              'pixdim': 'float, Grid spacings',
              'vox_offset': 'float, Offset into .nii file',
              'scl_slope': 'float, Data scaling: slope',
              'scl_inter': 'float, Data scaling: offset',
              'slice_end': 'short, Last slice index',
              'slice_code': 'char, Slice timing order',
              'xyzt_units': 'char, Units of pixdim[1..4]',
              'cal_max': 'float, Max display intensity',
              'cal_min': 'float, Min display intensity',
              'slice_duration': 'float, Time for 1 slice',
              'toffset': 'float, Time axis shift',
              'glmax': 'int, ++UNUSED++',
              'glmin': 'int, ++UNUSED++',
              'descrip': 'char, any text you like',
              'aux_file': 'char, auxiliary filename',
              'qform_code': 'short, code{0:arbitrary,1:scanner,2:anatomical,3:talairach,4:MNI}',
              'sform_code': 'short, code{0:arbitrary,1:scanner,2:anatomical,3:talairach,4:MNI}',
              'quatern_b': 'float, Quaternion b param',
              'quatern_c': 'float, Quaternion c param',
              'quatern_d': 'float, Quaternion d param',
              'qoffset_x': 'float, Quaternion x shift',
              'qoffset_y': 'float, Quaternion y shift',
              'qoffset_z': 'float, Quaternion z shift',
              'srow_x': 'float, 1st row affine transform',
              'srow_y': 'float, 2st row affine transform',
              'srow_z': 'float, 3st row affine transform',
              'intent_name': "char, 'name' or meaning of data",
              'magic': 'char, MUST be "ni1\\0" or "n+1\\0"'}
    return fields

def compare_headers(*args):
    """
    Print sequentially compare all combinations of couples of headers, affine and header bytes
    INPUT: 2 or more images as str
    comp_bytes: Do header bytes comparison, default suppress
    """
    c = color
    list_df = []
    for im in args:
        # Run bash command and capture XML output
        bash_output = subprocess.check_output(f"fslhd -x {im}", text=True, shell=True)
        # Parse and process as above
        root = ET.fromstring(bash_output)
        data = {k: root.attrib[k] for k in root.attrib}
        df = pd.DataFrame(data, index=[os.path.basename(im)])
        list_df += [df]

    # concat dataframes
    merged_df = pd.concat(list_df, ignore_index=True)

    # drop similar columns
    df_cleaned = df.loc[:, df.nunique() > 1]

    # Print
    print(tabulate(merged_df, headers='keys', tablefmt='heavy_outline'))





    #for i, comb in enumerate(itt.combinations(args, 2)):
    #    hdr_0, aff_0, name_0 = dict(nib.load(comb[0]).header), nib.load(comb[0]).affine, os.path.basename(comb[0])
    #    hdr_1, aff_1, name_1 = dict(nib.load(comb[1]).header), nib.load(comb[1]).affine, os.path.basename(comb[1])
    #    hdr_ref = nifti_fields()

    #    print('-' * 10, f'Comparison {i}:', c.CBLUE, name_0, c.ENDC, '&', c.CRED, name_1, c.ENDC, '-' * 10)


        # Affine comparison
    #    if np.any(aff_0 != aff_1):
    #        print('\nAffine (rounded 4):\n')
    #        print(c.CBLUE, name_0, c.ENDC, '\n', aff_0.round(4))
    #        print(c.CRED, name_1, c.ENDC, '\n', aff_1.round(4))
    #        print(c.CGREEN, f'Difference {name_0} - {name_1}', c.ENDC, '\n', np.round(aff_0 - aff_1, 4))
    print('\n https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/')


try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-vars", help="variables", nargs='+')
    args = parser.parse_args()
    compare_headers(*args.vars)
    sys.exit(0)

except Exception as e:
    print(f"{e}", file=sys.stderr)
    sys.exit(1)
