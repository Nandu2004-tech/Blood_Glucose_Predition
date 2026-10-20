document.addEventListener('DOMContentLoaded', function() {
    const articles = [
        {
            "title": "Managing Diabetes with Diet",
            "description": "Learn how to manage your diabetes effectively with a healthy diet.",
            "image": "/img/diet.jpg",
            "link": "/html_pages/article1.html"
        },
        {
            "title": "Exercise Tips for Diabetics",
            "description": "Discover the best exercise routines for managing diabetes.",
            "image": "/img/exercise.jpg",
            "link": "/html_pages/article2.html"
        },
        {
            "title": "Understanding Blood Sugar Levels",
            "description": "A comprehensive guide to understanding and monitoring your blood sugar levels.",
            "image": "/img/blood-sugar.jpg",
            "link": "/html_pages/article3.html"
        },
        {
            "title": "Article 4",
            "description": "Description of Article 4.",
            "image": "/img/article4.jpg",
            "link": "/html_pages/article4.html"
        },
        {
            "title": "Article 5",
            "description": "Description of Article 5.",
            "image": "/img/article5.jpg",
            "link": "/html_pages/article5.html"
        },
        {
            "title": "Article 6",
            "description": "Description of Article 6.",
            "image": "/img/article6.jpg",
            "link": "/html_pages/article6.html"
        },
        {
            "title": "Article 7",
            "description": "Description of Article 7.",
            "image": "/img/article7.jpg",
            "link": "/html_pages/article7.html"
        },
        {
            "title": "Article 8",
            "description": "Description of Article 8.",
            "image": "/img/article8.jpg",
            "link": "/html_pages/article8.html"
        },
        {
            "title": "Article 9",
            "description": "Description of Article 9.",
            "image": "/img/article9.jpg",
            "link": "/html_pages/article9.html"
        },
        {
            "title": "Article 10",
            "description": "Description of Article 10.",
            "image": "/img/article10.jpg",
            "link": "/html_pages/article10.html"
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

    const articleList = document.getElementById('article-list');
    articles.forEach(article => {
        const articleCard = document.createElement('div');
        articleCard.className = 'article-card';

        articleCard.innerHTML = `
            <img src="${article.image}" alt="${article.title}">
            <h2>${article.title}</h2>
            <p>${article.description}</p>
            <a href="${article.link}" class="btn">Read More</a>
        `;

        articleList.appendChild(articleCard);
    });
});