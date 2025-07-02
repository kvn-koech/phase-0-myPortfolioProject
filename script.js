// Project details visibility
document.querySelectorAll('.details-btn').forEach(button => {
  button.addEventListener('click', () => {
      const details = button.nextElementSibling;
      details.classList.toggle('hidden');
      button.textContent = details.classList.contains('hidden') ? 'Show Details': 'Hide Details';
  });
});

// Form submission handler
document.getElementById('contact-form').addEventListener('submit', (e) => {
  e.preventDefault();
  
  // Get form values
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const message = document.getElementById('message').value;
  
  // Interact with the server
  console.log('Form submitted:', { name, email, message });
  
  // Show a confirmation to the user
  alert('Thank you for your message! I will get back to you soon!');
  
  // Reset the form
  e.target.reset();
});

// Change header color on mouseover
const header = document.querySelector('header');
header.addEventListener('mouseover', () => {
  header.style.backgroundColor = '#4e6575';
});

header.addEventListener('mouseout', () => {
  header.style.backgroundColor = '#35424a';
});
