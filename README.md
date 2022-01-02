# func_adl_servicex_type_generator

 Given a description `yaml` file, generate a set of types and datasets for ServiceX

## Introduction

Produce a analysis-focused python package that:

* Has types for the objects a user is likely to access on a particular backend
* Has any injected code needed (to access things like special collections off the main `Event` object)
* Can inject intelligent code, like apply special scripts or include files for the C++ backend.
* Defines a typed flavor of a `servicex` dataset object.

## Usage

After `pip install`ing this package, the following command will write out a package in the parent directory:

```bash
sx_type_gen <path-to-type-yaml-file>
```

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

* [x] Produce very simple ATLAS `xAOD` typed objects to access collections like `Jets`, etc, in a R21 xAOD (C++ backend). This should include a locally installable package (`pip install -e`).
* [x] In a second package start developing a Jupyter notebook/book showing off the features for accessing the above collections
  * The [website](https://gordonwatts.github.io/xaod_usage) and github [repo](https://github.com/gordonwatts/xaod_usage).
* [x] After `Jets`, do 'EventInfo' and 'MissingET'. These two should generalize the system to other types.
* [x] Add automatic collection injection (so that we don't need definitions in the xAOD backend)
* [x] Access Jet constituents from Jet objects
* [x] Access truth particle arrays from their parent collection articles
* [x] Do something that requires a separate include file to access an object (include file injection).
* [ ] Add support for arbitrary injection of other packages in the ATLAS C++ backend (e.g. corrections). Use `Jets` to develop this.
* [ ] Support getting a single systematic error or nominal.
* [ ] Add support for `Jet::getAttribute`, which is a C++ code-behind function
* [ ] Figure out how to deal with multiple systematic errors requested at the same time, in different parts of a query.
* [ ] Do correction for `MissingET`, the most complex correction, perhaps.
* [ ] Use _common knowledge_ to get the first set of collections and implement those:
  * Tracks
  * etc.
* [ ] Support R22
* [ ] First release of package
* [ ] For version 2 plan out support for a flat ROOT `TTree` file.

## Development

This package is using `poetry`. As of writing, the following works on windows (the latest version of poetry is broken on windows):

```bash
pip install poetry==1.1.7
cd func_adl_servicex_type_generator
poetry env use python
poetry install
poetry shell
code .
```

All tests should run out of the box with `pytest`. Everything on master should always pass all tests and have excellent code coverage. Work should occur on branches.
