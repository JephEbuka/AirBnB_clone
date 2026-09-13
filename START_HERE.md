# Create the project files together

You do not need to create or upload each file separately. Choose one setup
method below; both contain the same project.

## Update the earlier package

Download the latest `setup_airbnb.py` and save it in your existing
`AirBnB_clone` repository folder. Open a terminal in that folder and run:

```bash
python3 setup_airbnb.py --target . --update
python3 -m unittest discover tests
```

This installs the six concrete model classes, their test files and storage
support for all seven model types. It also updates the basic console commands.
The update preserves an existing `AUTHORS`, `file.json`, Git metadata and
unrelated files. Before replacing changed project files, it creates a ZIP
backup beside your repository and prints its location. Identical files are
left alone, so you can rerun the same command.

The earlier package was limited to tasks 0–5. These additional models and
tests address the later model checks included in the reported checker output.

## Method 1: one setup script

Download `setup_airbnb.py`, open a terminal in its download folder, and run:

```bash
python3 setup_airbnb.py --author "Your Full Name <your-email@example.com>"
```

Replace the name and email before running. The script creates the complete
`AirBnB_clone` folder beside your terminal's current location. It runs offline
using Python's standard library. Repeat `--author` for each teammate.

To put the files into an existing local clone, specify its directory:

```bash
python3 setup_airbnb.py --target /path/to/AirBnB_clone \
  --author "Your Full Name <your-email@example.com>"
```

Without `--update`, the script detects conflicting files before writing and
stops if any exist. Use the update instructions above to update an existing
project with a backup. Identical files are kept in either mode.

On Windows, use `py` instead of `python3` if needed.

## Method 2: one ZIP archive

Download and extract `AirBnB_clone.zip`. It contains one
`AirBnB_clone` folder with the project code and tests. Replace the example
contributor in `AUTHORS` before submitting. Do not upload the ZIP itself as
the project: the repository must contain the extracted files and folders.

## Verify the project

Open a terminal in `AirBnB_clone` and run:

```bash
python3 -m unittest discover tests
python3 console.py
```

Type `help` in the console, or `quit` to leave it. See `README.md` for the
style check, non-interactive test command and usage examples.

To run an individual test file, include its `.py` suffix, or use a dotted
module name:

```bash
python3 -m unittest tests/test_models/test_user.py
python3 -m unittest tests.test_models.test_user
```

The full test discovery command above runs all six model test modules too.

## Put all files on GitHub together

For an existing local Git clone, use its repository root. If you have just
generated a new folder, create a GitHub repository named `AirBnB_clone` with
an initial README, clone it locally, and use the setup script with that clone
as `--target`. If the initial README conflicts, generate into a separate
folder, then copy the generated files and folders into the clone after
reviewing them. Keep the clone's Git metadata in place.

Inside the local Git clone, create a branch:

```bash
git checkout -b tasks-0-5
```

After the files are in place and tests pass, stage the whole project, review
what is staged, and commit it together:

```bash
git add .
git diff --cached --stat
git diff --cached
git commit -m "Implement BaseModel and JSON file storage"
git push -u origin tasks-0-5
```

On GitHub, open a pull request from `tasks-0-5` into your repository's default
branch, review it with your teammate if applicable, and merge when ready.
If your checker uses the default branch, the code must be merged there before
the checker can see it. The setup script does not run Git or publish anything.
