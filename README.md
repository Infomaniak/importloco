# Import Loco

Import strings like a noob.

Designed by ~~Apple~~ iOS team in ~~California~~ Geneva. Inspired by [Ink](https://github.com/LunarX/ink_utils).

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
project_root = /Users/.../project/Localizable
loco_key = xxx
```

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

## One more thing

If you are a cool guy, you can use a Raycast script.

```bash
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Import Loco
# @raycast.mode compact

# Optional parameters:
# @raycast.icon 🌐
# @raycast.argument1 { "type": "text", "placeholder": "kmail" }

# Documentation:
# @raycast.description Import Loco strings
# @raycast.author valentinperignon
# @raycast.authorURL https://raycast.com/valentinperignon

python3 path_to_script/importLoco/main.py $1
```

---

Fin ! The End! Fine! Fin! Ende!