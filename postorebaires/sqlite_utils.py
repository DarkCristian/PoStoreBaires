"""SPDX-License-Identifier: GPL-3.0-only. Transaction and explicit handle lifetime."""
from contextlib import contextmanager
import sqlite3

@contextmanager
def connect(*args, **kwargs):
    connection = sqlite3.connect(*args, **kwargs)
    try:
        with connection:
            yield connection
    finally:
        connection.close()
