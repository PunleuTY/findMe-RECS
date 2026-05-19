```
# 🧠 BenefitMe Synthetic E-Commerce Dataset Generator Prompt

You are a data generation engine for an e-commerce recommendation system.

Your task is to generate a **synthetic product dataset** for a marketplace called “BenefitMe”.

You must follow the schema, taxonomy, and constraints exactly. Do not invent new categories or sub-categories outside what is defined below.

---

# 📦 OUTPUT FORMAT RULES

- Output format: **JSON Lines (one product per line)**
- No explanations, no comments, no markdown in output
- Each product must be valid JSON
- Ensure all fields are present
- Ensure values are realistic and consistent across fields

---

# 🧬 MASTER PRODUCT SCHEMA

```json
{
  "product_id": "string",
  "name": "string",
  "category": "string",
  "sub_category": "string",
  "gender_target": "men | women | kids | unisex",
  "age_group": "infant | child | teen | adult",
  "brand": "string",
  "price": "float",
  "discount": "float",
  "final_price": "float",
  "color": ["string"],
  "size_range": ["XS","S","M","L","XL"],
  "material": ["string"],
  "season": "summer | winter | all-season | spring | autumn",
  "style": "casual | formal | streetwear | sporty | traditional",
  "rating": "float (1-5)",
  "review_count": "int",
  "popularity_score": "float (1-5)",
  "stock": "int",
  "tags": ["string"],
  "created_at": "datetime"
}


🧭 CATEGORY TAXONOMY (STRICT — DO NOT MODIFY)
👕 Fashion & Apparel
Men’s Clothing
T-shirts
Shirts (formal)
Shirts (casual)
Jeans
Trousers
Jackets
Traditional wear
Women’s Clothing
Dresses
Tops / Blouses
Skirts
Jeans / Pants
Outerwear
Traditional wear
Kids’ Clothing
Boys clothing
Girls clothing
Infant wear
Footwear
Sneakers
Formal shoes
Sandals / Slippers
Boots
Accessories
Bags (backpacks, handbags)
Belts
Hats / Caps
Wallets
📱 Electronics & Devices
Mobile Phones
Android phones
iPhones
Feature phones
Laptops & Computers
Laptops
Desktops
Monitors
PC components
Audio Devices
Headphones
Earbuds
Speakers
Smart Devices
Smartwatches
Smart home devices
Fitness trackers
Accessories
Chargers
Cables
Power banks
Cases
🏠 Home & Living
Furniture
Beds
Tables
Chairs
Sofas
Storage
Kitchen & Dining
Cookware
Utensils
Dinnerware
Appliances
Home Decor
Wall art
Lighting
Carpets
Curtains
Cleaning Supplies
Detergents
Cleaning tools
Disinfectants
💄 Beauty & Personal Care
Skincare
Face wash
Moisturizer
Sunscreen
Serums
Makeup
Lipstick
Foundation
Eye makeup
Brushes
Hair Care
Shampoo
Conditioner
Hair treatments
Personal Care
Soap
Deodorant
Oral care
🍜 Food & Groceries
Fresh Food
Vegetables
Fruits
Meat & seafood
Packaged Food
Snacks
Instant noodles
Cereals
Beverages
Soft drinks
Coffee / Tea
Juices
Household Essentials
Rice / grains
Cooking oil
Condiments
📚 Books & Education
Academic Books
Computer Science
Mathematics
Business
Self-development
Productivity
Communication
Leadership
Children Books
Story books
Learning books
Stationery
Notebooks
Pens
Art supplies
🏃 Sports & Outdoors
Fitness Equipment
Dumbbells
Yoga mats
Resistance bands
Sports Gear
Football
Basketball
Badminton
Outdoor Gear
Camping tents
Backpacks
Water bottles
🧸 Toys & Baby Products
Toys
Educational toys
Action figures
Puzzle games
Baby Care
Diapers
Baby food
Baby skincare
Baby Gear
Strollers
Car seats
Cribs
🚗 Automotive
Car Accessories
Seat covers
Air fresheners
Phone mounts
Maintenance
Engine oil
Cleaning kits
Tires
⚙️ GENERATION RULES
1. Consistency Rules
category must match sub_category exactly
gender_target must match product type
age_group must be logically correct
materials must match category
2. Pricing Rules
T-shirts: 5–25
Shirts: 10–40
Jeans: 20–60
Jackets: 30–120
Shoes: 15–100
Bags: 10–80
Electronics: 50–1500
Beauty: 3–80
Groceries: 1–50

final_price = price - (price × discount)

discount range: 0.0 – 0.4

3. Popularity Logic
rating: 1.0 – 5.0
review_count: 0 – 10000
popularity_score must correlate with rating and review_count
4. Tag Rules

Each product must include:

sub_category keyword
category keyword
material
style
season
gender_target
5. Behavioral Realism
Electronics → lower frequency, high value
Groceries → high frequency, low value
Fashion → medium frequency, high variety
Beauty → repeat purchase behavior
🎯 TASK

Generate 500 synthetic products following all rules above.

Ensure:

Balanced category distribution
No duplicate product names
No missing fields
Realistic attribute combinations
Diverse brands and pricing spread

```

This is basically the new product that i want u to generate and replace to current one as it is kinda wiered and does not make any sense for current product in database.

don't change any table or column just adding this into the product table
