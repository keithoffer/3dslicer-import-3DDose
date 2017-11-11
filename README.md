Import 3DDose 1.0.0
===================

A simple plugin for 3D Slicer 4.8.0+ to import .3ddose files from DOSxyznrc.

This was mainly an excuse for me to explore the 3D Slicer python plugin API, but it works pretty well for quickly checking results from simulations.

![Animated picture showing operation of the plugin](Screenshots/preview.gif?raw=true)

Installation
------------
In 3D Slicer, load the Extension Wizard module and then click "Select Extension". Browse to this folder and click OK. You can also then add this folder to the module search path to auto-load the module on load.

Usage
-----
Once the module is selected, press the "Import *.3ddose" button to browse and load a .3ddose file. There are a couple of options to choose before import, mainly whether to import the dose / uncertainties and if to import them into new volumes or overwrite existing ones. You can also choose to normalise the dose to the range [0,1] rather than the actual values in the .3ddose file. This can be useful as the very small numbers in .3ddose files aren't shown particularly well in 3D Slicer (data probe often just shows 0) and sometimes the colour lookup table can act strange for a similar reason.

Known issues
------------

As far as I understand, ITK (which 3D Slicer uses under the hood to store image volumes) dosen't support varying the voxel size along an axis (i.e. the voxels can be different sizes in the X/Y/Z directions, but only one size is supported along each axis). Often .3ddose files have voxels of varying size at different location. This plugin will import those files, but the spacing will be set to the first size found in each direction and will not be geometrically accurate. A warning message will be shown in this case.

License
-------

Import 3DDose is copyrighted free software made available under the terms of the GPLv3

Copyright: (C) 2017 by Keith Offer. All Rights Reserved.
