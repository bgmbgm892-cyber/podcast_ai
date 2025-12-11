"""Uploader module — thin wrapper for backwards compatibility.

The actual publish_local implementation lives in src.utils.
"""
from utils import publish_local

__all__ = ["publish_local"]

if __name__ == '__main__':
    print('uploader module loaded (wrapper)')
