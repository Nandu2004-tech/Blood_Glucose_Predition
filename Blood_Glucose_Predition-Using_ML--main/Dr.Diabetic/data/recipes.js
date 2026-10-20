document.addEventListener('DOMContentLoaded', function() {
    const recipeList = document.getElementById('recipe-list');

    // Simulated recipe data
    const recipes = [
        {
            "title": "Grilled Salmon with Avocado Salsa",
            "description": "Delicious grilled salmon topped with fresh avocado salsa, a healthy and flavorful dish.",
            "video": "https://www.youtube.com/embed/NT1NPZL8Ijo",
            "image": "https://via.placeholder.com/300x200?text=Grilled+Salmon"
        },
        {
            "title": "Mango Chicken Stir-Fry",
            "description": "A quick and easy mango chicken stir-fry with fresh vegetables, perfect for a weeknight dinner.",
            "video": "https://www.youtube.com/embed/2RW5tA0f2F8",
            "image": "https://via.placeholder.com/300x200?text=Mango+Chicken"
        },
        {
            "title": "Quinoa and Black Bean Stuffed Peppers",
            "description": "Healthy and satisfying quinoa and black bean stuffed peppers, packed with protein and fiber.",
            "video": "https://www.youtube.com/embed/7hltMjm3S7I",
            "image": "https://via.placeholder.com/300x200?text=Quinoa+Stuffed+Peppers"
        },
        {
            "title": "Greek Yogurt Berry Parfait",
            "description": "A refreshing and nutritious Greek yogurt parfait with mixed berries and granola, great for breakfast or dessert.",
            "video": "https://www.youtube.com/embed/YBmHj68u-hM",
            "image": "https://via.placeholder.com/300x200?text=Yogurt+Parfait"
        },
        {
            "title": "Vegetable and Tofu Stir-Fry",
            "description": "Colorful and flavorful vegetable and tofu stir-fry with a savory sauce, a perfect meatless option.",
            "video": "https://www.youtube.com/embed/vlM5GkzrBkw",
            "image": "https://via.placeholder.com/300x200?text=Vegetable+Stir-Fry"
        },
        {
            "title": "Spinach and Mushroom Quiche",
            "description": "A savory quiche filled with spinach, mushrooms, and cheese, perfect for brunch or a light meal.",
            "video": "https://www.youtube.com/embed/zb7c8NkzBZc",
            "image": "https://via.placeholder.com/300x200?text=Spinach+Quiche"
        },
        {
            "title": "Cauliflower Fried Rice",
            "description": "Healthy and low-carb cauliflower fried rice with vegetables and lean protein, a great alternative to traditional fried rice.",
            "video": "https://www.youtube.com/embed/3q22bz0u9-Q",
            "image": "https://via.placeholder.com/300x200?text=Cauliflower+Fried+Rice"
        },
        {
            "title": "Lemon Garlic Grilled Chicken",
            "description": "Juicy grilled chicken marinated in a tangy lemon garlic sauce, served with roasted vegetables.",
            "video": "https://www.youtube.com/embed/vzE5v9t_2_M",
            "image": "https://via.placeholder.com/300x200?text=Lemon+Garlic+Chicken"
        },
        {
            "title": "Berry Spinach Salad with Balsamic Vinaigrette",
            "description": "Fresh spinach and mixed berries salad drizzled with a sweet and tangy balsamic vinaigrette.",
            "video": "https://www.youtube.com/embed/lV9W2lQUACo",
            "image": "https://via.placeholder.com/300x200?text=Spinach+Berry+Salad"
        },
        {
            "title": "Zucchini Noodles with Pesto",
            "description": "Light and flavorful zucchini noodles tossed in homemade pesto sauce, a healthy twist on pasta.",
            "video": "https://www.youtube.com/embed/5ceSqN6vA3E",
            "image": "https://via.placeholder.com/300x200?text=Zucchini+Noodles"
        },
        {
            "title": "Turkey and Quinoa Stuffed Bell Peppers",
            "description": "Colorful bell peppers stuffed with a filling of ground turkey, quinoa, and spices, baked to perfection.",
            "video": "https://www.youtube.com/embed/7zrZ6ZwPIYA",
            "image": "https://via.placeholder.com/300x200?text=Stuffed+Peppers"
        },
        {
            "title": "Greek Salad with Grilled Shrimp",
            "description": "A refreshing Greek salad topped with grilled shrimp and tossed in a lemon herb dressing.",
            "video": "https://www.youtube.com/embed/b8fNnUVJ-Jo",
            "image": "https://via.placeholder.com/300x200?text=Greek+Salad"
        },
        {
            "title": "Black Bean and Sweet Potato Tacos",
            "description": "Vegetarian tacos filled with seasoned black beans, roasted sweet potatoes, and avocado salsa.",
            "video": "https://www.youtube.com/embed/D_wN_eM0ngI",
            "image": "https://via.placeholder.com/300x200?text=Tacos"
        },
        {
            "title": "Mediterranean Stuffed Chicken Breast",
            "description": "Chicken breasts stuffed with spinach, feta cheese, and sun-dried tomatoes, baked to perfection.",
            "video": "https://www.youtube.com/embed/WY4EVjVY-mg",
            "image": "https://via.placeholder.com/300x200?text=Stuffed+Chicken"
        },
        {
            "title": "Berry Smoothie Bowl",
            "description": "A nutritious and colorful smoothie bowl topped with fresh berries, granola, and seeds.",
            "video": "https://www.youtube.com/embed/bbqu_W6j9Lk",
            "image": "https://via.placeholder.com/300x200?text=Smoothie+Bowl"
        },
        {
            "title": "Caprese Salad with Balsamic Glaze",
            "description": "Classic Caprese salad with fresh mozzarella, tomatoes, basil, and a drizzle of balsamic glaze.",
            "video": "https://www.youtube.com/embed/dCrsFYUy_Ng",
            "image": "https://via.placeholder.com/300x200?text=Caprese+Salad"
        },
        {
            "title": "Salmon and Asparagus Foil Packs",
            "description": "Salmon fillets and asparagus spears seasoned and cooked together in foil packs for an easy and healthy meal.",
            "video": "https://www.youtube.com/embed/Be7Z7DvLQwQ",
            "image": "https://via.placeholder.com/300x200?text=Foil+Packs"
        },
        {
            "title": "Chia Seed Pudding with Fresh Berries",
            "description": "Creamy chia seed pudding topped with a medley of fresh berries, a nutritious and delicious dessert.",
            "video": "https://www.youtube.com/embed/EM3G_tH4kEk",
            "image": "https://via.placeholder.com/300x200?text=Chia+Seed+Pudding"
        },
        {
            "title": "Vegetarian Lentil Soup",
            "description": "Hearty lentil soup loaded with vegetables and flavored with aromatic spices, perfect for a comforting meal.",
            "video": "https://www.youtube.com/embed/FSdLqK3cV7U",
            "image": "https://via.placeholder.com/300x200?text=Lentil+Soup"
        },
        {
            "title": "Avocado Toast with Poached Egg",
            "description": "Whole grain toast topped with mashed avocado, a perfectly poached egg, and a sprinkle of seasoning.",
            "video": "https://www.youtube.com/embed/6z0gJB1tqyA",
            "image": "https://via.placeholder.com/300x200?text=Avocado+Toast"
        },
        {
            "title": "Thai Peanut Chicken Lettuce Wraps",
            "description": "Lettuce wraps filled with Thai-inspired peanut chicken, crunchy vegetables, and a hint of spice.",
            "video": "https://www.youtube.com/embed/8XsHhACuZZY",
            "image": "https://via.placeholder.com/300x200?text=Lettuce+Wraps"
        },
        {
            "title": "Roasted Vegetable Quinoa Salad",
            "description": "Nutritious quinoa salad loaded with roasted vegetables, fresh herbs, and a tangy lemon dressing.",
            "video": "https://www.youtube.com/embed/Alw5CX9szZs",
            "image": "https://via.placeholder.com/300x200?text=Quinoa+Salad"
        },
        {
            "title": "Pesto Zoodles with Cherry Tomatoes",
            "description": "Zucchini noodles tossed in basil pesto sauce and garnished with cherry tomatoes, a light and flavorful dish.",
            "video": "https://www.youtube.com/embed/UoA6rHD1qAg",
            "image": "https://via.placeholder.com/300x200?text=Pesto+Zoodles"
        },
        {
            "title": "Honey Garlic Shrimp Stir-Fry",
            "description": "Quick and flavorful shrimp stir-fry with a honey garlic sauce, served with steamed rice or noodles.",
            "video": "https://www.youtube.com/embed/7UHqdU8Izgw",
            "image": "https://via.placeholder.com/300x200?text=Honey+Garlic+Shrimp"
        },
        {
            "title": "Greek Yogurt Chicken Salad",
            "description": "Creamy Greek yogurt chicken salad with grapes, celery, and almonds, perfect for sandwiches or wraps.",
            "video": "https://www.youtube.com/embed/sU4Edd-tIio",
            "image": "https://via.placeholder.com/300x200?text=Yogurt+Chicken+Salad"
        },
        {
            "title": "Pineapple Mango Salsa",
            "description": "Fresh and vibrant pineapple mango salsa with cilantro and lime, great as a topping or dip.",
            "video": "https://www.youtube.com/embed/FX7A3WTC1QQ",
            "image": "https://via.placeholder.com/300x200?text=Pineapple+Mango+Salsa"
        },
        {
            "title": "Mediterranean Chickpea Salad",
            "description": "Refreshing Mediterranean salad with chickpeas, cucumbers, tomatoes, and feta cheese, tossed in a lemon herb dressing.",
            "video": "https://www.youtube.com/embed/_X07ab6hbs8",
            "image": "https://via.placeholder.com/300x200?text=Chickpea+Salad"
        },
        {
            "title": "Broccoli and Cheese Stuffed Chicken Breast",
            "description": "Tender chicken breasts stuffed with broccoli and cheese, baked until golden and cheesy.",
            "video": "https://www.youtube.com/embed/c7Xen9iLrK0",
            "image": "https://via.placeholder.com/300x200?text=Stuffed+Chicken+Breast"
        },
        {
            "title": "Peach and Spinach Smoothie",
            "description": "A refreshing smoothie blend of peaches, spinach, and Greek yogurt, packed with vitamins and antioxidants.",
            "video": "https://www.youtube.com/embed/vvCmpVjBn3M",
            "image": "https://via.placeholder.com/300x200?text=Peach+Smoothie"
        },
        {
            "title": "Stuffed Portobello Mushrooms",
            "description": "Portobello mushrooms stuffed with a savory mixture of quinoa, spinach, and cheese, baked to perfection.",
            "video": "https://www.youtube.com/embed/B7s3Mqu7fvA",
            "image": "https://via.placeholder.com/300x200?text=Stuffed+Mushrooms"
        },
        {
            "title": "Turkey Meatballs with Marinara Sauce",
            "description": "Lean turkey meatballs simmered in a flavorful marinara sauce, served over whole wheat pasta or zucchini noodles.",
            "video": "https://www.youtube.com/embed/Db3jJF3sgjY",
            "image": "https://via.placeholder.com/300x200?text=Turkey+Meatballs"
        },
        {
            "title": "Sweet Potato and Black Bean Chili",
            "description": "Hearty sweet potato and black bean chili seasoned with warm spices and served with avocado slices.",
            "video": "https://www.youtube.com/embed/3FSMmE1YRCM",
            "image": "https://via.placeholder.com/300x200?text=Sweet+Potato+Chili"
        },
        {
            "title": "Pesto Salmon with Roasted Vegetables",
            "description": "Baked salmon fillets topped with basil pesto, accompanied by a colorful assortment of roasted vegetables.",
            "video": "https://www.youtube.com/embed/0MA0no7c0Vg",
            "image": "https://via.placeholder.com/300x200?text=Pesto+Salmon"
        },
        {
            "title": "Mango Coconut Chia Pudding",
            "description": "Creamy chia seed pudding infused with mango and coconut flavors, topped with fresh fruit and coconut flakes.",
            "video": "https://www.youtube.com/embed/wT1Uf3opwuk",
            "image": "https://via.placeholder.com/300x200?text=Mango+Chia+Pudding"
        },
        {
            "title": "Teriyaki Tofu Stir-Fry",
            "description": "Tofu cubes stir-fried with colorful vegetables in a sweet and savory teriyaki sauce, served over brown rice.",
            "video": "https://www.youtube.com/embed/QaomIB2QgrM",
            "image": "https://via.placeholder.com/300x200?text=Teriyaki+Tofu"
        },
        {
            "title": "Cucumber Avocado Salad",
            "description": "Refreshing salad with cucumber, avocado, cherry tomatoes, and a light lemon vinaigrette dressing.",
            "video": "https://www.youtube.com/embed/QCqHs4qo8J4",
            "image": "https://via.placeholder.com/300x200?text=Cucumber+Avocado+Salad"
        },
        {
            "title": "Chicken and Vegetable Skewers",
            "description": "Grilled chicken and vegetable skewers marinated in a tangy herb marinade, perfect for outdoor grilling.",
            "video": "https://www.youtube.com/embed/n9BdP4AciUk",
            "image": "https://via.placeholder.com/300x200?text=Chicken+Skewers"
        },
        {
            "title": "Quinoa Stuffed Acorn Squash",
            "description": "Roasted acorn squash halves filled with quinoa, cranberries, and pecans, a festive and nutritious dish.",
            "video": "https://www.youtube.com/embed/3e-N0dQj8uA",
            "image": "https://via.placeholder.com/300x200?text=Stuffed+Squash"
        }
    ];

    // Function to render recipes on the page
    recipes.forEach(recipe => {
        const recipeCard = document.createElement('div');
        recipeCard.className = 'recipe-card';

        recipeCard.innerHTML = `
            <img src="${recipe.image}" alt="${recipe.title}">
            <h2>${recipe.title}</h2>
            <p>${recipe.description}</p>
            <iframe width="100%" height="200" src="${recipe.video}" frameborder="0" allowfullscreen></iframe>
        `;

        recipeList.appendChild(recipeCard);
    });
});