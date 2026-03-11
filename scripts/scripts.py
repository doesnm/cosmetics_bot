import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.infrastructure.database.models.product import ProductORM
from src.config import Settings


SAMPLE_PRODUCTS = [
    {
        "name": "Advanced Snail 96 Mucin Power Essence",
        "brand": "COSRX",
        "category": "skincare",
        "gender": "unisex",
        "price": 21.00,
        "currency": "USD",
        "rating": 4.6,
        "description": "Lightweight essence with 96% snail mucin",
        "attributes": {
            "subcategory": ["serums"],
            "skin_type": ["dry", "combination", "normal", "sensitive"],
            "skin_concerns": ["moisturising", "dullness", "scarring"],
            "formulation": ["fluid"],
            "ingredients": ["snail_mucin", "hyaluronic_acid"],
        },
    },
    {
        "name": "Centella Unscented Serum",
        "brand": "PURITO",
        "category": "skincare",
        "gender": "unisex",
        "price": 16.00,
        "currency": "USD",
        "rating": 4.5,
        "description": "Fragrance-free soothing serum with centella",
        "attributes": {
            "subcategory": ["serums"],
            "skin_type": ["sensitive", "combination", "normal"],
            "skin_concerns": ["soothing", "redness", "moisturising"],
            "formulation": ["fluid"],
            "ingredients": ["centella", "niacinamide", "panthenol"],
        },
    },
    {
        "name": "Low pH Good Morning Gel Cleanser",
        "brand": "COSRX",
        "category": "skincare",
        "gender": "unisex",
        "price": 12.00,
        "currency": "USD",
        "rating": 4.4,
        "description": "Gentle low-pH gel cleanser",
        "attributes": {
            "subcategory": ["cleansers"],
            "skin_type": ["oily", "combination", "normal"],
            "skin_concerns": ["deep_cleansing", "acne"],
            "formulation": ["gel"],
            "ingredients": ["tea_tree", "bha"],
        },
    },
    {
        "name": "Moisturizing Cream",
        "brand": "illiyoon",
        "category": "skincare",
        "gender": "unisex",
        "price": 18.00,
        "currency": "USD",
        "rating": 4.7,
        "description": "Ceramide-rich moisturizer for dry skin",
        "attributes": {
            "subcategory": ["moisturizers"],
            "skin_type": ["dry", "sensitive", "normal"],
            "skin_concerns": ["moisturising", "soothing"],
            "formulation": ["cream"],
            "ingredients": ["ceramide", "panthenol"],
        },
    },
    {
        "name": "AHA/BHA Clarifying Treatment Toner",
        "brand": "COSRX",
        "category": "skincare",
        "gender": "unisex",
        "price": 14.00,
        "currency": "USD",
        "rating": 4.3,
        "description": "Exfoliating toner with AHA and BHA",
        "attributes": {
            "subcategory": ["toners"],
            "skin_type": ["oily", "combination"],
            "skin_concerns": ["blackheads", "visible_pores", "deep_cleansing"],
            "formulation": ["toner"],
            "ingredients": ["aha", "bha"],
        },
    },
    {
        "name": "Vitamin C Serum",
        "brand": "Klairs",
        "category": "skincare",
        "gender": "unisex",
        "price": 23.00,
        "currency": "USD",
        "rating": 4.4,
        "description": "Gentle vitamin C serum for brightening",
        "attributes": {
            "subcategory": ["serums"],
            "skin_type": ["normal", "combination", "sensitive"],
            "skin_concerns": ["brightening", "dullness", "dark_spots"],
            "formulation": ["fluid"],
            "ingredients": ["vitamin_c", "centella"],
        },
    },
    {
        "name": "Aloe BHA Skin Toner",
        "brand": "Benton",
        "category": "skincare",
        "gender": "unisex",
        "price": 15.00,
        "currency": "USD",
        "rating": 4.3,
        "description": "Soothing toner with aloe and BHA",
        "attributes": {
            "subcategory": ["toners"],
            "skin_type": ["oily", "combination", "sensitive"],
            "skin_concerns": ["acne", "soothing", "visible_pores"],
            "formulation": ["toner"],
            "ingredients": ["bha", "snail_mucin"],
        },
    },
    {
        "name": "Retinol Cream 0.5",
        "brand": "Beauty of Joseon",
        "category": "skincare",
        "gender": "unisex",
        "price": 19.00,
        "currency": "USD",
        "rating": 4.5,
        "description": "Gentle retinol cream for anti-aging",
        "attributes": {
            "subcategory": ["creams"],
            "skin_type": ["normal", "combination", "dry"],
            "skin_concerns": ["well_aging", "brightening"],
            "formulation": ["cream"],
            "ingredients": ["retinol", "niacinamide", "peptide"],
        },
    },
]


async def seed() -> None:
    settings = Settings()
    engine = create_async_engine(settings.database_url)
    session_maker = async_sessionmaker(engine, class_=AsyncSession)

    async with session_maker() as session:
        for product_data in SAMPLE_PRODUCTS:
            product = ProductORM(**product_data)
            session.add(product)

        await session.commit()
        print(f"Seeded {len(SAMPLE_PRODUCTS)} products")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
