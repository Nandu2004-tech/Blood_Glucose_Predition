document.addEventListener('DOMContentLoaded', function() {
    const dietPlans = [
        {
            "title": "Low Carb Diet",
            "description": "A low carbohydrate diet to help manage blood sugar levels.",
            "image": "/img/low-carb.jpg",
            "link": "/html_pages/diet1.html"
        },
        {
            "title": "Mediterranean Diet",
            "description": "A heart-healthy Mediterranean diet plan.",
            "image": "/img/mediterranean.jpg",
            "link": "/html_pages/diet2.html"
        },
        {
            "title": "Vegetarian Diet",
            "description": "A balanced vegetarian diet for diabetics.",
            "image": "/img/vegetarian.jpg",
            "link": "/html_pages/diet3.html"
        },
        {
            "title": "High Fiber Diet",
            "description": "A diet rich in fiber to help control blood sugar.",
            "image": "/img/high-fiber.jpg",
            "link": "/html_pages/diet4.html"
        },
        {
            "title": "DASH Diet",
            "description": "Dietary Approaches to Stop Hypertension (DASH) for diabetics.",
            "image": "/img/dash.jpg",
            "link": "/html_pages/diet5.html"
        },
        {
            "title": "Keto Diet",
            "description": "A ketogenic diet to manage diabetes effectively.",
            "image": "/img/keto.jpg",
            "link": "/html_pages/diet6.html"
        },
        {
            "title": "Paleo Diet",
            "description": "A paleo diet plan for diabetics.",
            "image": "/img/paleo.jpg",
            "link": "/html_pages/diet7.html"
        },
        {
            "title": "Vegan Diet",
            "description": "A complete vegan diet plan for managing diabetes.",
            "image": "/img/vegan.jpg",
            "link": "/html_pages/diet8.html"
        },
        {
            "title": "Flexitarian Diet",
            "description": "A flexible diet plan that includes vegetarian meals.",
            "image": "/img/flexitarian.jpg",
            "link": "/html_pages/diet9.html"
        },
        {
            "title": "Zone Diet",
            "description": "The Zone diet for balanced nutrition and blood sugar control.",
            "image": "/img/zone.jpg",
            "link": "/html_pages/diet10.html"
        },
        {
            "title": "Article 11",
            "description": "Description of Article 11.",
            "image": "/img/article11.jpg",
            "link": "/html_pages/article11.html"
        },
        {
            "title": "Article 12",
            "description": "Description of Article 12.",
            "image": "/img/article12.jpg",
            "link": "/html_pages/article12.html"
        },
        {
            "title": "Article 13",
            "description": "Description of Article 13.",
            "image": "/img/article13.jpg",
            "link": "/html_pages/article13.html"
        },
        {
            "title": "Article 14",
            "description": "Description of Article 14.",
            "image": "/img/article14.jpg",
            "link": "/html_pages/article14.html"
        },
        {
            "title": "Article 15",
            "description": "Description of Article 15.",
            "image": "/img/article15.jpg",
            "link": "/html_pages/article15.html"
        },
        {
            "title": "Article 16",
            "description": "Description of Article 16.",
            "image": "/img/article16.jpg",
            "link": "/html_pages/article16.html"
        },
        {
            "title": "Article 17",
            "description": "Description of Article 17.",
            "image": "/img/article17.jpg",
            "link": "/html_pages/article17.html"
        },
        {
            "title": "Article 18",
            "description": "Description of Article 18.",
            "image": "/img/article18.jpg",
            "link": "/html_pages/article18.html"
        },
        {
            "title": "Article 19",
            "description": "Description of Article 19.",
            "image": "/img/article19.jpg",
            "link": "/html_pages/article19.html"
        },
        {
            "title": "Article 20",
            "description": "Description of Article 20.",
            "image": "/img/article20.jpg",
            "link": "/html_pages/article20.html"
        },
        {
            "title": "Article 21",
            "description": "Description of Article 21.",
            "image": "/img/article21.jpg",
            "link": "/html_pages/article21.html"
        },
        {
            "title": "Article 22",
            "description": "Description of Article 22.",
            "image": "/img/article22.jpg",
            "link": "/html_pages/article22.html"
        },
        {
            "title": "Article 23",
            "description": "Description of Article 23.",
            "image": "/img/article23.jpg",
            "link": "/html_pages/article23.html"
        },
        {
            "title": "Article 24",
            "description": "Description of Article 24.",
            "image": "/img/article24.jpg",
            "link": "/html_pages/article24.html"
        },
        {
            "title": "Article 25",
            "description": "Description of Article 25.",
            "image": "/img/article25.jpg",
            "link": "/html_pages/article25.html"
        },
        {
            "title": "Article 26",
            "description": "Description of Article 26.",
            "image": "/img/article26.jpg",
            "link": "/html_pages/article26.html"
        },
        {
            "title": "Article 27",
            "description": "Description of Article 27.",
            "image": "/img/article27.jpg",
            "link": "/html_pages/article27.html"
        },
        {
            "title": "Article 28",
            "description": "Description of Article 28.",
            "image": "/img/article28.jpg",
            "link": "/html_pages/article28.html"
        },
        {
            "title": "Article 29",
            "description": "Description of Article 29.",
            "image": "/img/article29.jpg",
            "link": "/html_pages/article29.html"
        },
        {
            "title": "Article 30",
            "description": "Description of Article 30.",
            "image": "/img/article30.jpg",
            "link": "/html_pages/article30.html"
        }
    ];

    const dietPlanList = document.getElementById('diet-plan-list');
    dietPlans.forEach(plan => {
        const dietPlanCard = document.createElement('div');
        dietPlanCard.className = 'diet-plan-card';

        dietPlanCard.innerHTML = `
            <img src="${plan.image}" alt="${plan.title}">
            <h2>${plan.title}</h2>
            <p>${plan.description}</p>
            <a href="${plan.link}" class="btn">Read More</a>
        `;

        dietPlanList.appendChild(dietPlanCard);
    });
});