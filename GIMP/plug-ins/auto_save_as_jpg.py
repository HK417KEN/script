#!/usr/bin/env python

import os
import gimpcolor
from gimpfu import *

def auto_save_as_jpg(image, layer, inputFolder, outputFolder):
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
            fileWithoutExt = file
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

            outputPath = outputPath + fileWithoutExt + ".jpg"
                
            # Verify if the file is an image.
            if(image != None):
                # Invert the image.
                if(len(image.layers) > 0):

                    # merge layers
                    while len(image.layers) > 1:
                        pdb.gimp_image_merge_down(image, image.layers[0], 0)

                    # Save the image.
                    pdb.file_jpeg_save(image, image.layers[0], outputPath, outputPath, 0.9, 0, 0, 0, "Creating with GIMP", 0, 0, 0, 0)
        except Exception as err:
            gimp.message("Unexpected error: " + str(err))

register(
    "python_fu_auto_save_as_jpg",
    "Auto save as jpg",
    "Auto save as jpg of a folder",
    "[KEN]",
    "Open source",
    "2023",
    "<Image>/Filters/Auto/Save As Jpg",
    "",
    [
        (PF_DIRNAME, "inputFolder", "Input directory", ""),
        (PF_DIRNAME, "outputFolder", "Output directory", "")
    ],
    [],
    auto_save_as_jpg)

main()
