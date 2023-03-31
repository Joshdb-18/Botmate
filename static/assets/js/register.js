const forms = document.querySelector(".forms"),
	pwShowHide = document.querySelectorAll(".eye-icon"),
	links = document.querySelectorAll(".link");

pwShowHide.forEach(eyeIcon => {
    eyeIcon.addEventListener("click", () => {
        let pwFields = eyeIcon.parentElement.parentElement.querySelectorAll(".password");

        pwFields.forEach(password => {
            if(password.type === "password"){
                password.type = "text";
                eyeIcon.classList.replace("bx-hide", "bx-show");
                return;
            }
            password.type = "password";
            eyeIcon.classList.replace("bx-show", "bx-hide");
        })

    })
})
const passwordInput = document.getElementById('password');
const passwordRequirements = document.querySelectorAll('.password-requirements li');

passwordInput.addEventListener('input', function() {
  const password = passwordInput.value;
  
  if (password === '') {
    hidePasswordRequirements();
  } else {
    showPasswordRequirements();
    
    let requirementsMet = true;
    requirementsMet &= password.length >= 8;
    requirementsMet &= /[a-z]/.test(password);
    requirementsMet &= /[A-Z]/.test(password);
    requirementsMet &= /\d/.test(password);
    requirementsMet &= /\W/.test(password);
    
    passwordRequirements.forEach(function(requirement) {
      const requirementClass = requirement.classList[0];
      if (password.length === 0) {
        requirement.classList.remove('valid');
        requirement.classList.remove('invalid');
      } else if (password.length >= 8 && requirementClass === 'length') {
        requirement.classList.add('valid');
        requirement.classList.remove('invalid');
      } else if (/[a-z]/.test(password) && requirementClass === 'lowercase') {
        requirement.classList.add('valid');
        requirement.classList.remove('invalid');
      } else if (/[A-Z]/.test(password) && requirementClass === 'uppercase') {
        requirement.classList.add('valid');
        requirement.classList.remove('invalid');
      } else if (/\d/.test(password) && requirementClass === 'number') {
        requirement.classList.add('valid');
        requirement.classList.remove('invalid');
      } else if (/\W/.test(password) && requirementClass === 'special') {
        requirement.classList.add('valid');
        requirement.classList.remove('invalid');
      } else {
        requirement.classList.remove('valid');
        requirement.classList.add('invalid');
      }
    });
    
    if (requirementsMet) {
      hidePasswordRequirements();
    }
  }
});

function showPasswordRequirements() {
  const container = document.querySelector('.password-requirements-container');
  container.style.display = 'block';
}

function hidePasswordRequirements() {
  const container = document.querySelector('.password-requirements-container');
  container.style.display = 'none';
}

const confirmPasswordInput = document.getElementById('confirm-password');
const passwordMismatch = document.getElementById('password-mismatch');

confirmPasswordInput.addEventListener('input', function() {
  if (confirmPasswordInput.value !== passwordInput.value) {
    passwordMismatch.style.display = 'block';
  } else {
    passwordMismatch.style.display = 'none';
  }
});

