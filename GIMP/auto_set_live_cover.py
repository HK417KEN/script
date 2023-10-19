#!/usr/bin/env python

import os
import gimpcolor
from gimpfu import *

def auto_set_live_cover(image, layer, inputFolder, outputFolder):
    ''' Auto set live cover images of a folder.

    modify from : https://github.com/jfmdev/PythonFuSamples/blob/master/test-invert-layer.py

    Parameters:
    inputFolder : string The folder of the images that must be inverted.
    outputFolder : string The folder in which save the inverted images.
    '''
    # Iterate the folder
    for file in os.listdir(inputFolder):
        try:
            # Build the full file paths.
            inputPath = inputFolder + "\\" + file
            outputPath = outputFolder + "\\"
        
            # Open the file if is a JPEG or PNG or XCF image.
            image = None
            fileWithoutExt = None
            if(file.lower().endswith(('.png'))):
                image = pdb.file_png_load(inputPath, inputPath)
                fileWithoutExt = file[0:file.rindex('.png')]
            if(file.lower().endswith(('.jpeg'))):
                image = pdb.file_jpeg_load(inputPath, inputPath)
                fileWithoutExt = file[0:file.rindex('.jpeg')]
            if(file.lower().endswith(('.jpg'))):
                image = pdb.file_jpeg_load(inputPath, inputPath)
                fileWithoutExt = file[0:file.rindex('.jpg')]
            if(file.lower().endswith(('.xcf'))):
                image = pdb.gimp_file_load(inputPath, inputPath)
                fileWithoutExt = file[0:file.rindex('.xcf')]

            outputPath = outputPath + fileWithoutExt + ".xcf"

            # Verify if the file is an image.
            if(image != None):
                if(len(image.layers) > 0):
                    layer = image.layers[0]
                    # add alpha channel
                    pdb.gimp_layer_add_alpha(layer)
                    # let image scale to 1280x598
                    pdb.gimp_image_scale(image, 1280, 598)
                    # resize canvas to 1280x720
                    pdb.gimp_image_resize(image, 1280, 720, 0, 61)
                    # new filter layer
                    bLayer = pdb.gimp_layer_new(image, 1280, 720, 0, "b", 100., 29)
                    pdb.gimp_image_add_layer(image, bLayer, 1)
                    # copy to background layer
                    pdb.gimp_image_add_layer(image, pdb.gimp_layer_copy(bLayer, 0), 2)
                    # set foreground color to black
                    pdb.gimp_context_set_foreground(gimpcolor.RGB(0,0,0))
                    # fill filter layer to black
                    pdb.gimp_drawable_edit_bucket_fill(bLayer, 0, 0., 0.)
                    # set filter layer to 10% opacity (90% transparent)
                    pdb.gimp_layer_set_opacity(bLayer, 10.)

                    # Save the image.
                    pdb.gimp_xcf_save(0, image.layers[0], layer, outputPath, outputPath)
        except Exception as err:
            gimp.message("Unexpected error: " + str(err))

register(
    "python_fu_auto_set_live_cover",
    "Auto set live cover",
    "Auto set live cover images of a folder",
    "[KEN]",
    "Open source",
    "2023",
    "<Image>/Filters/Auto/Set live cover",
    "",
    [
        (PF_DIRNAME, "inputFolder", "Input directory", ""),
        (PF_DIRNAME, "outputFolder", "Output directory", "")
    ],
    [],
    auto_set_live_cover)

main()
