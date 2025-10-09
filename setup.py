"""
DAFU CLI - Setup Configuration
==============================

Installation script for DAFU command-line interface.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
readme_file = this_directory / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')
else:
    long_description = "DAFU - Data Analytics Functional Utilities CLI"

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    requirements_path = this_directory / "fraud_detection" / filename
    if requirements_path.exists():
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f 
                   if line.strip() and not line.startswith('#')]
    return []

# CLI-specific requirements
cli_requirements = [
    'click>=8.0.0',
    'rich>=13.0.0',
    'IPython>=8.0.0',
]

setup(
    name='dafu-cli',
    version='1.0.0',
    description='DAFU - Data Analytics Functional Utilities CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MasterFabric',
    author_email='dafu@masterfabric.co',
    url='https://github.com/MasterFabric/dafu',
    license='AGPL-3.0',
    
    packages=find_packages(include=['dafu_cli', 'dafu_cli.*']),
    
    install_requires=cli_requirements,
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991',
        ],
        'all': read_requirements('requirements.txt'),
    },
    
    entry_points={
        'console_scripts': [
            'dafu=dafu_cli.cli:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    python_requires='>=3.8',
    
    keywords='fraud-detection machine-learning cli analytics',
    
    project_urls={
        'Bug Reports': 'https://github.com/MasterFabric/dafu/issues',
        'Source': 'https://github.com/MasterFabric/dafu',
        'Documentation': 'https://github.com/MasterFabric/dafu#readme',
    },
)

