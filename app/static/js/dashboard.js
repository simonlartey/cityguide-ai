const SELECTORS = {
  conversation: "#dashboard-conversation",
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
  searchProgressItems: ".search-progress-list li",
  resultsState: "#dashboard-results-state",
  resultsStateTitle: "[data-results-state-title]",
  resultsStateMessage: "[data-results-state-message]",
  placeHero: "[data-place-hero]",
  placeGallery: "[data-place-gallery]",
  placePhotoAttribution:
    "[data-place-photo-attribution]",
};

let PLACES = {};
let latestSearchRequestId = 0;

const hydrateDashboardIcons = () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
};

const formatMessageTime = (date = new Date()) =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(date);

const createMessageAvatar = (role) => {
  const avatar = document.createElement("div");

  avatar.className =
    `message-avatar message-avatar--${role}`;

  if (role === "user") {
    avatar.textContent = "SL";
    avatar.setAttribute("aria-label", "Simon Lartey");
  } else {
    avatar.textContent = "✦";
    avatar.setAttribute("aria-hidden", "true");
  }

  return avatar;
};

const createConversationMessage = ({
  role,
  text,
  pending = false,
}) => {
  const row = document.createElement("div");

  row.className =
    `message-row message-row--${role}`;

  const bubble = document.createElement("article");

  bubble.className =
    `message-bubble message-bubble--${role}`;

  const message = document.createElement("p");
  message.textContent = text;

  // Add a visually hidden sender label for screen readers
  const sender = document.createElement("span");
  sender.className = "sr-only";
  sender.textContent = role === "user" ? "You:" : "CityGuide AI:";

  const time = document.createElement("time");
  const now = new Date();

  time.dateTime = now.toISOString();
  time.textContent = formatMessageTime(now);

  bubble.append(sender, message, time);

  if (pending) {
    bubble.dataset.pendingMessage = "";
    bubble.setAttribute("aria-busy", "true");
  }

  const avatar = createMessageAvatar(role);

  if (role === "user") {
    row.append(bubble, avatar);
  } else {
    row.append(avatar, bubble);
  }

  return {
    row,
    bubble,
    message,
  };
};

const scrollConversationToLatest = () => {
  const conversation = document.querySelector(
    SELECTORS.conversation
  );

  if (!conversation) {
    return;
  }

  conversation.lastElementChild?.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
  });
};

const appendConversationMessage = ({
  role,
  text,
  pending = false,
}) => {
  const conversation = document.querySelector(
    SELECTORS.conversation
  );

  if (!conversation) {
    return null;
  }

  const renderedMessage = createConversationMessage({
    role,
    text,
    pending,
  });

  conversation.append(renderedMessage.row);
  scrollConversationToLatest();

  return renderedMessage;
};

const updateConversationMessage = (
  renderedMessage,
  text
) => {
  if (!renderedMessage) {
    return;
  }

  renderedMessage.message.textContent = text;
  renderedMessage.bubble.removeAttribute(
    "data-pending-message"
  );
  renderedMessage.bubble.setAttribute(
    "aria-busy",
    "false"
  );

  scrollConversationToLatest();
};

const buildSearchResultMessage = (
  query,
  resultCount
) => {
  const resultLabel =
    resultCount === 1 ? "place" : "places";

  return (
    `I found ${resultCount} ${resultLabel} matching ` +
    `“${query}” near Portland. Here are the local ` +
    "options I found."
  );
};

const formatPriceLevel = (priceLevel) => {
  if (!Number.isInteger(priceLevel) || priceLevel < 1) {
    return "";
  }

  return "$".repeat(priceLevel);
};

const formatRating = (rating) => {
  if (typeof rating !== "number") {
    return "Not rated";
  }

  return String(rating);
};

const formatDistance = (distanceMiles) => {
  if (typeof distanceMiles !== "number") {
    return "Distance unavailable";
  }

  return `${distanceMiles} mi`;
};

const formatOpenStatus = (openNow) => {
  if (openNow === true) {
    return "Open now";
  }

  if (openNow === false) {
    return "Closed";
  }

  return "Hours unavailable";
};

const buildPlacePhotoUrl = (
  photo,
  width = 800
) => {
  const photoName = photo?.name;

  if (
    typeof photoName !== "string" ||
    photoName.trim().length === 0
  ) {
    return null;
  }

  const params = new URLSearchParams({
    name: photoName,
    width: String(width),
  });

  return `/api/v1/place-photo?${params.toString()}`;
};

const getPhotoAttributionNames = (photo) => {
  const attributions = photo?.author_attributions;

  if (!Array.isArray(attributions)) {
    return [];
  }

  return attributions
    .map((attribution) => attribution?.displayName)
    .filter(
      (name) =>
        typeof name === "string" &&
        name.trim().length > 0
    );
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
  rating: place.rating,
  ratingLabel: formatRating(place.rating),
  distance: formatDistance(place.distance_miles),
  price:
    formatPriceLevel(place.price_level) ||
    "Price unavailable",
  status: formatOpenStatus(place.open_now),
  hours: place.hours_text || "Hours unavailable",
  primaryPhoto:
    Array.isArray(place.photos) &&
    place.photos.length > 0
      ? place.photos[0]
      : null,
  photos: Array.isArray(place.photos) ? place.photos : [],
  heroClass: getRecommendationImageClass(index).replace(
    "recommendation-image",
    "place-hero"
  ),
  reasons: Array.isArray(place.match_reasons)
    ? place.match_reasons
    : [],
});

const updateCurrentPlaces = (places) => {
  const normalizedPlaces = places.map(
    normalizePlaceForDashboard
  );

  PLACES = Object.fromEntries(
    normalizedPlaces.map((place) => [
      place.id,
      place,
    ])
  );

  return normalizedPlaces;
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

  const photoUrl = buildPlacePhotoUrl(
    place.primaryPhoto,
    800
  );

  if (photoUrl) {
    const photo = document.createElement("img");
    const authorAttributions =
      place.primaryPhoto?.author_attributions;

    photo.className = "recommendation-photo";
    photo.src = photoUrl;
    photo.alt = `${place.name} location`;
    photo.loading = "lazy";
    photo.decoding = "async";

    if (
      Array.isArray(authorAttributions) &&
      authorAttributions.length > 0
    ) {
      const names = authorAttributions
        .map((attribution) => attribution?.displayName)
        .filter(Boolean);

      if (names.length > 0) {
        photo.dataset.photoAttribution =
          names.join(", ");
      }
    }

    photo.addEventListener("error", () => {
      photo.remove();

      image.classList.remove(
        "recommendation-image--has-photo"
      );
    });

    image.classList.add(
      "recommendation-image--has-photo"
    );
    image.append(photo);
  }

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
  if (typeof place.rating === "number") {
    const reviewCount =
      Number.isInteger(place.review_count)
        ? ` (${place.review_count})`
        : "";

    rating.textContent =
      `★ ${place.rating}${reviewCount}`;
  } else {
    rating.textContent = "Not rated";
  }

  const distance = document.createElement("span");
  distance.textContent = formatDistance(place.distance_miles);

  const price = document.createElement("span");
  price.textContent =
    formatPriceLevel(place.price_level) ||
    "Price unavailable";

  const availability = document.createElement("span");
  availability.className = "availability-pill";
  availability.textContent = formatOpenStatus(place.open_now);

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
    formatRating(place.rating),
    formatDistance(place.distance_miles),
    formatPriceLevel(place.price_level) || "Price unavailable",
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

const createPlaceGalleryThumbnail = (
  place,
  photo,
  index
) => {
  const thumbnail = document.createElement("button");

  thumbnail.type = "button";
  thumbnail.className = "place-gallery-thumbnail";
  thumbnail.setAttribute(
    "aria-label",
    `View photo ${index + 1} of ${place.name}`
  );

  const photoUrl = buildPlacePhotoUrl(photo, 400);

  if (!photoUrl) {
    thumbnail.disabled = true;
    return thumbnail;
  }

  const image = document.createElement("img");

  image.src = photoUrl;
  image.alt = "";
  image.loading = "lazy";
  image.decoding = "async";

  image.addEventListener("error", () => {
    thumbnail.remove();
  });

  thumbnail.append(image);

  thumbnail.addEventListener("click", () => {
    updateSelectedPlacePhoto(
      place,
      photo,
      index
    );
  });

  return thumbnail;
};

const updateSelectedPlacePhoto = (
  place,
  photo,
  activeIndex = 0
) => {
  const hero = document.querySelector(
    SELECTORS.placeHero
  );
  const heroPhoto = hero?.querySelector(
    "[data-place-hero-photo]"
  );
  const attribution = document.querySelector(
    SELECTORS.placePhotoAttribution
  );

  if (!hero || !heroPhoto || !attribution) {
    return;
  }

  const photoUrl = buildPlacePhotoUrl(photo, 1600);

  hero
    .querySelectorAll(".place-gallery-thumbnail")
    .forEach((thumbnail, index) => {
      thumbnail.classList.toggle(
        "place-gallery-thumbnail--active",
        index === activeIndex
      );
    });

  if (!photoUrl) {
    heroPhoto.hidden = true;
    heroPhoto.removeAttribute("src");
    hero.classList.remove("place-hero--has-photo");
    attribution.hidden = true;
    attribution.textContent = "";
    return;
  }

  heroPhoto.src = photoUrl;
  heroPhoto.alt = `${place.name} location`;
  heroPhoto.hidden = false;
  hero.classList.add("place-hero--has-photo");

  const attributionNames =
    getPhotoAttributionNames(photo);

  if (attributionNames.length > 0) {
    attribution.textContent =
      `Photo: ${attributionNames.join(", ")}`;
    attribution.hidden = false;
  } else {
    attribution.textContent = "";
    attribution.hidden = true;
  }

  heroPhoto.onerror = () => {
    heroPhoto.hidden = true;
    heroPhoto.removeAttribute("src");
    hero.classList.remove("place-hero--has-photo");
    attribution.hidden = true;
    attribution.textContent = "";
  };
};

const renderSelectedPlacePhotos = (place) => {
  const gallery = document.querySelector(
    SELECTORS.placeGallery
  );

  if (!gallery) {
    return;
  }

  const photos = place.photos.slice(0, 4);

  gallery.replaceChildren(
    ...photos.map((photo, index) =>
      createPlaceGalleryThumbnail(
        place,
        photo,
        index
      )
    )
  );

  gallery.hidden = photos.length === 0;

  updateSelectedPlacePhoto(
    place,
    photos[0] || null,
    0
  );
};

const updatePlaceDetails = (placeId) => {
  const place = PLACES[placeId];

  if (!place) {
    return;
  }

  document.querySelector("[data-place-name]").textContent =
    place.name;

  const ratingLabel =
    typeof place.rating === "number"
      ? Number.isInteger(place.review_count)
        ? `${place.rating} (${place.review_count} reviews)`
        : String(place.rating)
      : "Not rated";
  const distanceLabel =
    place.distance ||
    formatDistance(place.distance_miles);
  const priceLabel =
    place.price ||
    formatPriceLevel(place.price_level) ||
    "Price unavailable";
  const statusLabel =
    place.status ||
    formatOpenStatus(place.open_now);

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

  const hero = document.querySelector(
    SELECTORS.placeHero
  );

  if (hero) {
    hero.classList.remove(
      "place-hero--one",
      "place-hero--two",
      "place-hero--three"
    );
    hero.classList.add(place.heroClass);
  }

  renderSelectedPlacePhotos(place);

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

const clearSelectedPlaceDetails = () => {
  const name = document.querySelector("[data-place-name]");
  const rating = document.querySelector("[data-place-rating]");
  const distance = document.querySelector("[data-place-distance]");
  const price = document.querySelector("[data-place-price]");
  const status = document.querySelector("[data-place-status]");
  const address = document.querySelector("[data-place-address]");
  const hours = document.querySelector("[data-place-hours]");
  const reasons = document.querySelector("[data-place-reasons]");
  const hero = document.querySelector(
    SELECTORS.placeHero
  );
  const heroPhoto = hero?.querySelector(
    "[data-place-hero-photo]"
  );
  const gallery = document.querySelector(
    SELECTORS.placeGallery
  );
  const attribution = document.querySelector(
    SELECTORS.placePhotoAttribution
  );

  if (name) {
    name.textContent = "No place selected";
  }

  if (rating) {
    rating.textContent = "Rating unavailable";
  }

  if (distance) {
    distance.textContent = "Distance unavailable";
  }

  if (price) {
    price.textContent = "Price unavailable";
  }

  if (status) {
    status.textContent = "Unavailable";
  }

  if (address) {
    address.textContent = "Address unavailable";
  }

  if (hours) {
    hours.textContent = "Hours unavailable";
  }

  if (reasons) {
    reasons.replaceChildren();
  }

  if (hero && heroPhoto) {
    hero.classList.remove("place-hero--has-photo");
    heroPhoto.hidden = true;
    heroPhoto.removeAttribute("src");
    heroPhoto.alt = "";
  }

  if (gallery) {
    gallery.replaceChildren();
    gallery.hidden = true;
  }

  if (attribution) {
    attribution.textContent = "";
    attribution.hidden = true;
  }
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

const searchPlaces = async (query, { signal } = {}) => {
  const response = await fetch("/api/v1/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    signal,
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

  setSearchProgressItemsState(
    isLoading ? "active" : "complete"
  );
};

const setSearchProgressItemsState = (state) => {
  document
    .querySelectorAll(SELECTORS.searchProgressItems)
    .forEach((item) => {
      item.dataset.progressState = state;
    });
};

const setSearchErrorState = () => {
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

  progress.setAttribute("aria-busy", "false");
  title.textContent = "Local business search unavailable";
  progressStatus.textContent = "Error";
  setSearchProgressItemsState("error");
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
  const normalizedPlaces =
    updateCurrentPlaces(places);

  renderRecommendationCards(normalizedPlaces);
  renderInspectorResults(normalizedPlaces);
  renderMapMarkers(normalizedPlaces);

  if (normalizedPlaces.length > 0) {
    selectPlace(normalizedPlaces[0].id);
  } else {
    clearSelectedPlaceDetails();
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

    const requestId = ++latestSearchRequestId;

    appendConversationMessage({
      role: "user",
      text: query,
    });

    const pendingAssistantMessage =
      appendConversationMessage({
        role: "assistant",
        text: "Searching for local places...",
        pending: true,
      });

    input.value = "";

    input.disabled = true;
    submitButton.disabled = true;

    setSearchLoadingState(true);
    hideResultsState();

    status.textContent =
      "Searching for local businesses.";

    let searchFailed = false;

    const controller = new AbortController();
    const timeoutId = window.setTimeout(
      () => controller.abort(),
      15000
    );

    try {
      const searchResponse = await searchPlaces(query, {
        signal: controller.signal,
      });

      if (requestId !== latestSearchRequestId) {
        return;
      }

      if (searchResponse.results.length === 0) {
        clearSearchResults();

        updateConversationMessage(
          pendingAssistantMessage,
          "I couldn’t find matching places for that request. " +
            "Try changing the wording or broadening your search."
        );

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

      updateConversationMessage(
        pendingAssistantMessage,
        buildSearchResultMessage(
          query,
          searchResponse.result_count
        )
      );

      console.log(
        "CityGuide search response:",
        searchResponse
      );
    } catch (error) {
      if (requestId !== latestSearchRequestId) {
        return;
      }

      clearSearchResults();

      searchFailed = true;

      const requestTimedOut =
        error instanceof Error &&
        error.name === "AbortError";

      const message = requestTimedOut
        ? "The search took too long. Please try again."
        : error instanceof Error
        ? error.message
        : "CityGuide could not complete your search.";

      status.textContent = message;

      updateConversationMessage(
        pendingAssistantMessage,
        requestTimedOut
          ? "The local search took too long. Please try again."
          : "I couldn’t load local recommendations right now. " +
              "Please try again."
      );

      showResultsState({
        title: "We could not complete your search",
        message,
        isError: true,
      });

      console.error("CityGuide search failed:", error);
    } finally {
      window.clearTimeout(timeoutId);

      if (requestId !== latestSearchRequestId) {
        return;
      }

      if (searchFailed) {
        setSearchErrorState();
      } else {
        setSearchLoadingState(false);
      }
      input.disabled = false;
      updateSubmitState();
      input.focus();
    }
  });

  updateSubmitState();
};

const initializeConversation = () => {
  appendConversationMessage({
    role: "assistant",
    text:
      "Hi! Tell me what kind of place, service, food, or activity " +
      "you are looking for in Portland.",
  });
};

const initializeDashboard = () => {
  initializeConversation();
  setSearchProgressItemsState("ready");
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
  syncMobileDrawerAccessibility();
};

document.addEventListener("DOMContentLoaded", initializeDashboard);

if (typeof window.requestIdleCallback === "function") {
  window.requestIdleCallback(hydrateDashboardIcons);
} else {
  window.setTimeout(hydrateDashboardIcons, 0);
}