const SELECTORS = {
  filterChip: "[data-filter]",
  recommendationCard: "[data-recommendation-card]",
  recommendationList: ".recommendation-list",
  mapPreview: ".map-preview",
  placeMarker: "[data-place-marker]",
  placeSaveButton: "[data-place-save-button]",
  sidebarShell: "#dashboard-shell",
  dashboardSidebar: "#dashboard-sidebar",
  dashboardInspector: "#dashboard-inspector",
  sidebarToggle: "[data-sidebar-toggle]",
  sidebarToggleIcon: "[data-sidebar-toggle-icon]",
  mobileSidebarToggle: "[data-mobile-sidebar-toggle]",
  sidebarBackdrop: "[data-sidebar-backdrop]",
  inspectorTab: "[data-inspector-tab]",
  inspectorPanel: "[data-inspector-panel]",
  placeResult: "[data-place-result]",
  inspectorResultsList: ".inspector-results-list",
  mobileInspectorToggle: "[data-mobile-inspector-toggle]",
  mobileInspectorClose: "[data-mobile-inspector-close]",
  inspectorBackdrop: "[data-inspector-backdrop]",
  searchForm: "#dashboard-search-form",
  searchInput: "#dashboard-query",
  searchSubmit: "#dashboard-search-submit",
  searchStatus: "#dashboard-search-status",
  searchProgress: ".search-progress",
  searchProgressTitle: "#search-progress-title",
  searchProgressStatus: ".search-progress-status",
  resultsState: "#dashboard-results-state",
  resultsStateTitle: "[data-results-state-title]",
  resultsStateMessage: "[data-results-state-message]",
};

const INITIAL_SEARCH_QUERY =
  "Affordable barber for textured hair";

let PLACES = {};

const hydrateDashboardIcons = () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
};

const formatPriceLevel = (priceLevel) => {
  if (!Number.isInteger(priceLevel) || priceLevel < 1) {
    return "";
  }

  return "$".repeat(priceLevel);
};

const getRecommendationImageClass = (index) => {
  const imageClasses = [
    "recommendation-image--one",
    "recommendation-image--two",
    "recommendation-image--three",
  ];

  return imageClasses[index % imageClasses.length];
};

const normalizePlaceForDashboard = (place, index) => ({
  ...place,
  rating: String(place.rating),
  distance: `${place.distance_miles} mi`,
  price: formatPriceLevel(place.price_level),
  status: place.open_now ? "Open now" : "Closed",
  hours: place.hours_text,
  heroClass: getRecommendationImageClass(index).replace(
    "recommendation-image",
    "place-hero"
  ),
  reasons: place.match_reasons || [],
});

const updateCurrentPlaces = (places) => {
  PLACES = Object.fromEntries(
    places.map((place, index) => [
      place.id,
      normalizePlaceForDashboard(place, index),
    ])
  );
};

const createRecommendationCard = (place, index) => {
  const card = document.createElement("article");

  card.className = "recommendation-card";
  card.dataset.recommendationCard = "";
  card.dataset.placeId = place.id;
  card.tabIndex = 0;

  if (index === 0) {
    card.classList.add("recommendation-card--selected");
  }

  const image = document.createElement("div");
  image.className =
    `recommendation-image ${getRecommendationImageClass(index)}`;

  const rank = document.createElement("span");
  rank.className = "recommendation-rank";
  rank.textContent = String(index + 1);

  const imageLabel = document.createElement("span");
  imageLabel.className = "recommendation-image-label";
  imageLabel.setAttribute("aria-hidden", "true");
  imageLabel.textContent = `${place.name} preview`;

  image.append(rank, imageLabel);

  const copy = document.createElement("div");
  copy.className = "recommendation-copy";

  const heading = document.createElement("div");
  heading.className = "recommendation-heading";

  const headingCopy = document.createElement("div");

  const name = document.createElement("h2");
  name.textContent = place.name;

  const meta = document.createElement("div");
  meta.className = "recommendation-meta";

  const rating = document.createElement("span");
  rating.className = "rating";
  rating.textContent =
    `★ ${place.rating} (${place.review_count})`;

  const distance = document.createElement("span");
  distance.textContent = `${place.distance_miles} mi`;

  const price = document.createElement("span");
  price.textContent = formatPriceLevel(
    place.price_level
  );

  const availability = document.createElement("span");
  availability.className = "availability-pill";
  availability.textContent = place.open_now
    ? "Open now"
    : "Closed";

  const separators = Array.from(
    { length: 3 },
    () => {
      const separator = document.createElement("span");
      separator.setAttribute("aria-hidden", "true");
      separator.textContent = "·";
      return separator;
    }
  );

  meta.append(
    rating,
    separators[0],
    distance,
    separators[1],
    price,
    separators[2],
    availability
  );

  headingCopy.append(name, meta);

  const saveButton = document.createElement("button");
  saveButton.type = "button";
  saveButton.className = "save-place-button";
  saveButton.setAttribute(
    "aria-label",
    `Save ${place.name}`
  );
  saveButton.setAttribute(
    "data-place-save-button",
    ""
  );

  const saveIcon = document.createElement("span");
  saveIcon.setAttribute("aria-hidden", "true");
  saveIcon.setAttribute("data-lucide", "heart");

  saveButton.append(saveIcon);
  heading.append(headingCopy, saveButton);

  const description = document.createElement("p");
  description.className = "recommendation-description";
  description.textContent = place.description;

  const tag = document.createElement("span");
  tag.className = "recommendation-tag";
  tag.textContent =
    place.tags?.[0] || place.category;

  copy.append(heading, description, tag);

  const actions = document.createElement("div");
  actions.className = "recommendation-actions";

  [
    ["navigation", "Directions"],
    ["phone", "Call"],
    ["globe-2", "Website"],
  ].forEach(([iconName, label]) => {
    const button = document.createElement("button");
    button.type = "button";

    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");
    icon.setAttribute("data-lucide", iconName);

    button.append(icon, document.createTextNode(label));
    actions.append(button);
  });

  card.append(image, copy, actions);

  return card;
};

const createInspectorResult = (place, index) => {
  const result = document.createElement("button");

  result.type = "button";
  result.className = "inspector-result-item";
  result.dataset.placeResult = place.id;

  if (index === 0) {
    result.classList.add("inspector-result-item--active");
  }

  const rank = document.createElement("span");
  rank.className = "inspector-result-rank";
  rank.textContent = String(index + 1);

  const copy = document.createElement("span");
  copy.className = "inspector-result-copy";

  const name = document.createElement("span");
  name.className = "inspector-result-name";
  name.textContent = place.name;

  const meta = document.createElement("span");
  meta.className = "inspector-result-meta";
  meta.textContent = [
    place.rating,
    `${place.distance_miles} mi`,
    formatPriceLevel(place.price_level),
  ].join(" · ");

  copy.append(name, meta);
  result.append(rank, copy);

  return result;
};

const renderRecommendationCards = (places) => {
  const recommendationList = document.querySelector(
    SELECTORS.recommendationList
  );

  if (!recommendationList) {
    return;
  }

  recommendationList.replaceChildren(
    ...places.map(createRecommendationCard)
  );

  initializeRecommendationCards();
  hydrateDashboardIcons();
};

const renderInspectorResults = (places) => {
  const resultsList = document.querySelector(
    SELECTORS.inspectorResultsList
  );

  if (!resultsList) {
    return;
  }

  resultsList.replaceChildren(
    ...places.map(createInspectorResult)
  );

  initializeInspectorResults();
};

const getMapMarkerClass = (index) => {
  const markerClasses = [
    "map-marker--one",
    "map-marker--two",
    "map-marker--three",
  ];

  return markerClasses[index % markerClasses.length];
};

const createMapMarker = (place, index) => {
  const marker = document.createElement("button");

  marker.type = "button";
  marker.className =
    `map-marker ${getMapMarkerClass(index)}`;
  marker.dataset.placeMarker = place.id;
  marker.setAttribute("aria-label", place.name);

  if (index === 0) {
    marker.classList.add("map-marker--active");
  }

  const rank = document.createElement("span");
  rank.textContent = String(index + 1);

  marker.append(rank);

  return marker;
};

const renderMapMarkers = (places) => {
  const mapPreview = document.querySelector(
    SELECTORS.mapPreview
  );

  if (!mapPreview) {
    return;
  }

  mapPreview
    .querySelectorAll(SELECTORS.placeMarker)
    .forEach((marker) => marker.remove());

  mapPreview.append(
    ...places.map(createMapMarker)
  );

  initializeMapMarkers();
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

const updatePlaceDetails = (placeId) => {
  const place = PLACES[placeId];

  if (!place) {
    return;
  }

  document.querySelector("[data-place-name]").textContent =
    place.name;

  const ratingLabel =
    Number.isInteger(place.review_count)
      ? `${place.rating} (${place.review_count} reviews)`
      : place.rating;
  const distanceLabel =
    place.distance ?? `${place.distance_miles} mi`;
  const priceLabel =
    place.price ?? formatPriceLevel(place.price_level);
  const statusLabel =
    place.status ?? (place.open_now ? "Open now" : "Closed");

  document
    .querySelectorAll(SELECTORS.placeSaveButton)
    .forEach((button) => {
      button.setAttribute(
        "aria-label",
        `Save ${place.name}`
      );
    });

  document.querySelector("[data-place-rating]").textContent =
    ratingLabel;
  document.querySelector("[data-place-distance]").textContent =
    distanceLabel;
  document.querySelector("[data-place-price]").textContent =
    priceLabel;
  document.querySelector("[data-place-status]").textContent =
    statusLabel;
  document.querySelector("[data-place-address]").textContent =
    place.address || "Address unavailable";
  document.querySelector("[data-place-hours]").textContent =
    place.hours || "Hours unavailable";

  const hero = document.querySelector("[data-place-hero]");

  hero.classList.remove(
    "place-hero--one",
    "place-hero--two",
    "place-hero--three"
  );
  hero.classList.add(place.heroClass);

  const reasons = document.querySelector("[data-place-reasons]");

  reasons.replaceChildren(
    ...(place.reasons || []).map((reason) => {
      const listItem = document.createElement("li");
      const icon = document.createElement("span");
      const text = document.createTextNode(reason);

      icon.setAttribute("aria-hidden", "true");
      icon.setAttribute("data-lucide", "check");

      listItem.append(icon, text);

      return listItem;
    })
  );

  hydrateDashboardIcons();
};

const selectPlace = (placeId) => {
  document
    .querySelectorAll(SELECTORS.recommendationCard)
    .forEach((card) => {
      card.classList.toggle(
        "recommendation-card--selected",
        card.dataset.placeId === placeId
      );
    });

  document
    .querySelectorAll(SELECTORS.placeMarker)
    .forEach((marker) => {
      marker.classList.toggle(
        "map-marker--active",
        marker.dataset.placeMarker === placeId
      );
    });

  document
    .querySelectorAll(SELECTORS.placeResult)
    .forEach((result) => {
      result.classList.toggle(
        "inspector-result-item--active",
        result.dataset.placeResult === placeId
      );
    });

  updatePlaceDetails(placeId);
};

const initializeRecommendationCards = () => {
  document
    .querySelectorAll(SELECTORS.recommendationCard)
    .forEach((card) => {
      card.addEventListener("click", (event) => {
        if (event.target.closest("button, a")) {
          return;
        }

        selectPlace(card.dataset.placeId);
      });

      card.addEventListener("keydown", (event) => {
        if (event.target.closest("button, a, input, select, textarea")) {
          return;
        }

        if (event.key !== "Enter" && event.key !== " ") {
          return;
        }

        event.preventDefault();
        selectPlace(card.dataset.placeId);
      });
    });
};

const initializeMapMarkers = () => {
  document
    .querySelectorAll(SELECTORS.placeMarker)
    .forEach((marker) => {
      marker.addEventListener("click", () => {
        selectPlace(marker.dataset.placeMarker);
      });
    });
};

const activateInspectorTab = (tabName) => {
  document
    .querySelectorAll(SELECTORS.inspectorTab)
    .forEach((tab) => {
      const isActive = tab.dataset.inspectorTab === tabName;

      tab.classList.toggle("inspector-tab--active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
    });

  document
    .querySelectorAll(SELECTORS.inspectorPanel)
    .forEach((panel) => {
      panel.hidden = panel.dataset.inspectorPanel !== tabName;
    });
};

const initializeInspectorTabs = () => {
  const tabs = Array.from(
    document.querySelectorAll(
      SELECTORS.inspectorTab
    )
  );

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      activateInspectorTab(
        tab.dataset.inspectorTab
      );
    });

    tab.addEventListener("keydown", (event) => {
      if (
        event.key !== "ArrowLeft" &&
        event.key !== "ArrowRight" &&
        event.key !== "Home" &&
        event.key !== "End"
      ) {
        return;
      }

      event.preventDefault();

      let nextIndex = index;

      if (event.key === "ArrowRight") {
        nextIndex = (index + 1) % tabs.length;
      }

      if (event.key === "ArrowLeft") {
        nextIndex =
          (index - 1 + tabs.length) %
          tabs.length;
      }

      if (event.key === "Home") {
        nextIndex = 0;
      }

      if (event.key === "End") {
        nextIndex = tabs.length - 1;
      }

      const nextTab = tabs[nextIndex];

      activateInspectorTab(
        nextTab.dataset.inspectorTab
      );
      nextTab.focus();
    });
  });
};

const initializeInspectorResults = () => {
  document
    .querySelectorAll(SELECTORS.placeResult)
    .forEach((result) => {
      result.addEventListener("click", () => {
        selectPlace(result.dataset.placeResult);
        activateInspectorTab("map");
      });
    });
};

const initializeSidebarToggle = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const toggle = document.querySelector(
    SELECTORS.sidebarToggle
  );
  const icon = document.querySelector(
    SELECTORS.sidebarToggleIcon
  );

  if (!shell || !toggle || !icon) {
    return;
  }

  const syncSidebarToggleState = () => {
    const isCollapsed = shell.classList.contains(
      "dashboard-shell--sidebar-collapsed"
    );

    toggle.setAttribute(
      "aria-label",
      isCollapsed
        ? "Expand sidebar"
        : "Collapse sidebar"
    );

    toggle.setAttribute(
      "aria-expanded",
      String(!isCollapsed)
    );

    icon.setAttribute(
      "data-lucide",
      isCollapsed
        ? "chevrons-right"
        : "chevrons-left"
    );

    hydrateDashboardIcons();
  };

  toggle.addEventListener("click", () => {
    shell.classList.toggle(
      "dashboard-shell--sidebar-collapsed"
    );

    syncSidebarToggleState();
  });

  syncSidebarToggleState();
};

const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

const getFocusableElements = (container) =>
  Array.from(
    container.querySelectorAll(FOCUSABLE_SELECTOR)
  ).filter(
    (element) =>
      !element.closest(
        "[hidden], [aria-hidden='true'], [inert]"
      )
  );

const trapFocusWithin = (event, container) => {
  if (event.key !== "Tab") {
    return;
  }

  const focusableElements =
    getFocusableElements(container);

  if (focusableElements.length === 0) {
    event.preventDefault();
    return;
  }

  const firstElement = focusableElements[0];
  const lastElement =
    focusableElements[
      focusableElements.length - 1
    ];

  if (
    event.shiftKey &&
    document.activeElement === firstElement
  ) {
    event.preventDefault();
    lastElement.focus();
    return;
  }

  if (
    !event.shiftKey &&
    document.activeElement === lastElement
  ) {
    event.preventDefault();
    firstElement.focus();
  }
};

const setDrawerAccessibility = (
  drawer,
  isAvailable
) => {
  drawer.inert = !isAvailable;

  if (isAvailable) {
    drawer.removeAttribute("aria-hidden");
    return;
  }

  drawer.setAttribute("aria-hidden", "true");
};

const syncMobileDrawerAccessibility = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const sidebar = document.querySelector(
    SELECTORS.dashboardSidebar
  );
  const inspector = document.querySelector(
    SELECTORS.dashboardInspector
  );

  if (!shell || !sidebar || !inspector) {
    return;
  }

  const sidebarIsMobile =
    window.innerWidth <= 760;
  const inspectorIsMobile =
    window.innerWidth <= 900;

  setDrawerAccessibility(
    sidebar,
    !sidebarIsMobile ||
      shell.classList.contains(
        "dashboard-shell--mobile-sidebar-open"
      )
  );

  setDrawerAccessibility(
    inspector,
    !inspectorIsMobile ||
      shell.classList.contains(
        "dashboard-shell--mobile-inspector-open"
      )
  );
};

const updateBodyScrollLock = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );

  if (!shell) {
    return;
  }

  const hasOpenOverlay =
    shell.classList.contains(
      "dashboard-shell--mobile-sidebar-open"
    ) ||
    shell.classList.contains(
      "dashboard-shell--mobile-inspector-open"
    );

  document.body.style.overflow = hasOpenOverlay
    ? "hidden"
    : "";
};

const setMobileSidebarOpen = (isOpen, restoreFocus = false) => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const sidebar = document.querySelector(
    SELECTORS.dashboardSidebar
  );
  const toggle = document.querySelector(
    SELECTORS.mobileSidebarToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.sidebarBackdrop
  );

  if (!shell || !sidebar || !toggle || !backdrop) {
    return;
  }

  shell.classList.toggle(
    "dashboard-shell--mobile-sidebar-open",
    isOpen
  );

  toggle.setAttribute(
    "aria-expanded",
    String(isOpen)
  );

  toggle.setAttribute(
    "aria-label",
    isOpen
      ? "Close navigation"
      : "Open navigation"
  );

  backdrop.hidden = !isOpen;

  syncMobileDrawerAccessibility();

  if (isOpen) {
    const firstFocusable =
      getFocusableElements(sidebar)[0];

    firstFocusable?.focus();
  } else if (restoreFocus) {
    toggle.focus();
  }

  updateBodyScrollLock();
};

const setMobileInspectorOpen = (isOpen, restoreFocus = false) => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const inspector = document.querySelector(
    SELECTORS.dashboardInspector
  );
  const toggle = document.querySelector(
    SELECTORS.mobileInspectorToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.inspectorBackdrop
  );
  const closeButton = document.querySelector(
    SELECTORS.mobileInspectorClose
  );

  if (!shell || !inspector || !toggle || !backdrop) {
    return;
  }

  if (isOpen) {
    setMobileSidebarOpen(false);
  }

  shell.classList.toggle(
    "dashboard-shell--mobile-inspector-open",
    isOpen
  );

  toggle.setAttribute(
    "aria-expanded",
    String(isOpen)
  );

  toggle.setAttribute(
    "aria-label",
    isOpen
      ? "Close map and place details"
      : "Open map and place details"
  );

  backdrop.hidden = !isOpen;

  syncMobileDrawerAccessibility();

  if (isOpen) {
    closeButton?.focus();
  } else if (restoreFocus) {
    toggle.focus();
  }

  updateBodyScrollLock();
};

const initializeMobileSidebar = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const drawer = document.querySelector(
    SELECTORS.dashboardSidebar
  );
  const toggle = document.querySelector(
    SELECTORS.mobileSidebarToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.sidebarBackdrop
  );

  if (!shell || !drawer || !toggle || !backdrop) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isOpen = shell.classList.contains(
      "dashboard-shell--mobile-sidebar-open"
    );

    setMobileSidebarOpen(!isOpen);
  });

  backdrop.addEventListener("click", () => {
    setMobileSidebarOpen(false, true);
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Tab" &&
      shell.classList.contains(
        "dashboard-shell--mobile-sidebar-open"
      )
    ) {
      trapFocusWithin(event, drawer);
    }

    if (
      event.key === "Escape" &&
      shell.classList.contains(
        "dashboard-shell--mobile-sidebar-open"
      )
    ) {
      setMobileSidebarOpen(false, true);
    }
  });

  window.addEventListener("resize", () => {
    if (
      window.innerWidth > 760 &&
      shell.classList.contains(
        "dashboard-shell--mobile-sidebar-open"
      )
    ) {
      setMobileSidebarOpen(false);
    }

    syncMobileDrawerAccessibility();
  });
};

const initializeMobileInspector = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const drawer = document.querySelector(
    SELECTORS.dashboardInspector
  );
  const toggle = document.querySelector(
    SELECTORS.mobileInspectorToggle
  );
  const closeButton = document.querySelector(
    SELECTORS.mobileInspectorClose
  );
  const backdrop = document.querySelector(
    SELECTORS.inspectorBackdrop
  );

  if (
    !shell ||
    !drawer ||
    !toggle ||
    !closeButton ||
    !backdrop
  ) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isOpen = shell.classList.contains(
      "dashboard-shell--mobile-inspector-open"
    );

    setMobileInspectorOpen(!isOpen);
  });

  closeButton.addEventListener("click", () => {
    setMobileInspectorOpen(false, true);
  });

  backdrop.addEventListener("click", () => {
    setMobileInspectorOpen(false, true);
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Tab" &&
      shell.classList.contains(
        "dashboard-shell--mobile-inspector-open"
      )
    ) {
      trapFocusWithin(event, drawer);
    }

    if (
      event.key === "Escape" &&
      shell.classList.contains(
        "dashboard-shell--mobile-inspector-open"
      )
    ) {
      setMobileInspectorOpen(false, true);
    }
  });

  window.addEventListener("resize", () => {
    if (
      window.innerWidth > 900 &&
      shell.classList.contains(
        "dashboard-shell--mobile-inspector-open"
      )
    ) {
      setMobileInspectorOpen(false);
    }

    syncMobileDrawerAccessibility();
  });
};

const searchPlaces = async (query) => {
  const response = await fetch("/api/v1/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      location: {
        latitude: 43.6591,
        longitude: -70.2568,
      },
    }),
  });

  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    const message =
      data.error?.message ||
      "CityGuide could not complete your search.";

    throw new Error(message);
  }

  return data;
};

const loadInitialDashboardResults = async () => {
  const status = document.querySelector(
    SELECTORS.searchStatus
  );

  let searchSucceeded = false;

  setSearchLoadingState(true);

  if (status) {
    status.textContent =
      "Loading initial recommendations.";
  }

  try {
    const searchResponse = await searchPlaces(
      INITIAL_SEARCH_QUERY
    );

    applySearchResults(searchResponse.results);

    if (searchResponse.results.length === 0) {
      showResultsState({
        title: "No matching places found",
        message:
          "Try changing your search or using fewer filters.",
      });
    } else {
      hideResultsState();
    }
    searchSucceeded = true;

    if (status) {
      status.textContent =
        `Loaded ${searchResponse.result_count} initial results.`;
    }
  } catch (error) {
    if (status) {
      status.textContent =
        "The initial recommendations could not be loaded.";
    }

    showResultsState({
      title: "Recommendations unavailable",
      message:
        error instanceof Error
          ? error.message
          : "Please refresh the page and try again.",
      isError: true,
    });

    console.error(
      "CityGuide initial search failed:",
      error
    );
  } finally {
    if (searchSucceeded) {
      setSearchLoadingState(false);
    } else {
      const progress = document.querySelector(
        SELECTORS.searchProgress
      );
      const title = document.querySelector(
        SELECTORS.searchProgressTitle
      );
      const progressStatus = document.querySelector(
        SELECTORS.searchProgressStatus
      );

      progress?.setAttribute("aria-busy", "false");

      if (title) {
        title.textContent =
          "Local business search unavailable";
      }

      if (progressStatus) {
        progressStatus.textContent = "Error";
      }
    }
  }
};

const setSearchLoadingState = (isLoading) => {
  const progress = document.querySelector(
    SELECTORS.searchProgress
  );
  const title = document.querySelector(
    SELECTORS.searchProgressTitle
  );
  const progressStatus = document.querySelector(
    SELECTORS.searchProgressStatus
  );

  if (!progress || !title || !progressStatus) {
    return;
  }

  progress.setAttribute(
    "aria-busy",
    String(isLoading)
  );

  title.textContent = isLoading
    ? "Searching local businesses..."
    : "Local business search complete";

  progressStatus.textContent = isLoading
    ? "Searching"
    : "Complete";
};

const hideResultsState = () => {
  const state = document.querySelector(
    SELECTORS.resultsState
  );

  if (state) {
    state.hidden = true;
    state.classList.remove(
      "dashboard-results-state--error"
    );
  }
};

const showResultsState = ({
  title,
  message,
  isError = false,
}) => {
  const state = document.querySelector(
    SELECTORS.resultsState
  );
  const titleElement = document.querySelector(
    SELECTORS.resultsStateTitle
  );
  const messageElement = document.querySelector(
    SELECTORS.resultsStateMessage
  );

  if (!state || !titleElement || !messageElement) {
    return;
  }

  titleElement.textContent = title;
  messageElement.textContent = message;

  state.classList.toggle(
    "dashboard-results-state--error",
    isError
  );

  state.hidden = false;
  hydrateDashboardIcons();
};

const applySearchResults = (places) => {
  updateCurrentPlaces(places);

  renderRecommendationCards(places);
  renderInspectorResults(places);
  renderMapMarkers(places);

  if (places.length > 0) {
    selectPlace(places[0].id);
  }
};

const clearSearchResults = () => {
  applySearchResults([]);
};

const initializeDashboardSearch = () => {
  const form = document.querySelector(
    SELECTORS.searchForm
  );

  const input = document.querySelector(
    SELECTORS.searchInput
  );

  const submitButton = document.querySelector(
    SELECTORS.searchSubmit
  );

  const status = document.querySelector(
    SELECTORS.searchStatus
  );

  if (!form || !input || !submitButton || !status) {
    return;
  }

  const updateSubmitState = () => {
    submitButton.disabled =
      input.value.trim().length === 0;
  };

  input.addEventListener("input", updateSubmitState);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = input.value.trim();

    if (!query) {
      status.textContent =
        "Please enter a search query.";
      updateSubmitState();
      input.focus();
      return;
    }

    input.disabled = true;
    submitButton.disabled = true;
    setSearchLoadingState(true);
    hideResultsState();
    status.textContent =
      "Searching for local businesses.";

    try {
      const searchResponse = await searchPlaces(query);

      if (searchResponse.results.length === 0) {
        clearSearchResults();

        showResultsState({
          title: "No matching places found",
          message:
            "Try changing your wording, increasing the distance, or removing one preference.",
        });

        status.textContent =
          "Search complete. No matching places found.";

        return;
      }

      status.textContent =
        `Search complete. Found ` +
        `${searchResponse.result_count} results.`;

      applySearchResults(searchResponse.results);

      console.log(
        "CityGuide search response:",
        searchResponse
      );
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "CityGuide could not complete your search.";

      status.textContent = message;

      showResultsState({
        title: "We could not complete your search",
        message,
        isError: true,
      });

      console.error("CityGuide search failed:", error);
    } finally {
      setSearchLoadingState(false);
      input.disabled = false;
      updateSubmitState();
      input.focus();
    }
  });

  updateSubmitState();
};

const initializeDashboard = () => {
  initializeFilterChips();
  initializeRecommendationCards();
  initializeMapMarkers();
  initializeInspectorTabs();
  initializeInspectorResults();
  activateInspectorTab("map");
  initializeSidebarToggle();
  initializeMobileSidebar();
  initializeMobileInspector();
  initializeDashboardSearch();
  loadInitialDashboardResults();
  syncMobileDrawerAccessibility();
};

document.addEventListener("DOMContentLoaded", initializeDashboard);

if (typeof window.requestIdleCallback === "function") {
  window.requestIdleCallback(hydrateDashboardIcons);
} else {
  window.setTimeout(hydrateDashboardIcons, 0);
}