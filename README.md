# Abstract

This project is an example of creation of service that accept user file (MS Excel format)
and validate is using rules implemented with `pytest`.

The challenge is that `pytest` due to its internal architecture is optimized for one time 
command line launch. 
But if you want to call it programmatically - it may require from your patience and experimenting.
Expecially, if you want to run it several times from a services. And especially, if you want some of your
tests being executed for each of the line of the file.

# Key findings and takeaways

1. Programmatic call to `pytest` for collecting the results of execution is implemented with custom plugin
   intercepting moments of reporting individual test and making test summary.

2. Pass of the "file-to-be-tested" as command line parameter for `pytest` call may not well handle cases for 
   "row-base" testing due to the "late visibility" of the file name (as part of the fixture).
   By that time test collection phase will be already completed. So, another custom plugin will be required, 
   which will intercept process of "configuring" of the test run.  

3. `pytest` should be run in isolation (separate process) to handle dynamically passed data-to-test.
   While passing results of the test execution one should be careful to ensure that all results are
   serializable ("pickle-able").

# Project structure and dependencies

## Folders

| Folder        | Description                                                                    |
|---------------|--------------------------------------------------------------------------------|
| `/app`        | The code of t he service and Docker files is kept under  folder.               |
| `/app/<type>` | Tests for 2 sample file types are stored under subfolders named by file types. |
| `/examples`   | Samples MS Excel files which are used for corresponding tests.                 |

## Application structure

| File            | Description                                                       |
|-----------------|-------------------------------------------------------------------|
| common_types.py | Declaration of the types, used in service and validation process. |
| main.py         | Main file of the service, implemented with FastAPI                |
| validator.py    | Module handling `pytest` execution for given file and type        | 

## Dependencies

Project relies on several well-known libraries.

### Web service implementation:
 
- fastapi
- python-multipart
- pydantic
- uvicorn

### Testing 

- pytest
- pytest-dependency

### Processing MS Excel files

- openpyxl
- pandas



