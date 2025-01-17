import numpy as np
import nibabel as nib
import string
import os
import sys
import argparse

try:
    parser = argparse.ArgumentParser()

    parser.add_argument("-ex", help="expression")
    parser.add_argument("-o", help="output name")
    parser.add_argument("-vars", help="variables", nargs='+')

    args = parser.parse_args()
    exprs = args.ex
    variables = args.vars
    outname = args.o

    result = None
    alphabet = list(string.ascii_lowercase)

    # Get array of each image and assign it to its respective variable
    for i, v in enumerate(variables):
        exec(alphabet[i] + ' = ' + f'nib.load("{v}").get_fdata()', globals())

    # Execute statement
    exec('result = ' + exprs, globals())
    log_expression = f'result = {exprs}'

    if outname is None:
        odir = os.path.dirname(variables[0])
        outname = odir + '/result.nii.gz'
    # Save
    nib.Nifti1Image(result, nib.load(variables[0]).affine).to_filename(outname)
    sys.exit(0)

except Exception as e:
    print(f"{e}", file=sys.stderr)
    sys.exit(1)
