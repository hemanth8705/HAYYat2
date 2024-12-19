document.addEventListener("DOMContentLoaded", () => {
    // JSON file path
    const jsonFilePath = "database_content.json";

    // Fetch data from the JSON file
    fetch(jsonFilePath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            populateDomains(data);
            addDomainFilterLogic(data);
        })
        .catch(error => {
            console.error("Error loading data from JSON file:", error);
        });
});

// Populate domain filter
function populateDomains(data) {
    const tabsContainer = document.querySelector(".tab__nav ul");
    tabsContainer.innerHTML = "";

    const categories = Array.from(new Set(data.map(item => item.category)));

    categories.forEach((category, index) => {
        const tabItem = document.createElement("li");
        tabItem.classList.add("tab__item");

        const tabLink = document.createElement("a");
        tabLink.href = "#";
        tabLink.textContent = category;
        tabLink.dataset.category = category;

        if (index === 0) {
            tabLink.classList.add("is-activated");
        }

        tabItem.appendChild(tabLink);
        tabsContainer.appendChild(tabItem);
    });
}

// Add filtering logic
function addDomainFilterLogic(data) {
    const tabs = document.querySelectorAll(".tab__nav a");
    const contentContainer = document.querySelector(".tab__content");

    tabs.forEach(tab => {
        tab.addEventListener("click", event => {
            event.preventDefault();

            // Highlight the active tab
            tabs.forEach(t => t.classList.remove("is-activated"));
            tab.classList.add("is-activated");

            // Filter and display cards for the selected category
            const selectedCategory = tab.dataset.category;
            const filteredData = data.filter(item => item.category === selectedCategory);

            displayCards(filteredData, contentContainer);
        });
    });

    // Display cards for the first category by default
    const firstCategory = tabs[0].dataset.category;
    const filteredData = data.filter(item => item.category === firstCategory);
    displayCards(filteredData, contentContainer);
}

// Display cards for a specific category
function displayCards(data, container) {
    container.innerHTML = ""; // Clear existing content

    if (data.length === 0) {
        const noDataMessage = document.createElement("p");
        noDataMessage.textContent = "No articles available for this category.";
        container.appendChild(noDataMessage);
        return;
    }

    data.forEach(article => {
        const card = createCard(article);
        container.appendChild(card);
    });
}

function createCard(article) {
    const card = document.createElement("div");
    card.classList.add("card", "card--centered");

    // Card header
    const cardHeader = document.createElement("div");
    cardHeader.classList.add("card__header");

    const cardTitle = document.createElement("h3");
    cardTitle.classList.add("card__title");
    const cardLink = document.createElement("a");
    cardLink.href = article.article_url;
    cardLink.target = "_blank";
    cardLink.textContent = article.headlines.slice(0, 30) + "...";
    cardTitle.appendChild(cardLink);

    const cardSubline = document.createElement("p");
    cardSubline.classList.add("card__subline");

    cardHeader.appendChild(cardTitle);
    cardHeader.appendChild(cardSubline);

    // Tooltip on hover
    cardTitle.addEventListener("mouseover", () => {
        const tooltip = document.createElement("div");
        tooltip.classList.add("tooltip");
        tooltip.textContent = article.headlines;
        document.body.appendChild(tooltip);

        const rect = cardTitle.getBoundingClientRect();
        tooltip.style.left = `${rect.left}px`;
        tooltip.style.top = `${rect.bottom + 5}px`;

        cardTitle.addEventListener("mouseleave", () => {
            tooltip.remove();
        });
    });

    // Card content
    const cardContent = document.createElement("div");
    cardContent.classList.add("card__content");

    // Sentiment Text below headline
    const sentimentText = document.createElement("p");
    sentimentText.classList.add("sentiment-text");
    sentimentText.textContent = `Positive: ${article.positive}% | Negative: ${article.negative}%`;

    cardContent.appendChild(sentimentText);

    // Append header and content to the card
    card.appendChild(cardHeader);
    card.appendChild(cardContent);

    return card;
}
