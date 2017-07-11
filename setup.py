from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()


setup(name='ttldict',
      version='0.3.0',
      description="Dictionary with auto-expiring values for caching purposes",
      long_description=long_description,
      author='Oz Tiram',
      author_email='oztiram@mobilityhouse.com',
      url='https://github.com/mobilityhouse/ttldict',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'],
      zip_safe=True,
      extras_require={'test': ['pytest', 'coverage']})
