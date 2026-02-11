# test.virgin.galactic.hil


## Run Code
To run the pytest tests, run the following Makefile commands from the root directory of the project:

	make setup
	make build
	make test

## Makefile Commands Explained
### Make setup
This command will create a virtual environment.

### Make build
This command will install the required packages.

### Make test
This command will run all pytest tests.

### Make test-hardware
Run only hardware simulation tests.

	make test-hardware

### Make test-api
Run only API tests.

	make test-api

## Allure Reports Setup
Allure results are written to `allure-results/` by pytest. To view a local report, install the Allure CLI.

macOS:

	pip install allure-pytest
	brew install allure

Windows (PowerShell):

	pip install allure-pytest
	choco install allure-commandline

Then generate/open the report:

	allure generate allure-results -o allure-report --clean
	allure open allure-report

## Hardware Simulation Tests
Flight-control hardware simulations live under `tests/hardware/`. Run only those tests with:

	pytest -m hardware -v

The Jenkins Pipeline in `Jenkinsfile` runs the full test suite and publishes Allure results from `allure-results/`.

## API Tests
API tests live under `tests/api/` and use a local in-memory HTTP server, so they do not require external network access.

	pytest -m api -v

## Jenkins Pipeline Job
This repo includes a `Jenkinsfile` for a Pipeline job. To add it in Jenkins:

1. Install the Allure Jenkins plugin and configure the Allure CLI in **Manage Jenkins → Global Tool Configuration**.
2. Create a new Pipeline job.
3. Under **Pipeline**, set **Definition** to **Pipeline script from SCM**.
4. Choose your SCM (Git) and point it at this repository.
5. Set the **Script Path** to `Jenkinsfile`.
6. Save and run the job.
