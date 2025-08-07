"""
页面包
"""

from .voice_list import render_voice_list
from .test_voice import render_test_voice
from .add_voice import render_add_voice
from .batch_upload import render_batch_upload

__all__ = ['render_voice_list', 'render_test_voice', 'render_add_voice', 'render_batch_upload'] 