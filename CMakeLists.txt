cmake_minimum_required(VERSION 3.5)

project(import3DDose)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/keithoffer/3DSlicer-Import3DDose")
set(EXTENSION_CATEGORY "Importer")
set(EXTENSION_CONTRIBUTORS "Keith Offer (None)")
set(EXTENSION_DESCRIPTION "A simple extension to import .3ddose files from DOSXYZnrc")
set(EXTENSION_ICONURL "")
set(EXTENSION_SCREENSHOTURLS "")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(import3DDose)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
