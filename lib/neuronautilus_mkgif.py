import imageio
import numpy as np
import nibabel as nib
from scipy.ndimage import zoom
import matplotlib.pyplot as plt


def mkgif(img, path=False, view=0, slice4d=False, rotate=False, rotaxes=(1, 2), flip=False, rewind=True, winsorize=[1, 98],
          timebar=True, crosshair=False, scale=2, cmap=False, crop=True, vol_wise_norm=False, fps=60, concat_along=1):
    """
    :param img: image filepath, nibNifti1Image or ndarray
    :param path: string, filename to save the .gif. if False use input filename. [default=False]
    :param view: string or bool, specify type of view to plot: 'sagittal' or 0 [Default], 'coronal' or 1, 'axial'or 2
    :param rewind: bool, repeat the animation backwards. [default:=True]
    :param winsorize: list, winsorize image intensities to remove extreame values. [default:=[1,98]]
    :param rotaxes: tuple, axis along which rotate the image. [default=(1, 2)]
    :param rotate: int [1:3], int*90-degree rotation counter-clockwise. [default=False]
    :param slice4d: int: index where to slice chosen view in 4D image. [default=False -> img.shape[1]//2]
    :param timebar: bool, print timebar at the bottom [default=True]
    :param flip: int, axis to flip [default=False]
    :param crosshair: list [x, y], print crosshair at coordinates. [default=False]
    :param scale: int, factor to linear interpolate the input, time dimension is not interpolated. [default=2]
    :param cmap: str, add matplotlib cmap to image, eg: 'jet'. [default=2]
    :param crop: bool, crop air from image. [default=True]
    :param vol_wise_norm: normalize image volume-wise, only if timeseries. [default=False]
    :param fps: int, frame per second. Max 60. [default=60]
    :param concat_along: concatenate multiple images along a specific axis. [default=1]
    return file path
    todo: add plot all 3 views in one command
    """
    # Iterates through the first axis, collapses the last if ndim ==4
    # [ax0, ax1, ax2, ax3] == [Sagittal, Coronal, Axial, time] == [X, Y, Z, T]
    if not isinstance(img, list):
        imgsl = [img]
    else:
        imgsl = img

    toconcat = []
    for img in imgsl:
        if isinstance(img, str):
            inputimg = img
            img = nib.load(img).get_fdata()
        elif isinstance(img, nib.nifti1.Nifti1Image):
            inputimg = img.get_filename()
            img = img.get_fdata()
        elif isinstance(img, np.ndarray):
            if not path:
                raise IsADirectoryError("ERROR: when using a ndarray you must specify an output filename")
            img = img

        # Crop air areas
        if crop:
            if img.ndim == 4:
                xv, yv, zv = np.nansum(img, axis=(1, 2, 3)) > 0, \
                             np.nansum(img, axis=(0, 2, 3)) > 0, \
                             np.nansum(img, axis=(0, 1, 3)) > 0
                img, img, img = img[xv, :, :, :], \
                                img[:, yv, :, :], \
                                img[:, :, zv, :]
            else:
                xv, yv, zv = np.nansum(img, axis=(1, 2)) > 0, \
                             np.nansum(img, axis=(0, 2)) > 0, \
                             np.nansum(img, axis=(0, 1)) > 0
                img, img, img = img[xv, :, :], \
                                img[:, yv, :], \
                                img[:, :, zv]

        viewsstr = {'sagittal': 0, 'coronal': 1, 'axial': 2}
        views = {0: [0, 1, 2], 1: [2, 0, 1], 2: [1, 2, 0]}  # move first the dimension to slice for chosen view
        if isinstance(view, str):
            view = viewsstr[view]
        if img.ndim == 4:
            img = np.moveaxis(img, [0, 1, 2, 3], views[view] + [3])
        else:
            img = np.moveaxis(img, [0, 1, 2], views[view])

        if rotate:
            img = np.rot90(img, k=rotate, axes=rotaxes)  # Rotate along 2nd and 3rd axis by default

        if img.ndim == 4:
            img = np.moveaxis(img, 3, 0)  # push 4th dim (time) first since imageio iterates the first
            if isinstance(slice4d, bool):  # Then slice 2nd dimension to allow 3D animation
                img = img[:, img.shape[1] // 2, :, :]
            else:
                img = img[:, slice4d, :, :]

        # Winsorize and normalize intensities for plot
        Lpcl, Hpcl = np.nanpercentile(img, winsorize[0]), np.nanpercentile(img, winsorize[1])
        img[img < Lpcl], img[img > Hpcl] = Lpcl, Hpcl
        img = img * 255.0 / np.nanmax(img)
        if vol_wise_norm:  # normalize volume-wise
            img = np.array([img[idx, ...] * 255.0 / np.nanmax(img[idx, ...]) for idx in range(img.shape[0])])

        if not isinstance(flip, bool):
            img = np.flip(img, axis=flip)  # flip a dim if needed

        if not isinstance(scale, bool):  # interpol view but no time
            img = np.array([zoom(img[idx, ...], scale, order=1) for idx in range(img.shape[0])])
        else:
            scale = 1  # no interpol

        # timebar
        if timebar:
            tres = img.shape[2] / img.shape[0]
            it = 0
            for i in range(img.shape[0]):
                it += tres
                img[i, img.shape[1] - 1, 0:int(it)] = 255  # [i,0,0] is upper left corner

        # crosshair
        if isinstance(crosshair, list):
            xmask, ymask = np.zeros_like(img, dtype=bool), np.zeros_like(img, dtype=bool)
            xmask[:, crosshair[0] * scale, :], ymask[:, :, crosshair[1] * scale] = True, True
            mask = np.logical_xor(xmask, ymask)
            img[mask] = 255

        # repeat the animation backwards
        if rewind:
            img = np.concatenate([img, np.flip(img, axis=0)], axis=0)

        # set cmap
        if isinstance(cmap, str):
            cmap = plt.get_cmap(cmap)
            # return warning 'Convert image to uint8 prior to saving' but if cast it breaks
            img = cmap(img.astype(np.uint8))
        else:
            img = img.astype(np.uint8)

        # store
        toconcat += [img]

    # set outputpath if not specified
    if not path:
        path = inputimg.replace('.nii.gz', '.gif')

    # concatenate images to plot
    img = np.concatenate(toconcat, axis=concat_along)
    # write gif
    imageio.mimwrite(path, img, fps=fps)
    return path

