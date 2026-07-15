const SELECTORS = {
  filterChip: "[data-filter]",
  recommendationCard: "[data-recommendation-card]",
  placeMarker: "[data-place-marker]",
  sidebarShell: "#dashboard-shell",
  sidebarToggle: "[data-sidebar-toggle]",
  sidebarToggleIcon: "[data-sidebar-toggle-icon]",
  mobileSidebarToggle: "[data-mobile-sidebar-toggle]",
  sidebarBackdrop: "[data-sidebar-backdrop]",
  inspectorTab: "[data-inspector-tab]",
  inspectorPanel: "[data-inspector-panel]",
  placeResult: "[data-place-result]",
  mobileInspectorToggle: "[data-mobile-inspector-toggle]",
  mobileInspectorClose: "[data-mobile-inspector-close]",
  inspectorBackdrop: "[data-inspector-backdrop]",
};

const PLACES = {
  "portland-fade-studio": {
    name: "Portland Fade Studio",
    rating: "4.9 (527 reviews)",
    distance: "0.4 mi",
    price: "$$",
    status: "Open now",
    address: "123 Congress St, Portland, ME 04101",
    hours: "Open today: 9:00 AM – 7:00 PM",
    heroClass: "place-hero--one",
    reasons: [
      "Specializes in textured hair and modern fades",
      "Highly rated by customers with similar hair types",
      "Affordable pricing",
      "Close to your location",
    ],
  },
  "crown-and-co": {
    name: "Crown & Co. Barbershop",
    rating: "4.8 (319 reviews)",
    distance: "0.7 mi",
    price: "$$",
    status: "Open now",
    address: "75 Middle St, Portland, ME 04101",
    hours: "Open today: 10:00 AM – 8:00 PM",
    heroClass: "place-hero--two",
    reasons: [
      "Experienced with curls, coils, and textured styles",
      "Offers student discounts",
      "Strong customer service ratings",
      "Convenient downtown location",
    ],
  },
  "elevate-cuts": {
    name: "Elevate Cuts",
    rating: "4.7 (214 reviews)",
    distance: "1.1 mi",
    price: "$",
    status: "Open now",
    address: "210 Forest Ave, Portland, ME 04101",
    hours: "Open today: 8:30 AM – 6:30 PM",
    heroClass: "place-hero--three",
    reasons: [
      "Budget-friendly pricing",
      "Strong experience with curls and waves",
      "Fast appointment availability",
      "Good option for students",
    ],
  },
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

const updatePlaceDetails = (placeId) => {
  const place = PLACES[placeId];

  if (!place) {
    return;
  }

  document.querySelector("[data-place-name]").textContent =
    place.name;
  document.querySelector("[data-place-rating]").textContent =
    place.rating;
  document.querySelector("[data-place-distance]").textContent =
    place.distance;
  document.querySelector("[data-place-price]").textContent =
    place.price;
  document.querySelector("[data-place-status]").textContent =
    place.status;
  document.querySelector("[data-place-address]").textContent =
    place.address;
  document.querySelector("[data-place-hours]").textContent =
    place.hours;

  const hero = document.querySelector("[data-place-hero]");

  hero.classList.remove(
    "place-hero--one",
    "place-hero--two",
    "place-hero--three"
  );
  hero.classList.add(place.heroClass);

  const reasons = document.querySelector("[data-place-reasons]");

  reasons.replaceChildren(
    ...place.reasons.map((reason) => {
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
  document
    .querySelectorAll(SELECTORS.inspectorTab)
    .forEach((tab) => {
      tab.addEventListener("click", () => {
        activateInspectorTab(tab.dataset.inspectorTab);
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

const setMobileSidebarOpen = (isOpen) => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const toggle = document.querySelector(
    SELECTORS.mobileSidebarToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.sidebarBackdrop
  );

  if (!shell || !toggle || !backdrop) {
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

  updateBodyScrollLock();
};

const setMobileInspectorOpen = (isOpen) => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const toggle = document.querySelector(
    SELECTORS.mobileInspectorToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.inspectorBackdrop
  );

  if (!shell || !toggle || !backdrop) {
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

  updateBodyScrollLock();
};

const initializeMobileSidebar = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
  );
  const toggle = document.querySelector(
    SELECTORS.mobileSidebarToggle
  );
  const backdrop = document.querySelector(
    SELECTORS.sidebarBackdrop
  );

  if (!shell || !toggle || !backdrop) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isOpen = shell.classList.contains(
      "dashboard-shell--mobile-sidebar-open"
    );

    setMobileSidebarOpen(!isOpen);
  });

  backdrop.addEventListener("click", () => {
    setMobileSidebarOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      shell.classList.contains(
        "dashboard-shell--mobile-sidebar-open"
      )
    ) {
      setMobileSidebarOpen(false);
      toggle.focus();
    }
  });
};

const initializeMobileInspector = () => {
  const shell = document.querySelector(
    SELECTORS.sidebarShell
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
    setMobileInspectorOpen(false);
    toggle.focus();
  });

  backdrop.addEventListener("click", () => {
    setMobileInspectorOpen(false);
    toggle.focus();
  });

  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      shell.classList.contains(
        "dashboard-shell--mobile-inspector-open"
      )
    ) {
      setMobileInspectorOpen(false);
      toggle.focus();
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
  });
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
};

document.addEventListener("DOMContentLoaded", initializeDashboard);

if (typeof window.requestIdleCallback === "function") {
  window.requestIdleCallback(hydrateDashboardIcons);
} else {
  window.setTimeout(hydrateDashboardIcons, 0);
}