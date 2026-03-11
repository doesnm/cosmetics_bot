from src.core.enums import Formulation, SkinConcerns, SkinType, SkincareSubcategory
from src.infrastructure.survey_config.base_flow import BaseSurveyFlow
from src.infrastructure.survey_config.steps import StepOption, SurveyStep


class SkincareSurveyFlow(BaseSurveyFlow):
    def _category_steps(self) -> list[SurveyStep]:
        return [
            self._subcategory_step(),
            self._skin_type_step(),
            self._skin_concerns_step(),
            self._formulation_step(),
            self._ingredients_step(),
        ]

    @staticmethod
    def _subcategory_step() -> SurveyStep:
        return SurveyStep(
            key="subcategory",
            question_key="step-skincare-subcategory-question",
            options=[
                StepOption(
                    value=SkincareSubcategory.MOISTURIZERS,
                    label_key="step-skincare-sub-moisturizers",
                ),
                StepOption(
                    value=SkincareSubcategory.CLEANSERS,
                    label_key="step-skincare-sub-cleansers",
                ),
                StepOption(
                    value=SkincareSubcategory.SERUMS,
                    label_key="step-skincare-sub-serums",
                ),
                StepOption(
                    value=SkincareSubcategory.TONERS,
                    label_key="step-skincare-sub-toners",
                ),
                StepOption(
                    value=SkincareSubcategory.CREAMS,
                    label_key="step-skincare-sub-creams",
                ),
                StepOption(
                    value=SkincareSubcategory.EYE_CARE,
                    label_key="step-skincare-sub-eye-care",
                ),
                StepOption(
                    value=SkincareSubcategory.ACNE, label_key="step-skincare-sub-acne"
                ),
                StepOption(
                    value=SkincareSubcategory.EXFOLIATORS,
                    label_key="step-skincare-sub-exfoliators",
                ),
                StepOption(
                    value=SkincareSubcategory.SPOT_CARE,
                    label_key="step-skincare-sub-spot-care",
                ),
                StepOption(
                    value=SkincareSubcategory.FACE_MIST,
                    label_key="step-skincare-sub-face-mist",
                ),
                StepOption(
                    value=SkincareSubcategory.FACE_OIL,
                    label_key="step-skincare-sub-face-oil",
                ),
                StepOption(
                    value=SkincareSubcategory.GIFT_SETS,
                    label_key="step-skincare-sub-gift-sets",
                ),
                StepOption(
                    value=SkincareSubcategory.DONT_KNOW,
                    label_key="step-skincare-sub-dont-know",
                ),
            ],
        )

    @staticmethod
    def _skin_type_step() -> SurveyStep:
        return SurveyStep(
            key="skin_type",
            question_key="step-skin-type-question",
            options=[
                StepOption(
                    value=SkinType.COMBINATION, label_key="step-skin-type-combination"
                ),
                StepOption(value=SkinType.DRY, label_key="step-skin-type-dry"),
                StepOption(value=SkinType.OILY, label_key="step-skin-type-oily"),
                StepOption(
                    value=SkinType.SENSITIVE, label_key="step-skin-type-sensitive"
                ),
                StepOption(value="dont_know", label_key="step-skin-type-dont-know"),
            ],
        )

    @staticmethod
    def _skin_concerns_step() -> SurveyStep:
        return SurveyStep(
            key="skin_concerns",
            question_key="step-skin-concerns-question",
            options=[
                StepOption(
                    value=SkinConcerns.MOISTURISING,
                    label_key="step-skin-concerns-moisturising",
                ),
                StepOption(
                    value=SkinConcerns.SOOTHING, label_key="step-skin-concerns-soothing"
                ),
                StepOption(
                    value=SkinConcerns.WELL_AGING, label_key="step-skin-concerns-aging"
                ),
                StepOption(
                    value=SkinConcerns.VILISIBLE_PORES,
                    label_key="step-skin-concerns-pores",
                ),
                StepOption(
                    value=SkinConcerns.DEEP_CLEANSING,
                    label_key="step-skin-concerns-deep-cleansing",
                ),
                StepOption(
                    value=SkinConcerns.BLACKHEADS,
                    label_key="step-skin-concerns-blackheads",
                ),
                StepOption(
                    value=SkinConcerns.BRIGHTENING,
                    label_key="step-skin-concerns-brightening",
                ),
                StepOption(
                    value=SkinConcerns.DULLNESS, label_key="step-skin-concerns-dullness"
                ),
                StepOption(
                    value=SkinConcerns.ACNE, label_key="step-skin-concerns-acne"
                ),
                StepOption(
                    value=SkinConcerns.SCARRING, label_key="step-skin-concerns-scarring"
                ),
                StepOption(
                    value=SkinConcerns.PUFFINESS,
                    label_key="step-skin-concerns-puffiness",
                ),
                StepOption(
                    value=SkinConcerns.SUNCARE_COOLING,
                    label_key="step-skin-concerns-suncare",
                ),
            ],
            is_multi_select=True,
            max_selections=3,
        )

    @staticmethod
    def _formulation_step() -> SurveyStep:
        return SurveyStep(
            key="formulation",
            question_key="step-formulation-question",
            options=[
                StepOption(value=Formulation.FLUID, label_key="step-formulation-fluid"),
                StepOption(value=Formulation.CREAM, label_key="step-formulation-cream"),
                StepOption(value=Formulation.TONER, label_key="step-formulation-toner"),
                StepOption(
                    value=Formulation.AMPOULE, label_key="step-formulation-ampoule"
                ),
                StepOption(value=Formulation.GEL, label_key="step-formulation-gel"),
                StepOption(value=Formulation.BALM, label_key="step-formulation-balm"),
                StepOption(value=Formulation.OIL, label_key="step-formulation-oil"),
                StepOption(
                    value=Formulation.BUBBLE, label_key="step-formulation-bubble"
                ),
                StepOption(
                    value=Formulation.POWDER, label_key="step-formulation-powder"
                ),
                StepOption(value=Formulation.ANY, label_key="step-formulation-any"),
            ],
            is_skippable=True,
        )

    @staticmethod
    def _ingredients_step() -> SurveyStep:
        return SurveyStep(
            key="preferred_ingredients",
            question_key="step-ingredients-question",
            options=[
                StepOption(
                    value="hyaluronic_acid", label_key="step-ingredient-hyaluronic"
                ),
                StepOption(value="panthenol", label_key="step-ingredient-panthenol"),
                StepOption(
                    value="niacinamide", label_key="step-ingredient-niacinamide"
                ),
                StepOption(value="centella", label_key="step-ingredient-centella"),
                StepOption(value="ceramide", label_key="step-ingredient-ceramide"),
                StepOption(value="peptide", label_key="step-ingredient-peptide"),
                StepOption(value="collagen", label_key="step-ingredient-collagen"),
                StepOption(
                    value="madecassoside", label_key="step-ingredient-madecassoside"
                ),
                StepOption(value="vitamin_c", label_key="step-ingredient-vitamin-c"),
                StepOption(value="retinol", label_key="step-ingredient-retinol"),
                StepOption(value="tea_tree", label_key="step-ingredient-tea-tree"),
                StepOption(value="squalane", label_key="step-ingredient-squalane"),
                StepOption(
                    value="glutathione", label_key="step-ingredient-glutathione"
                ),
                StepOption(
                    value="beta_glucan", label_key="step-ingredient-beta-glucan"
                ),
                StepOption(value="bifida", label_key="step-ingredient-bifida"),
                StepOption(value="aha", label_key="step-ingredient-aha"),
                StepOption(value="bha", label_key="step-ingredient-bha"),
                StepOption(value="pha", label_key="step-ingredient-pha"),
                StepOption(value="bakuchiol", label_key="step-ingredient-bakuchiol"),
                StepOption(value="snail_mucin", label_key="step-ingredient-snail"),
            ],
            is_multi_select=True,
            is_skippable=True,
            max_selections=5,
        )
