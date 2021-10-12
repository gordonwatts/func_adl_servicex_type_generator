# func_adl_servicex_type_generator

 Given a description `yaml` file, generate a set of types and datasets for ServiceX

## Introduction

Produce a analysis-focused python package that:

* Has types for the objects a user is likely to access on a particular backend
* Has any injected code needed (to access things like special collections off the main `Event` object)
* Can inject intelligent code, like apply special scripts or include files for the C++ backend.
* Defines a typed flavor of a `servicex` dataset object. 

## How this works

To get things setup:

1. Load the `yaml` file that contains a definition of the collections and other object types necessary to access the data in the type of file we are producing for.
1. Uses a small amount of other metadata in addition
    * The name of what it is producing, like _xAODR21_ or similar.
1. Write out a python package that a user can install.

Then the user:

1. User `pip install`'s the package in the environment
1. User starts a typed `func_adl` query from the dataset provided by this package.
    * User will need to specify the dataset and the backend name.

## Status

This is currently a package that is planned. The development path is as follows:

* [ ] Produce very simple ATLAS `xAOD` typed objets to access collections like `Jets`, etc, in a R21 xAOD (C++ backend). This should include a locally installable package (`pip install -e`).
* [ ] In a second package start developing a Jupyter notebook/book showing off the features for accessing the above collections
* [ ] After `Jets`, do 'EventInfo' and 'MissingET'. These two should generalize the system to other types.
* [ ] Add support for arbitrary injection of other packages in the ATLAS C++ backend (e.g. corrections). Use `Jets` to develop this. Include ability to do a single systematic error or nominal.
* [ ] Figure out how to deal with multiple systematic errors requested at the same time, in different parts of a query.
* [ ] Add above to the Jupyter notebook
* [ ] Do correction for `MissingET`, the most complex correction, perhaps.
* [ ] Use _common knowledge_ to get the first set of collections and implement those:
  * Tracks
  * etc.
* [ ] Support R22
* [ ] First release of package
* [ ] For version 2 plan out support for a flat ROOT `TTree` file.
