"""
This code provides a command-line wrapper to call the brdf and topographic functions on a given scene

Author: Winston Olson-Duvall, winston.olson-duvall@jpl.nasa.gov
"""

import argparse
import glob
import hytools as ht
import os
import sys

from hytools.brdf import *
from hytools.topo_correction import *

# The input_dir is fixed within the Docker container
input_dir = "/Users/winstono/Desktop/GeoSPEC/Algorithm_Testing/data"
output_dir = "/Users/winstono/Desktop/GeoSPEC/Algorithm_Testing/data"


def get_input_files(image_id):
    """
    Return reflectance and observation files from the input directory
    """
    rfl_path = glob.glob(input_dir + "/" + image_id + "*_rfl_*_img")
    obs_path = glob.glob(input_dir + "/" + image_id + "*_rdn_obs_ort")

    if len(rfl_path) == 0 or len(obs_path) == 0:
        raise Exception("Can't find reflectance or obs file in %s!" % input_dir)

    return rfl_path[0], obs_path[0]


def apply_brdf_correction(rfl_path, obs_path):
    """
    Wrapper function to call hytools.brdf.brdf_correct_img
    :param rfl_path: Input reflectance path
    :param obs_path: Input obs path
    :return: brdf_path: Path to brdf corrected image
    """
    # Load reflectance file
    rfl = ht.openENVI(rfl_path)
    rfl.load_data()
    rfl.no_data = -9999

    # Load obs file
    obs = ht.openENVI(obs_path)
    obs.load_data()

    # Get sensor and solar azimuth and zenith
    rfl.sensor_az = np.radians(obs.get_band(1))
    rfl.sensor_zn = np.radians(obs.get_band(2))
    rfl.solar_az = np.radians(obs.get_band(3))
    rfl.solar_zn = np.radians(obs.get_band(4))

    brdf_path = rfl_path.replace("_rfl_", "_brdf_")
    brdf_correct_img(rfl, brdf_path, ross="thick", li="dense")

    return brdf_path


def apply_topographic_correction(rfl_path, obs_path):
    """
    Wrapper function to call hytools.topo_correction.topo_correct_img
    :param rfl_path: Input reflectance path
    :param obs_path: Input obs path
    :return: topo_path: Path to topographically corrected image
    """
    # Load reflectance file
    rfl = ht.openENVI(rfl_path)
    rfl.load_data()
    rfl.no_data = -9999

    # Load obs file
    obs = ht.openENVI(obs_path)
    obs.load_data()

    # Get sensor and solar azimuth and zenith
    rfl.sensor_az = np.radians(obs.get_band(1))
    rfl.sensor_zn = np.radians(obs.get_band(2))
    rfl.solar_az = np.radians(obs.get_band(3))
    rfl.solar_zn = np.radians(obs.get_band(4))
    rfl.slope = np.radians(obs.get_band(6))
    rfl.aspect = np.radians(obs.get_band(7))

    topo_path = rfl_path.replace("_rfl_", "_topo_")
    topo_correct_img(rfl, topo_path, cos_i=obs.get_band(8))

    return topo_path


def main():
    """
    Parse command line arguments and call brdf and topographic corrections accordingly
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("image_id")
    parser.add_argument("--brdf", action="store_true")
    parser.add_argument("--topo", action="store_true")
    args = parser.parse_args()

    # Exit if not options are chosen
    if not args.brdf and not args.topo:
        print("ERROR: No options selected. Please choose either \"--brdf\" or \"--topo\".")
        sys.exit(1)

    # Get required input files
    rfl_path, obs_path = get_input_files(args.image_id)

    # Perform BRDF correction
    if args.brdf:
        brdf_path = apply_brdf_correction(rfl_path, obs_path)

    # Perform topographic correction
    if args.topo:
        topo_path = apply_topographic_correction(rfl_path, obs_path)


if __name__ == '__main__':
    main()