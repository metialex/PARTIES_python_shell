from setuptools import setup, find_packages

dependencies = ['numpy',
                'pandas',
                'h5py',
                'icecream',
                'matplotlib',
                ]
             
setup(
   name='parties',
   version='0.0.25',
   description='A python shell for parties cfd code',
   license="MIT",
   long_description='A python shell for parties cfd code',
   author='Alexander Metelkin',
   author_email='a.metelkin@tu-braunschweig.de',
   url="https://github.com/metialex/PARTIES_python_shell",
   py_modules=["parties"],
   package_dir={'': 'src'},
   install_requires=dependencies #external packages as dependencies
)