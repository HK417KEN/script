#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GIMP 3 port of auto_set_live_cover (originally written for GIMP 2 / gimpfu).

import os
import sys

import gi
gi.require_version('Gimp', '3.0')
gi.require_version('GimpUi', '3.0')
gi.require_version('Gegl', '0.4')
from gi.repository import Gimp, GimpUi, Gegl, Gio, GObject, GLib

PROC_NAME = 'python-fu-auto-set-live-cover'

TILE_SIZE = 26.0
TILE_HEIGHT = 4.0
TILE_SPACING = 1.0
TILE_NEATNESS = 1.0
TILE_ALLOW_SPLIT = True
LIGHT_DIR = 135.0
COLOR_VARIATION = 0.0
ANTI_ALIASING = True
COLOR_AVERAGING = True
# GIMP 2's plug-in-mosaic took tile_type=1 here, i.e. hexagons;
# gegl:mosaic expects the choice name instead of the old enum number
TILE_TYPE = 'hexagons'
TILE_SURFACE = True
FILTER_OPACITY = 10.0


def set_config(config, name, value):
    """Set a gegl:mosaic property, coercing the value to the property type."""
    for pspec in config.list_properties():
        if pspec.name == name:
            type_name = GObject.type_name(pspec.value_type)
            if type_name == 'gboolean':
                value = bool(value)
            elif type_name in ('gfloat', 'gdouble'):
                value = float(value)
            elif type_name in ('gchar', 'gint', 'guint', 'glong', 'gulong',
                               'gint64', 'guint64'):
                value = int(value)
            config.set_property(name, value)
            return
    raise KeyError('unknown gegl:mosaic property: ' + name)


def apply_mosaic(layer):
    """Apply the mosaic effect (formerly plug-in-mosaic) to a layer."""
    mosaic = Gimp.DrawableFilter.new(layer, 'gegl:mosaic', 'Mosaic')
    config = mosaic.get_config()
    set_config(config, 'tile-size', TILE_SIZE)
    set_config(config, 'tile-height', TILE_HEIGHT)
    set_config(config, 'tile-spacing', TILE_SPACING)
    set_config(config, 'tile-neatness', TILE_NEATNESS)
    set_config(config, 'tile-allow-split', TILE_ALLOW_SPLIT)
    set_config(config, 'light-dir', LIGHT_DIR)
    set_config(config, 'color-variation', COLOR_VARIATION)
    set_config(config, 'antialiasing', ANTI_ALIASING)
    set_config(config, 'color-averaging', COLOR_AVERAGING)
    set_config(config, 'tile-type', TILE_TYPE)
    set_config(config, 'tile-surface', TILE_SURFACE)
    layer.merge_filter(mosaic)


def process_file(input_path, output_dir, stem):
    image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,
                           Gio.File.new_for_path(input_path))
    try:
        layers = image.get_layers()
        if not layers:
            return

        width = image.get_width()
        height = image.get_height()

        if width * 720 == height * 1280:
            # exact 16:9: only scale to 1280x720, then save directly
            if width != 1280 or height != 720:
                image.scale(1280, 720)
            out_jpg = os.path.join(output_dir, stem + '.jpg')
            Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                           Gio.File.new_for_path(out_jpg), None)
            return

        # any other aspect ratio: scale (keeping the aspect ratio) to the
        # largest size that fits into 1280x720 - no cropping, no stretching;
        # one side ends up exactly at 1280 or 720, the other stays below
        # its limit
        if width * 720 > height * 1280:
            # wider than 16:9: width is the limiting side
            new_width = 1280
            new_height = max(1, round(height * 1280.0 / width))
        else:
            # taller than 16:9: height is the limiting side
            new_height = 720
            new_width = max(1, round(width * 720.0 / height))

        source = layers[0]
        source.add_alpha()
        image.scale(new_width, new_height)
        # center the content on a 1280x720 canvas (transparent margins)
        image.resize(1280, 720,
                     (1280 - new_width) // 2, (720 - new_height) // 2)

        filter_layer = Gimp.Layer.new(image, 'b', 1280, 720,
                                      Gimp.ImageType.RGB_IMAGE, 100.0,
                                      Gimp.LayerMode.NORMAL)
        image.insert_layer(filter_layer, None, 1)
        # copy below the filter layer (kept for the XCF output)
        image.insert_layer(filter_layer.copy(), None, 2)

        # set foreground color to black and fill the filter layer
        Gimp.context_set_foreground(Gegl.Color.new('black'))
        filter_layer.edit_bucket_fill(Gimp.FillType.FOREGROUND, 0.0, 0.0)

        apply_mosaic(filter_layer)
        # the mosaic overlay is only 10% opaque (90% transparent)
        filter_layer.set_opacity(FILTER_OPACITY)

        # save the xcf image (layers intact)
        out_xcf = os.path.join(output_dir, stem + '.xcf')
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                       Gio.File.new_for_path(out_xcf), None)

        # merge layers down to a single layer
        while len(image.get_layers()) > 1:
            image.merge_down(image.get_layers()[0],
                             Gimp.MergeType.EXPAND_AS_NECESSARY)

        # save the jpg image
        out_jpg = os.path.join(output_dir, stem + '.jpg')
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                       Gio.File.new_for_path(out_jpg), None)
    finally:
        image.delete()


def run(procedure, run_mode, image, drawables, config, data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init('auto_set_live_cover.py')
        dialog = GimpUi.ProcedureDialog.new(procedure, config,
                                             'Auto set live cover')
        GimpUi.window_set_transient(dialog)
        dialog.fill(['input-folder', 'output-folder'])
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
        dialog.destroy()

    input_arg = config.get_property('input-folder')
    output_arg = config.get_property('output-folder')
    input_dir = input_arg.get_path() if input_arg else None
    output_dir = output_arg.get_path() if output_arg else None

    if not input_dir or not os.path.isdir(input_dir):
        Gimp.message('Input directory does not exist: ' + str(input_dir))
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error('Input directory does not exist'))
    if not output_dir or not os.path.isdir(output_dir):
        Gimp.message('Output directory does not exist: ' + str(output_dir))
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error('Output directory does not exist'))

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.xcf')):
            continue
        try:
            stem = os.path.splitext(filename)[0]
            process_file(os.path.join(input_dir, filename), output_dir, stem)
        except Exception as err:
            Gimp.message('Unexpected error: ' + str(err))

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class AutoSetLiveCover(Gimp.PlugIn):
    def do_set_i18n(self, procedure_name):
        # no translations; avoids a missing-locale-dir warning at startup
        return False, None, None

    def do_query_procedures(self):
        return [PROC_NAME]

    def do_create_procedure(self, name):
        if name != PROC_NAME:
            return None

        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            run, None)
        procedure.set_image_types('*')
        procedure.set_menu_label('Set live cover')
        procedure.set_documentation(
            'Auto set live cover',
            'Loads every image of the input directory. Exact 16:9 images '
            'are scaled to 1280x720 and saved as JPEG directly. Other '
            'aspect ratios are scaled to fit into 1280x720 without '
            'cropping or distortion, centered on the canvas, and get a '
            '10% mosaic overlay; they are saved as XCF and JPEG.',
            PROC_NAME)
        procedure.set_attribution('KEN', 'Open source', '2023')
        procedure.add_menu_path('<Image>/File/[Export]')
        procedure.set_sensitivity_mask(
            Gimp.ProcedureSensitivityMask.DRAWABLE |
            Gimp.ProcedureSensitivityMask.NO_DRAWABLES)
        procedure.add_file_argument(
            'input-folder', '_Input directory',
            'Folder with the source images',
            Gimp.FileChooserAction.SELECT_FOLDER, True, None,
            GObject.ParamFlags.READWRITE)
        procedure.add_file_argument(
            'output-folder', 'O_utput directory',
            'Folder where the converted images are saved',
            Gimp.FileChooserAction.SELECT_FOLDER, True, None,
            GObject.ParamFlags.READWRITE)
        return procedure


Gimp.main(AutoSetLiveCover.__gtype__, sys.argv)
