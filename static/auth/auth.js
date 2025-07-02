// UI interactions only - no form submission
document.addEventListener("DOMContentLoaded", () => {
  initializeAuthUI()
})

function initializeAuthUI() {
  // Add input animations and interactions
  addInputAnimations()

  // Initialize password strength checker for signup
  const passwordInput = document.getElementById("password1")
  if (passwordInput) {
    passwordInput.addEventListener("input", function () {
      checkPasswordStrength(this.value)
    })
  }

  // Initialize password confirmation for signup
  const confirmPasswordInput = document.getElementById("password2")
  if (confirmPasswordInput) {
    confirmPasswordInput.addEventListener("input", () => {
      validatePasswordMatch()
    })
  }

  // Initialize email validation
  const emailInput = document.getElementById("email")
  if (emailInput) {
    emailInput.addEventListener("blur", function () {
      validateEmail(this.value)
    })
  }
}

function addInputAnimations() {
  const inputs = document.querySelectorAll(".form-input")

  inputs.forEach((input) => {
    input.addEventListener("focus", function () {
      this.parentElement.classList.add("focused")
    })

    input.addEventListener("blur", function () {
      this.parentElement.classList.remove("focused")
      if (this.value) {
        this.parentElement.classList.add("filled")
      } else {
        this.parentElement.classList.remove("filled")
      }
    })

    // Check if already filled on load
    if (input.value) {
      input.parentElement.classList.add("filled")
    }
  })
}

function checkPasswordStrength(password) {
  const strengthBar = document.querySelector(".strength-fill")
  const strengthText = document.querySelector(".strength-text")

  if (!strengthBar || !strengthText) return

  let strength = 0
  let text = "Weak"
  let color = "#e74c3c"

  // Length check
  if (password.length >= 8) strength += 25

  // Uppercase check
  if (/[A-Z]/.test(password)) strength += 25

  // Lowercase check
  if (/[a-z]/.test(password)) strength += 25

  // Number or special character check
  if (/[\d\W]/.test(password)) strength += 25

  // Update text and color based on strength
  if (strength >= 75) {
    text = "Strong"
    color = "#2ecc71"
  } else if (strength >= 50) {
    text = "Medium"
    color = "#f39c12"
  } else if (strength >= 25) {
    text = "Fair"
    color = "#e67e22"
  }

  strengthBar.style.width = strength + "%"
  strengthBar.style.background = color
  strengthText.textContent = `Password strength: ${text}`
  strengthText.style.color = color
}

function validatePasswordMatch() {
  const password = document.getElementById("password1")?.value
  const confirmPassword = document.getElementById("password2")?.value
  const confirmInput = document.getElementById("password2")

  if (!confirmInput) return

  const validation = confirmInput.parentElement.querySelector(".input-validation")

  if (confirmPassword && password === confirmPassword) {
    confirmInput.classList.add("valid")
    confirmInput.classList.remove("invalid")
    if (validation) validation.classList.add("valid")
  } else if (confirmPassword) {
    confirmInput.classList.add("invalid")
    confirmInput.classList.remove("valid")
    if (validation) validation.classList.remove("valid")
  }
}

function validateEmail(email) {
  const emailInput = document.getElementById("email")
  if (!emailInput) return

  const validation = emailInput.parentElement.querySelector(".input-validation")
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (emailRegex.test(email)) {
    emailInput.classList.add("valid")
    emailInput.classList.remove("invalid")
    if (validation) validation.classList.add("valid")
    return true
  } else if (email) {
    emailInput.classList.add("invalid")
    emailInput.classList.remove("valid")
    if (validation) validation.classList.remove("valid")
    return false
  }
  return true
}

function togglePassword(inputId) {
  const input = document.getElementById(inputId)
  if (!input) return

  const toggle = input.parentElement.querySelector(".password-toggle i")

  if (input.type === "password") {
    input.type = "text"
    toggle.classList.remove("fa-eye")
    toggle.classList.add("fa-eye-slash")
  } else {
    input.type = "password"
    toggle.classList.remove("fa-eye-slash")
    toggle.classList.add("fa-eye")
  }
}

function fillDemoCredentials(type) {
  const emailInput = document.getElementById("email")
  const passwordInput = document.getElementById("password")

  if (!emailInput || !passwordInput) return

  if (type === "admin") {
    emailInput.value = "admin@bookhaven.com"
    passwordInput.value = "admin123"
  } else {
    emailInput.value = "john.doe@example.com"
    passwordInput.value = "password123"
  }

  // Trigger input events
  emailInput.dispatchEvent(new Event("input"))
  passwordInput.dispatchEvent(new Event("input"))

  // Add filled class
  emailInput.parentElement.classList.add("filled")
  passwordInput.parentElement.classList.add("filled")
}
