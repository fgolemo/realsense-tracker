from setuptools import setup

setup(name='realsense_tracker',
      version='1.0',
      install_requires=[
          'opencv-python',
          'numpy',
          'pyrealsense2' # tested on D435i
      ]
)
