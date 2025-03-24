#!/usr/bin/env python
#
# -------------------------------------------------------------------------------------
#
# Copyright (c) 2013, Jose F. Maldonado
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#    - Redistributions of source code must retain the above copyright notice, this 
#    list of conditions and the following disclaimer.
#    - Redistributions in binary form must reproduce the above copyright notice, 
#    this list of conditions and the following disclaimer in the documentation and/or 
#    other materials provided with the distribution.
#    - Neither the name of the author nor the names of its contributors may be used 
#    to endorse or promote products derived from this software without specific prior 
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH 
# DAMAGE.
#
# -------------------------------------------------------------------------------------
# Modified by: [KEN]
# Modified from : https://github.com/jfmdev/PythonFuSamples/blob/master/test-batch-cartoon.py
# -------------------------------------------------------------------------------------
#

import os
import gimpcolor
from gimpfu import *

def auto_set_live_cover(image, layer, inputFolder, outputFolder):
    ''' Auto set live cover images of a folder.

    Modified from : https://github.com/jfmdev/PythonFuSamples/blob/master/test-batch-cartoon.py

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
            fileWithoutExt = ""
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

            outputPathXCF = outputPath + fileWithoutExt + ".xcf"
            outputPathJPG = outputPath + fileWithoutExt + ".jpg"

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
                    filterLayer = pdb.gimp_layer_new(image, 1280, 720, 0, "b", 100., 29)
                    pdb.gimp_image_add_layer(image, filterLayer, 1)
                    # copy to background layer
                    pdb.gimp_image_add_layer(image, pdb.gimp_layer_copy(filterLayer, 0), 2)
                    # set foreground color to black
                    pdb.gimp_context_set_foreground(gimpcolor.RGB(0,0,0))
                    # fill filter layer to black
                    pdb.gimp_drawable_edit_bucket_fill(filterLayer, 0, 0., 0.)

                    # mosaic
                    tile_size = 26.
                    tile_height = 4.
                    tile_spacing = 1.
                    tile_neatness = 1.
                    tile_allow_split = 1
                    light_dir = 135.
                    color_variation = 0.
                    antialiasing = 1
                    color_averaging = 1
                    tile_type = 1
                    tile_surface = 1
                    grout_color = 0
                    pdb.plug_in_mosaic(
                        image,
                        filterLayer,
                        tile_size,
                        tile_height,
                        tile_spacing,
                        tile_neatness,
                        tile_allow_split,
                        light_dir,
                        color_variation,
                        antialiasing,
                        color_averaging,
                        tile_type,
                        tile_surface,
                        grout_color
                    )

                    # set filter layer to 10% opacity (90% transparent)
                    pdb.gimp_layer_set_opacity(filterLayer, 10.)

                    # Save the xcf image.
                    pdb.gimp_xcf_save(0, image, image.layers[0], outputPathXCF, outputPathXCF)

                    # merge layers
                    while len(image.layers) > 1:
                        pdb.gimp_image_merge_down(image, image.layers[0], 0)

                    # Save the jpg image.
                    pdb.file_jpeg_save(image, image.layers[0], outputPathJPG, outputPathJPG, 0.9, 0, 0, 0, "Creating with GIMP", 0, 0, 0, 0)

        except Exception as err:
            gimp.message("Unexpected error: " + str(err))

register(
    "python_fu_auto_set_live_cover",
    "Auto set live cover",
    "Auto set live cover images of a folder",
    "[KEN]",
    "Open source (BSD 3-clause license)",
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
