
create tasks from these and work on them:

convert the project to use uv for dependency management

verify that everything works correctly afterwards. make sure tests and pre-commit pass, try and test that the project works well

create makefile target for building a docker for this project, that's easy to run. Ideally in README there should be example where you can run it with one command against sqlite.


the project should be able to run against sqlite or posgres depending on env variable

tests should run against both postgres and sqlite, kinda two sets.?
I imagine this will be difficuilt, break it down into multiple tasks first

use python3.12 everywhere

make sure deps are upgraded, pre-commit autoupgrade etc


typing annotation where applicable? basically for all functions? bump version in pyproject


go trough the codebase and remove comments that aren't necessary. only keep the most important ones that point to behaviour not undestood from the code
