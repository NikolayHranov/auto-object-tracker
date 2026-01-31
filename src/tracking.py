# import numpy as np
# import pandas as pd
# import cv2
# import time
import multiprocessing as mp
from pathlib import Path
import copy
# from .tracking_log import logger
import json
from .data import DEFAULT_SETTINGS, VIDEO_FORMATS
from .utilities import track


class Track():

    def __init__(self, path_str, processes=DEFAULT_SETTINGS["processes"]):

        self.pool = mp.Pool(processes=processes)

        path = Path(path_str).resolve()

        self.pipeline_opt_run(path)

        self.pool.close()
        self.pool.join()

        del self.pool
    

    def pipeline_opt_run(self, path):

        self.pipeline_recursive_run(path, copy.deepcopy(DEFAULT_SETTINGS))


    def pipeline_recursive_run(self, path, settings):

        with open(str(path)) as file:

            info = json.load(file)

            print("info: " + str(info))

            if "settings" in info:
                settings.update(info["settings"])

            if "confdirs" in info:
                for dir in info["confdirs"]:
                    path_dir = Path(dir)

                    if not path_dir.is_absolute():
                        path_dir = path.parent / path_dir

                    self.pipeline_recursive_run(path_dir, copy.deepcopy(settings))
            
            if "dirs" in info:
                for dir in info["dirs"]:
                    path_dir = Path(dir)

                    if not path_dir.is_absolute():
                        path_dir = path.parent / path_dir
                    
                    self.track_dir(path_dir, copy.deepcopy(settings))
    

    def track_dir(self, path, settings):

        local_settings_path = path / "settings.json"

        ignore_files = []

        if local_settings_path.is_file():

            with open(str(local_settings_path), "r") as file:

                local_settings = json.load(file)

                if "ignore" in local_settings:
                    ignore_files = local_settings["ignore"]

                if "settings" in local_settings:
                    settings.update(local_settings["settings"])


        for f in path.iterdir():

            if f.is_file() and f.suffix.lower() in VIDEO_FORMATS and f.name not in ignore_files:
                self.pool.apply_async(track, args=(str(f), copy.deepcopy(settings)))
        

