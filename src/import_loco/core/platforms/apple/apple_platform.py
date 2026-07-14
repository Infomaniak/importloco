import logging
import re

from import_loco.core.platforms.platform import Platform

logger = logging.getLogger(__name__)


class ApplePlatform(Platform):
    def _format_source_path(self, language: str, filename: str) -> str:
        return f"{language}.lproj/{filename}"

    def _format_destination_path(self, language: str, filename: str) -> str:
        return f"{language}.lproj/{filename}"

    def post_process(self, destination_path: str, language: str) -> None:
        """Strip Loco export headers from .strings and .stringsdict files."""
        if destination_path.endswith(".stringsdict"):
            self._strip_stringsdict_header(destination_path)
        elif destination_path.endswith(".strings"):
            self._strip_strings_header(destination_path)

    def _strip_strings_header(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        stripped = self._strip_header_comment(content)
        if stripped != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(stripped)
            logger.debug("Stripped header from %s", file_path)

    def _strip_header_comment(self, content: str) -> str:
        stripped_content = content.lstrip()

        if not stripped_content.startswith("/*"):
            return content

        end = stripped_content.find("*/")
        if end == -1:
            return content

        comment = stripped_content[0:end + 2]
        if "Loco" in comment and "export" in comment:
            return stripped_content[end + 2:].lstrip()

        return content

    def _strip_stringsdict_header(self, file_path: str) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        def remove_loco_comment(match):
            comment = match.group(0)
            if "Loco" in comment and "export" in comment:
                return ""
            return comment

        result = re.sub(r'<!--.*?-->', remove_loco_comment, content, count=1, flags=re.DOTALL)
        result = result.lstrip()

        if result != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)
            logger.debug("Stripped header from %s", file_path)
