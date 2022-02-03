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
* [x] Add support for arbitrary injection of other packages in the ATLAS C++ backend (e.g. corrections). Use `Jets` to develop this.
* [x] Support getting a single systematic error or nominal.
* [x] Use _common knowledge_ (CP groups) to get the first set of collections and implement those:
  * [x] Muons
  * [x] Electrons
  * [x] Taus
  * [x] Tracks
  * [x] Primary Vertices
  * [x] MissingET (basics)
  * [x] Trigger
* Technical Debt Cleanup
  * [x] Use python decorators for all class methods and classes themselves (and convert everything to use them)
  * [x] Track changes to the ast inside nested functions (a default argument to a function inside a select)
  * [x] Make sure the type propagations works inside the lambda functions for Select, Where, etc.
  * [x] Fix the trigger object matching
  * [ ] Get rid of ctor generation (ops!)
* [ ] Add support for `Jet::getAttribute`, which is a C++ code-behind function, but likely it is a method
* [ ] Add support for decorator access
* [ ] Support R22
* [ ] First release of package (documentation on how to run and build, pushing type info to pypi, making it easy to use, etc.)

Deferred to later (they are now in github issues in the `xaod_usage` project):

* Photons (head of 21.1 can't run on DAOD_PHYS at the moment)
* DiTau Jets (head of 21.1 can't run on DAOD_PHYS at the moment)
* Rebuilding MissingET is put off till later because it is complex and I do not understand it!
* BTagging is C++ code that will be written inline, likely, so added as a todo for later.
* Trigger matching isn't working in 21.2
* Overlap removal hasn't been tackled yet

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
