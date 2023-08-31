# Import Loco

Import strings like a noob.

Designed by ~~Apple~~ iOS team in ~~California~~ Geneva. Inspired by [Ink](https://github.com/LunarX/ink_utils).

## How to use

### Configuration file

Import Loco requires a configuration file to set up your projects.
You need to create a file in your home directory with the name `.import_loco`.
```bash
$ touch ~/.import_loco
```
For each project, add these lines with the values corresponding to your setup:
```
[project_name]
project_root = /Users/.../project/Localizable
loco_key = xxx
```

### Execute the script

To run the script, simply execute the following line in a terminal:
```bash
$ python3 path_to_script/importLoco/main.py {project_name} 
```

You can create an alias in your `.bashrc` to make life easier.
```bash
alias import_loco="python3 path_to_script/importLoco/main.py"
```

---

Fin ! The End! Fine! Fin! Ende!