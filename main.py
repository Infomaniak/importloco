import sys
from import_translations import StringsImportTranslations

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: Import Loco requires 1 argument.\n$ import_loco {project_name}')
        sys.exit(1)

    project_name = sys.argv[1]

    importer = StringsImportTranslations(project_name)
    importer.import_and_validate_strings()
