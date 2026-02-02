from import_loco.core.platforms.platform import Platform


class ApplePlatform(Platform):
    def _format_source_path(self, language: str, filename: str) -> str:
        return f"{language}.lproj/{filename}"

    def _format_destination_path(self, language: str, filename: str) -> str:
        return f"{language}.lproj/{filename}"
