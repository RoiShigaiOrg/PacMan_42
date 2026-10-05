# Contribution

This Markdown file is aiming to the devs wanting to contribute to the project.

# Installation

This repo use CI/CD pipelines and is construct with one 'main' branch where the release version of the project is deployed, and the 'dev' branch where development and contribution evaluation occurs. Every pull request must be evaluated before merging, the evaluation consist of passing some automated test using pytest and the tests within the 'tests' folder, norm validation (flake8 and mypy on src folder) and direct Validation from the dev who contribute to the project the owner of the repo (**RoiShigai**). Every feature and implementation details can be discussed and must be solved before merging the contribution.

## Clone repo

To start contributing first you have to clone the 'dev' branch of the repo
```bash
git clone --single-branch --branch dev git@github.com:RoiShigaiOrg/PacMan_42.git
```

Then open a new branch with the explicit name of your working feature contribution
```bash
git checkout -b [feature_name]
```

## 42 Mlx Library
This project depends of the 42 mlx Graphic library.
This library contain 2 whl file depending of the system used by the dev:
- ubuntu (standard)
- fedora

Change within the requirements.txt which mlx version you to use.

## dependancy 

The virtual environment manager used within this project is UV.
To install the environment you can:
- setup the right environment from scratch using the 'requirements-dev.txt'
```bash
uv pip install -r requirements-dev.txt
```

- Synchronize with uv.lock file present in the repo (depreciate)
```bash
uv sync uv.lock
```

### Adding dependency
Adding new dependencies to the project is strictly prohibited, except in exceptional cases approved by the repository owner. In most case any added dependencies will result to refused Pull Request until the issue is solved.

## Pull Request and Evaluation

### Pull Request

After developing the new feature you must create a pull request to the dev branch.
First of all GIT PULL !
```bash
git pull dev [branch-name]
```

This can be done in 2 ways:
1) From the command-line
```bash
gh pr create \
--base dev \
--head dev/[branch name] \ OR --head $(git branch --show-current) <- depreciate
--title "My feature" \
--body "My feature description"
```
2) Push to the dev branch
``` bash
git push dev [branch-name]
```
And open the pull request within github (Green button to check PR).
Verify that you are making a pull request on the dev branch and not the main branch then open the Pull Request, give it a title, a description.

### Evaluation

As discussed before, each PR will be evaluated and must be approved by another contributer of the project.

#### Being evaluated

After opening your pull request if it passed all the automated test, you will have to wait the approving from another contributor of the project, this can take some times (so chill go outside touch some grass). And discussion can be opened and some changes can be asked during the review. 
If all of the discussion has  been solved and all test has been passed, congratulation you can merge your branch with the dev branch !

#### Evaluate a Pull Request

Sometimes you will have to evaluate the Pull Request from another contributor.

Check the file changes and the code from the pull request, if there is something wrong with it open a discussion about the implementation.

You can add some test directly to the PR branch so you can test some potentially omitted test case.
```bash
git fetch dev
git checkout [branch-name]
```

Add some test in the tests folder and run
```bash
uv run pytest tests
```

## Test Framework
This project use pytest as the main Framework for unit test

Create a Python test file for the feature you are developing and write in it some test
*Example in tests folder*
```bash
touch test_my_feature.py
```
The test added by your feature will be automatically being added to the Git Action Automatided test and being run at every PR.

You can run all the test at the root of the project with:
```bash
uv run pytest tests
```
