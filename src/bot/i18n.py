from pathlib import Path

from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub

LOCALES_DIR = Path(__file__).parent.parent / "locales"

SUPPORTED_LOCALES = ("ru", "en")

_LOCALE_FILES = [
    "main.ftl",
    "survey.ftl",
    "recommendation.ftl",
    "errors.ftl",
    "manager.ftl",
    "order.ftl",
]


def _build_bundle(locale: str) -> FluentBundle:
    return FluentBundle.from_files(
        locale,
        filenames=[str(LOCALES_DIR / locale / f) for f in _LOCALE_FILES],
    )


def create_translator_hub() -> TranslatorHub:
    return TranslatorHub(
        locales_map={
            "ru": ("ru", "en"),
            "en": ("en", "ru"),
        },
        translators=[
            FluentTranslator(locale="ru", translator=_build_bundle("ru")),
            FluentTranslator(locale="en", translator=_build_bundle("en")),
        ],
        root_locale="ru",
    )


def resolve_locale(language_code: str | None) -> str:
    if language_code and language_code in SUPPORTED_LOCALES:
        return language_code
    return "ru"
