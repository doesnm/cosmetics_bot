from enum import StrEnum


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNISEX = "unisex"


class AgeRange(StrEnum):
    UNDER_18 = "under_18"
    AGE_18_24 = "18_24"
    AGE_25_34 = "25_34"
    AGE_35_44 = "35_44"
    AGE_45_PLUS = "45_plus"


class Category(StrEnum):
    SKINCARE = "skincare"


class SkinType(StrEnum):
    OILY = "oily"
    DRY = "dry"
    COMBINATION = "combination"
    NORMAL = "normal"
    SENSITIVE = "sensitive"


class SkinConcerns(StrEnum):
    MOISTURISING = "moisturising"
    SOOTHING = "soothing"
    WELL_AGING = "well_aging"
    VILISIBLE_PORES = "visible_pores"
    DEEP_CLEANSING = "deep_cleansing"
    BLACKHEADS = "blackheads"
    BRIGHTENING = "brightening"
    DULLNESS = "dullness"
    ACNE = "acne"
    SCARRING = "scarring"
    PUFFINESS = "puffiness"
    SUNCARE_COOLING = "suncare_cooling"


class Formulation(StrEnum):
    FLUID = "fluid"
    CREAM = "cream"
    TONER = "toner"
    AMPOULE = "ampoule"
    GEL = "gel"
    BALM = "balm"
    OIL = "oil"
    BUBBLE = "bubble"
    POWDER = "powder"
    ANY = "any"


class SkincareSubcategory(StrEnum):
    MOISTURIZERS = "moisturizers"
    CLEANSERS = "cleansers"
    SERUMS = "serums"
    TONERS = "toners"
    CREAMS = "creams"
    EYE_CARE = "eye_care"
    ACNE = "acne"
    EXFOLIATORS = "exfoliators"
    SPOT_CARE = "spot_care"
    FACE_MIST = "face_mist"
    FACE_OIL = "face_oil"
    GIFT_SETS = "gift_sets"
    DONT_KNOW = "dont_know"


class BudgetRange(StrEnum):
    LOW = "low"  # < $15
    MEDIUM = "medium"  # $15-40
    HIGH = "high"  # $40-80
    PREMIUM = "premium"  # $80+
