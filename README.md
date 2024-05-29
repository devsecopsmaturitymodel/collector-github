
# GitHub Collector for DSOMM metrics

CLI application to list DSOMM related metrics for GitHub repositories.


## Features

- List branch protection-status for repositories 
- List repositories for an organization or for a specific team
- List teams for an organization

These features are implemented as easy to use commands within a Python CLI application.


## Installation
Clone the repository and install required dependencies via `pip`.

```bash
  git clone git@github.com/devsecopsmaturitymodel/collector-github.git
  cd collector-github
  pip install -r requirements.txt
```

### Prerequisites and Dependencies
The prerequisites to install and run the application are:

* a terminal, preferably with ANSI color support
* Python 3+ to execute 
* a GitHub token to access the organization and repositories

Other languages, tools and libraries used:

* [PyGithub](https://pypi.org/project/PyGithub/) as third-party client for GitHub's REST API v3.
* [Click](https://pypi.org/project/click/) for declaring and operating the CLI aspects.
* [python-dotenv](https://pypi.org/project/python-dotenv/) for loading the GitHub token from a dot-env (`.env`) file or from an environment variable directly.
## Run Locally

In order for the application to log in to GitHub, please provide your personal GitHub token (permission for org and repos) as environment variable `GITHUB_TOKEN` or in an `.env` file within the project directory.

Start the CLI application directly from your favourite terminal:
```bash
./collect-github.py --help
```


## Demo
To view available commands:
```shell
$ ./collect-github.py
Usage: collect-github.py [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  repo-status
  repos
  teams
```

To quickly poll the security-status of a specific repository, e.g. `EXAMPLE-ORG/repo-1`:
```shell
$ ./collect-github.py repo-status EXAMPLE-ORG/repo-1
Debug mode is off
Retrieve protected-status of repo EXAMPLE-ORG/repo-1
User USER logged in.
 EXAMPLE-ORG/repo-1.................................... 🛡 has protected default-branch `develop` 
```

## Documentation
For additional insights to research, design and decisions made, please consult the separate [Documentation](./docs).