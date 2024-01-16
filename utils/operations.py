from ast import Dict
import os
import glob
import logging
from typing import Dict
import tempfile


def dir_size_adjust(dir_path: str, 
                    num_files : int = 10, 
                    size_limit : int = 100000000, 
                    logger: logging.Logger = logging.getLogger(__name__)):
    
    """_summary_: Adjusts the number of files in the directory to 10 by deleting the oldest files.

    Args:
        file_path (str): Path to the directory.
        num_files (int, optional): Number of files to keep. Defaults to 10.
        size_limit (int, optional): Maximum size of the directory in bytes. Defaults to 100000000.
    """
    files = glob.glob(os.path.join(dir_path, "*"))
    try:
        if len(files) > num_files:
            files.sort(key=os.path.getmtime)
            for i in range(len(files) - 10):
                os.remove(files[i])
            files = glob.glob(os.path.join(dir_path, "*"))
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        if sum(os.path.getsize(f) for f in files) > size_limit:
            files.sort(key=os.path.getmtime)
            while sum(os.path.getsize(f) for f in files) > size_limit:
                os.remove(files[0])
                logger.info(f"Removed file {files[0]}")
                files = glob.glob(os.path.join(dir_path, "*"))
            files.sort(key=os.path.getmtime, reverse=True)
            return True
        else:
            files.sort(key=os.path.getmtime, reverse=True)
            return True
    except FileNotFoundError:
        logger.error(f"Directory not found: {dir_path}", exc_info=True)
    except PermissionError:
        logger.error(f"Permission denied for directory: {dir_path}", exc_info=True)
    except Exception as e:
        logger.error("An unexpected error occurred in dir_size_adjust", exc_info=True)
    return False

def dict_size_adjust(dict : Dict, 
                     num_items : int = 10, 
                     logger: logging.Logger = logging.getLogger(__name__)):
    
    """_summary_: Adjusts the number of items in the dictionary to 10 by deleting the oldest items.

    Args:
        dict (dict): Dictionary to be adjusted.
        num_items (int, optional): Number of items to keep. Defaults to 10.
    """
    try:
        keys = list(dict.keys())
        keys.sort(key=lambda x: dict[x]['timestamp'])
        if len(dict) > num_items:
            for i in range(len(dict) - num_items):
                logger.info(f"Removed task {keys[i]}")
                del dict[keys[i]]
            return True
        else:
            return True
    except Exception as e:
        logger.error(f"An unexpected error occurred in dict_size_adjust: {e}", exc_info=True)
        return False

def save_temp_file(audio_data: bytes, file_extension: str = 'wav') -> str:
    """
    Save the audio data to a temporary file and return the file path.

    Args:
    audio_data (bytes): The audio data to save.
    file_extension (str): The file extension for the audio file (default 'wav').

    Returns:
    str: The path to the temporary audio file.
    """
    temp_file, temp_file_path = tempfile.mkstemp(suffix=f'.{file_extension}')
    with os.fdopen(temp_file, 'wb') as file:
        file.write(audio_data)

    return temp_file_path

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension of a file.

    Args:
    file_path (str): The path to the file.

    Returns:
    str: The file extension.
    """
    return os.path.splitext(file_path)[1][1:].strip().lower()