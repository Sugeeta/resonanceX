from setuptools import setup, find_packages

setup(
    name='resonanceX',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'pandas',
        'plotly',
        'dash',
    ],
    author='Sugeeta',
    author_email='sk.at.analytics@gmail.com',
    description='A Python package for simulating and visualizing resonance phenomena in physics',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Sugeeta/resonanceX',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    python_requires='>=3.10',
)