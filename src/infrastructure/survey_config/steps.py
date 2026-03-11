from dataclasses import dataclass, field


@dataclass(frozen=True)
class StepOption:
    value: str
    label_key: str


@dataclass(frozen=True)
class SurveyStep:
    key: str
    question_key: str
    options: list[StepOption] = field(default_factory=list)
    is_multi_select: bool = False
    is_skippable: bool = False
    is_text_input: bool = False
    max_selections: int | None = None

