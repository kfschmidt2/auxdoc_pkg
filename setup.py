from setuptools import setup, find_packages

setup(name='auxdoc',
      version='0.1',
      description='AUXDoc Python Based Report Cretion Tool',
      author='Karl Schmidt',
      author_email='kfschmidt@gmail.com',
      url='https://github.com/kfschmidt2/auxdoc',
      packages=['auxdoc', 'auxdoc.media', 'auxdoc.layouts'],
      packages_dir={"":"auxdoc"},
      include_package_data=True,
      )
