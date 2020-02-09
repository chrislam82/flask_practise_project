# setup.py
# 	Build project as distribution file.
# 		--> Buidling it as a distribution file means we can run it wherever
# 		--> Easier to manage dependencies
# 		--> Can isolate test tools from development environment

from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),		# find_packages() finds the packages automatically
    include_package_data=True, 		# include_package_data to include other files like static and templates (See makefile.in)
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
