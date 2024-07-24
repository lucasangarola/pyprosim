from setuptools import setup

setup(
    name="pyprosim",
    version="0.1.0",
    description="Python wrapper for ProSim SDK",
    url="https://github.com/lucasangarola/pyprosim.git",
    author="Lucas M. Angarola",
    author_email="737goodness@gmail.com",
    license="MIT",
    packages=["pyprosim"],
    install_requires=["pythonnet>=3.0.1"],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    include_package_data=True,
)
