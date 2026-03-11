from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner
import structlog

from src.bot.keyboards.menu import category_keyboard, main_menu_keyboard
from src.bot.keyboards.survey import step_keyboard, text_input_keyboard
from src.bot.states.survey import SurveyStates
from src.core.enums import Category
from src.infrastructure.survey_config.steps import StepOption, SurveyStep
from src.services.manager_service import ManagerService
from src.services.recommendation_service import RecommendationService
from src.services.survey_service import SurveyService

logger = structlog.get_logger()

router = Router()


@router.callback_query(F.data == "start_survey")
@inject
async def start_survey(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    categories = survey_service.available_categories()
    await message.edit_text(
        i18n.get("select-category"),
        reply_markup=category_keyboard(categories, i18n),
    )
    await state.set_state(SurveyStates.choosing_category)
    await callback.answer()


@router.callback_query(
    SurveyStates.choosing_category,
    F.data.startswith("category:"),
)
@inject
async def category_selected(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    category_value = callback.data.split(":")[1] if callback.data else ""
    category = Category(category_value)
    steps = survey_service.get_steps(category)

    await state.update_data(
        category=category_value,
        steps=[_step_to_dict(s) for s in steps],
        current_step=0,
        answers={},
    )

    await _show_step(message, steps[0], state, i18n, show_back=False)
    await callback.answer()


# --- Single select ---
@router.callback_query(
    SurveyStates.answering_step,
    F.data.startswith("survey_answer:"),
)
@inject
async def handle_single_answer(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
    recommendation_service: FromDishka[RecommendationService],
    manager_service: FromDishka[ManagerService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    _, step_key, value = callback.data.split(":", 2) if callback.data else ""

    data = await state.get_data()
    answers: dict = data["answers"]
    answers[step_key] = [value]
    await state.update_data(answers=answers)

    await _advance_step(
        message,
        state,
        i18n,
        survey_service,
        recommendation_service,
        manager_service,
    )
    await callback.answer()


# --- Multi select toggle ---
@router.callback_query(
    SurveyStates.multi_select_step,
    F.data.startswith("survey_toggle:"),
)
async def handle_multi_toggle(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    _, step_key, value = callback.data.split(":", 2) if callback.data else ""

    data = await state.get_data()
    answers: dict = data["answers"]
    selected: list = answers.get(step_key, [])

    step_dict = data["steps"][data["current_step"]]
    max_sel = step_dict.get("max_selections")

    if value in selected:
        selected.remove(value)
    elif max_sel is None or len(selected) < max_sel:
        selected.append(value)
    else:
        await callback.answer(
            i18n.get("multi-select-max", max=str(max_sel)),
        )
        return

    answers[step_key] = selected
    await state.update_data(answers=answers)

    step = _dict_to_step(step_dict)
    show_back = data["current_step"] > 0
    await message.edit_reply_markup(
        reply_markup=step_keyboard(
            step,
            i18n,
            selected=selected,
            show_back=show_back,
        ),
    )
    await callback.answer()


# --- Multi select done ---
@router.callback_query(
    SurveyStates.multi_select_step,
    F.data == "done",
)
@inject
async def handle_multi_done(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
    recommendation_service: FromDishka[RecommendationService],
    manager_service: FromDishka[ManagerService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    await _advance_step(
        message,
        state,
        i18n,
        survey_service,
        recommendation_service,
        manager_service,
    )
    await callback.answer()


# --- Skip ---
@router.callback_query(F.data == "skip")
@inject
async def handle_skip(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
    recommendation_service: FromDishka[RecommendationService],
    manager_service: FromDishka[ManagerService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    await _advance_step(
        message,
        state,
        i18n,
        survey_service,
        recommendation_service,
        manager_service,
    )
    await callback.answer()


# --- Back ---
@router.callback_query(F.data == "back")
@inject
async def handle_back(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    data = await state.get_data()
    current = data["current_step"]

    if current <= 0:
        await state.set_state(SurveyStates.choosing_category)
        categories = survey_service.available_categories()
        await message.edit_text(
            i18n.get("select-category"),
            reply_markup=category_keyboard(categories, i18n),
        )
        await callback.answer()
        return

    prev_index = current - 1
    steps = data["steps"]
    prev_step = _dict_to_step(steps[prev_index])

    answers: dict = data["answers"]
    current_step_dict = steps[current]
    answers.pop(current_step_dict["key"], None)

    await state.update_data(current_step=prev_index, answers=answers)

    prev_selected = answers.get(prev_step.key, [])

    await _show_step(
        message,
        prev_step,
        state,
        i18n,
        show_back=prev_index > 0,
        selected=prev_selected,
    )
    await callback.answer()


# --- Text input ---
@router.message(SurveyStates.text_input_step)
@inject
async def handle_text_input(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: FromDishka[SurveyService],
    recommendation_service: FromDishka[RecommendationService],
    manager_service: FromDishka[ManagerService],
) -> None:
    data = await state.get_data()
    step_dict = data["steps"][data["current_step"]]

    values = survey_service.parse_text_input(message.text or "")

    answers: dict = data["answers"]
    answers[step_dict["key"]] = values
    await state.update_data(answers=answers)

    await _advance_step(
        message,
        state,
        i18n,
        survey_service,
        recommendation_service,
        manager_service,
    )


# --- Cancel ---
@router.callback_query(F.data == "cancel")
async def handle_cancel(
    callback: CallbackQuery,
    state: FSMContext,
    i18n: TranslatorRunner,
) -> None:
    message = callback.message
    if not isinstance(message, Message):
        await callback.answer()
        return

    await state.clear()
    await message.edit_text(
        i18n.get("survey-cancelled"),
        reply_markup=main_menu_keyboard(i18n),
    )
    await callback.answer()


# --- Helpers ---


async def _advance_step(
    message: Message,
    state: FSMContext,
    i18n: TranslatorRunner,
    survey_service: SurveyService,
    recommendation_service: RecommendationService,
    manager_service: ManagerService,
) -> None:
    data = await state.get_data()
    current = data["current_step"]
    steps = data["steps"]
    next_index = current + 1

    if next_index < len(steps):
        await state.update_data(current_step=next_index)
        step = _dict_to_step(steps[next_index])
        await _show_step(message, step, state, i18n, show_back=True)
        return

    # --- Survey complete → get recommendations immediately ---
    category = Category(data["category"])
    answers = data["answers"]
    telegram_id = message.chat.id

    survey = await survey_service.complete_survey(
        telegram_id=telegram_id,
        category=category,
        answers=answers,
    )

    await state.update_data(survey_completed=True)

    # show loading
    await message.edit_text(i18n.get("rec-loading"))

    result = await recommendation_service.get_recommendations(survey)

    if not result.ai_succeeded or not result.recommendations:
        warning = result.warning_message or i18n.get("rec-ai-failed-default")
        await manager_service.handle_ai_failure(
            telegram_id=telegram_id,
            survey=survey,
            error=warning,
        )
        await message.edit_text(
            i18n.get("rec-ai-failed", warning=warning),
            reply_markup=main_menu_keyboard(i18n),
        )
        return

    # format recommendations
    from src.bot.handlers.recommendation import recommendation_keyboard

    text_parts = [i18n.get("rec-title"), ""]

    if result.warning_message:
        text_parts.append(f"⚠️ {result.warning_message}\n")

    for idx, rec in enumerate(result.recommendations, 1):
        text_parts.append(
            f"<b>{idx}. {rec.product.brand} — {rec.product.name}</b>\n"
            f"   💰 ${rec.product.price}\n"
            f"   ⭐ {rec.product.rating}\n"
            f"   💬 {rec.reasoning}\n",
        )

    rec_data = [
        {
            "product_id": r.product.id,
            "name": r.product.name,
            "brand": r.product.brand,
            "price": str(r.product.price),
            "reasoning": r.reasoning,
        }
        for r in result.recommendations
    ]
    await state.update_data(recommendations=rec_data)

    await message.edit_text(
        "\n".join(text_parts),
        reply_markup=recommendation_keyboard(i18n),
        parse_mode="HTML",
    )


async def _show_step(
    message: Message,
    step: SurveyStep,
    state: FSMContext,
    i18n: TranslatorRunner,
    show_back: bool = False,
    selected: list[str] | None = None,
) -> None:
    question = i18n.get(step.question_key)

    if step.is_text_input:
        await state.set_state(SurveyStates.text_input_step)
        await message.edit_text(
            question,
            reply_markup=text_input_keyboard(i18n, show_back=show_back),
        )
    elif step.is_multi_select:
        await state.set_state(SurveyStates.multi_select_step)
        await message.edit_text(
            question,
            reply_markup=step_keyboard(
                step,
                i18n,
                selected=selected or [],
                show_back=show_back,
            ),
        )
    else:
        await state.set_state(SurveyStates.answering_step)
        await message.edit_text(
            question,
            reply_markup=step_keyboard(step, i18n, show_back=show_back),
        )


def _step_to_dict(step: SurveyStep) -> dict:
    return {
        "key": step.key,
        "question_key": step.question_key,
        "options": [{"value": o.value, "label_key": o.label_key} for o in step.options],
        "is_multi_select": step.is_multi_select,
        "is_skippable": step.is_skippable,
        "is_text_input": step.is_text_input,
        "max_selections": step.max_selections,
    }


def _dict_to_step(d: dict) -> SurveyStep:
    return SurveyStep(
        key=d["key"],
        question_key=d["question_key"],
        options=[
            StepOption(value=o["value"], label_key=o["label_key"])
            for o in d.get("options", [])
        ],
        is_multi_select=d.get("is_multi_select", False),
        is_skippable=d.get("is_skippable", False),
        is_text_input=d.get("is_text_input", False),
        max_selections=d.get("max_selections"),
    )

