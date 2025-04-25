# Import Loco

Import strings like a noob.

Designed by ~~Apple~~ iOS team in ~~California~~ Geneva. Inspired by [Ink](https://github.com/Infomaniak/ink_utils).

## Install the script

### Python dependencies

Import Loco requires one dependency.
```bash
$ pip3 install requests==2.28.2
```

### Configuration file

Import Loco needs a configuration file to set up your projects.
You need to create a file in your home directory with the name `.import_loco`.
```bash
$ touch ~/.import_loco
```
For each project, add these lines with the values corresponding to your setup:
```
[project_name]
project_root = /Users/.../project
project_localizable = /Users/.../project/.../Localizable
loco_key = xxx
filters = !common
```
The `filters` property is optional.

## Execute the script

To run the script, simply execute the following line in a terminal.
The project name corresponds to the one you added in the `.import_loco` file.
```bash
$ python3 path_to_script/importLoco/main.py {project_name}
```

You can create an alias in your `.bashrc` to make life easier.
```bash
alias import_loco="python3 path_to_script/importLoco/main.py"
```

Then you can call the script as follows:
```bash
import_loco {project_name}
```

---

Fin ! The End! Fine! Fin! Ende!
