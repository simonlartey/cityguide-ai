const SELECTORS = {
  filterChip: "[data-filter]",
  recommendationCard: "[data-recommendation-card]",
};

const hydrateDashboardIcons = () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
};

const initializeFilterChips = () => {
  const filterChips = document.querySelectorAll(
    SELECTORS.filterChip
  );

  filterChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      filterChips.forEach((currentChip) => {
        currentChip.classList.remove("filter-chip--active");
        currentChip.setAttribute("aria-pressed", "false");
      });

      chip.classList.add("filter-chip--active");
      chip.setAttribute("aria-pressed", "true");
    });
  });
};

const selectRecommendationCard = (selectedCard) => {
  const cards = document.querySelectorAll(
    SELECTORS.recommendationCard
  );

  cards.forEach((card) => {
    card.classList.toggle(
      "recommendation-card--selected",
      card === selectedCard
    );
  });
};

const initializeRecommendationCards = () => {
  const cards = document.querySelectorAll(
    SELECTORS.recommendationCard
  );

  cards.forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("button, a")) {
        return;
      }

      selectRecommendationCard(card);
    });

    card.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      event.preventDefault();
      selectRecommendationCard(card);
    });
  });
};

const initializeDashboard = () => {
  initializeFilterChips();
  initializeRecommendationCards();
};

document.addEventListener("DOMContentLoaded", initializeDashboard);

if (typeof window.requestIdleCallback === "function") {
  window.requestIdleCallback(hydrateDashboardIcons);
} else {
  window.setTimeout(hydrateDashboardIcons, 0);
}