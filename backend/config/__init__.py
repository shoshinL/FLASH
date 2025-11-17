"""
Backend config package
"""

from .defaults import *
from .paths import get_flash_db_path, get_app_data_dir

__all__ = ['get_flash_db_path', 'get_app_data_dir']
