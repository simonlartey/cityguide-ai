"use strict";

const SELECTORS = Object.freeze({
  form: ".auth-form",
  passwordToggle: "[data-password-toggle]",
  googleButton: '[data-auth-provider="google"]',
  formMessage: ".form-message",
});

const FIELD_IDS = Object.freeze({
  email: "email",
  password: "password",
  confirmPassword: "confirm-password",
  displayName: "display-name",
  terms: "terms",
});

const ERROR_IDS = Object.freeze({
  email: "email-error",
  password: "password-error",
  confirmPassword: "confirm-password-error",
  displayName: "display-name-error",
  terms: "terms-error",
});

function getElement(id) {
  return document.getElementById(id);
}

function getErrorElement(fieldName) {
  const errorId = ERROR_IDS[fieldName];

  return errorId ? getElement(errorId) : null;
}

function setFieldError(field, message) {
  if (!field) {
    return;
  }

  const errorElement = getErrorElement(field.name);

  field.setAttribute("aria-invalid", "true");
  field.classList.add("is-invalid");

  if (errorElement) {
    errorElement.textContent = message;
  }
}

function clearFieldError(field) {
  if (!field) {
    return;
  }

  const errorElement = getErrorElement(field.name);

  field.removeAttribute("aria-invalid");
  field.classList.remove("is-invalid");

  if (errorElement) {
    errorElement.textContent = "";
  }
}

function clearFormMessage(form) {
  const messageElement = form.querySelector(SELECTORS.formMessage);

  if (!messageElement) {
    return;
  }

  messageElement.textContent = "";
  messageElement.hidden = true;
}

function showFormMessage(form, message) {
  const messageElement = form.querySelector(SELECTORS.formMessage);

  if (!messageElement) {
    return;
  }

  messageElement.textContent = message;
  messageElement.hidden = false;
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isStrongEnoughPassword(value) {
  const hasLetter = /[A-Za-z]/.test(value);
  const hasNumber = /\d/.test(value);

  return value.length >= 8 && hasLetter && hasNumber;
}

function validateDisplayName(field) {
  if (!field) {
    return true;
  }

  const value = field.value.trim();

  if (!value) {
    setFieldError(field, "Enter your full name.");
    return false;
  }

  if (value.length < 2) {
    setFieldError(field, "Name must contain at least 2 characters.");
    return false;
  }

  clearFieldError(field);
  return true;
}

function validateEmail(field) {
  if (!field) {
    return true;
  }

  const value = field.value.trim();

  if (!value) {
    setFieldError(field, "Enter your email address.");
    return false;
  }

  if (!isValidEmail(value)) {
    setFieldError(field, "Enter a valid email address.");
    return false;
  }

  clearFieldError(field);
  return true;
}

function validatePassword(field, isSignup) {
  if (!field) {
    return true;
  }

  const value = field.value;

  if (!value) {
    setFieldError(field, "Enter your password.");
    return false;
  }

  if (value.length < 8) {
    setFieldError(field, "Password must contain at least 8 characters.");
    return false;
  }

  if (isSignup && !isStrongEnoughPassword(value)) {
    setFieldError(
      field,
      "Use at least 8 characters with a mix of letters and numbers."
    );
    return false;
  }

  clearFieldError(field);
  return true;
}

function validateConfirmPassword(field, passwordField) {
  if (!field) {
    return true;
  }

  if (!field.value) {
    setFieldError(field, "Confirm your password.");
    return false;
  }

  if (!passwordField || field.value !== passwordField.value) {
    setFieldError(field, "Passwords do not match.");
    return false;
  }

  clearFieldError(field);
  return true;
}

function validateTerms(field) {
  if (!field) {
    return true;
  }

  const errorElement = getErrorElement("terms");

  if (!field.checked) {
    field.setAttribute("aria-invalid", "true");

    if (errorElement) {
      errorElement.textContent =
        "You must agree to the Terms of Service and Privacy Policy.";
    }

    return false;
  }

  field.removeAttribute("aria-invalid");

  if (errorElement) {
    errorElement.textContent = "";
  }

  return true;
}

function validateForm(form) {
  const isSignup = form.dataset.authForm === "signup";

  const displayNameField = getElement(FIELD_IDS.displayName);
  const emailField = getElement(FIELD_IDS.email);
  const passwordField = getElement(FIELD_IDS.password);
  const confirmPasswordField = getElement(FIELD_IDS.confirmPassword);
  const termsField = getElement(FIELD_IDS.terms);

  const validations = [
    validateDisplayName(displayNameField),
    validateEmail(emailField),
    validatePassword(passwordField, isSignup),
    validateConfirmPassword(confirmPasswordField, passwordField),
    validateTerms(termsField),
  ];

  return validations.every(Boolean);
}

function setSubmittingState(form, isSubmitting) {
  const submitButton = form.querySelector('button[type="submit"]');

  if (!submitButton) {
    return;
  }

  submitButton.disabled = isSubmitting;
  submitButton.setAttribute("aria-busy", String(isSubmitting));

  const label = submitButton.querySelector("span");

  if (label) {
    if (!submitButton.dataset.defaultLabel) {
      submitButton.dataset.defaultLabel = label.textContent.trim();
    }

    label.textContent = isSubmitting
      ? "Please wait..."
      : submitButton.dataset.defaultLabel;
  }
}

function initializePasswordToggles() {
  const toggles = document.querySelectorAll(SELECTORS.passwordToggle);

  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const passwordField = toggle.closest(".password-field");
      const input = passwordField?.querySelector("input");
      const showIcon = toggle.querySelector(".password-icon-show");
      const hideIcon = toggle.querySelector(".password-icon-hide");

      if (!input) {
        return;
      }

      const isVisible = input.type === "text";

      input.type = isVisible ? "password" : "text";
      toggle.setAttribute("aria-pressed", String(!isVisible));
      toggle.setAttribute(
        "aria-label",
        isVisible ? "Show password" : "Hide password"
      );

      if (showIcon) {
        showIcon.hidden = !isVisible;
      }

      if (hideIcon) {
        hideIcon.hidden = isVisible;
      }
    });
  });
}

function initializeLiveValidation(form) {
  const fields = form.querySelectorAll("input");

  fields.forEach((field) => {
    field.addEventListener("input", () => {
      clearFormMessage(form);

      switch (field.name) {
        case "displayName":
          validateDisplayName(field);
          break;

        case "email":
          validateEmail(field);
          break;

        case "password": {
          validatePassword(
            field,
            form.dataset.authForm === "signup"
          );

          const confirmPassword = getElement(
            FIELD_IDS.confirmPassword
          );

          if (confirmPassword?.value) {
            validateConfirmPassword(confirmPassword, field);
          }

          break;
        }

        case "confirmPassword":
          validateConfirmPassword(
            field,
            getElement(FIELD_IDS.password)
          );
          break;

        default:
          break;
      }
    });

    field.addEventListener("blur", () => {
      switch (field.name) {
        case "displayName":
          validateDisplayName(field);
          break;

        case "email":
          validateEmail(field);
          break;

        case "password":
          validatePassword(
            field,
            form.dataset.authForm === "signup"
          );
          break;

        case "confirmPassword":
          validateConfirmPassword(
            field,
            getElement(FIELD_IDS.password)
          );
          break;

        default:
          break;
      }
    });

    if (field.name === "terms") {
      field.addEventListener("change", () => {
        validateTerms(field);
      });
    }
  });
}

function initializeAuthForms() {
  const forms = document.querySelectorAll(SELECTORS.form);

  forms.forEach((form) => {
    initializeLiveValidation(form);

    form.addEventListener("submit", (event) => {
      clearFormMessage(form);

      if (!validateForm(form)) {
        event.preventDefault();

        const firstInvalidField = form.querySelector(
          '[aria-invalid="true"]'
        );

        firstInvalidField?.focus();
        return;
      }

      setSubmittingState(form, true);
    });
  });
}

function initializeGoogleButtons() {
  const buttons = document.querySelectorAll(
    SELECTORS.googleButton
  );

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const form =
        button.closest(".auth-panel-content")?.querySelector(
          SELECTORS.form
        );

      if (form) {
        showFormMessage(
          form,
          "Google authentication will be connected in the backend milestone."
        );
      }
    });
  });
}

function initializeAuthPage() {
  initializePasswordToggles();
  initializeAuthForms();
  initializeGoogleButtons();
}

document.addEventListener("DOMContentLoaded", initializeAuthPage);