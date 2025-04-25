import sys
from loco_import import import_and_validate_strings
from loco_import_strategy import STRINGS_LOCO_IMPORT_STRATEGY, PLIST_LOCO_IMPORT_STRATEGY

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: Import Loco requires 1 argument.\n$ import_loco {project_name}')
        sys.exit(1)

    project_name = sys.argv[1]

    import_and_validate_strings(project_name, STRINGS_LOCO_IMPORT_STRATEGY)
