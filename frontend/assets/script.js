// =======================
// Highlight active nav link
// =======================
const navLinks = document.querySelectorAll('nav a');
navLinks.forEach(link => {
  if(link.href === window.location.href){
    link.classList.add('active');
  }
});

// =======================
// Company Search Function
// =======================
const companies = [];

function searchCompany() {
  const input = document.getElementById('demo-input').value.trim();
  const resultBox = document.getElementById('result');

  if (!input) {
    resultBox.textContent = 'Please enter a company name.';
    return;
  }

  const found = companies.find(c => c.toLowerCase() === input.toLowerCase());

  if (found) {
    resultBox.textContent = `Found: ${found}`;
  } else {
    resultBox.textContent = `${input} not found in our database.`;
  }
}

// =======================
// Review Submission & Star Rating
// =======================
let selectedRating = 0;
const stars = document.querySelectorAll('.star');

stars.forEach(star => {
  star.addEventListener('mouseover', () => highlightStars(star.dataset.value));
  star.addEventListener('mouseout', () => highlightStars(selectedRating));
  star.addEventListener('click', () => {
    selectedRating = star.dataset.value;
    highlightStars(selectedRating);
  });
});

function highlightStars(rating) {
  stars.forEach(star => {
    star.classList.remove('selected', 'yellow');
    if(star.dataset.value <= rating){
      if(rating <= 3){
        star.classList.add('selected'); // red for 1-3
      } else {
        star.classList.add('yellow');   // yellow for 4-5
      }
    }
  });
}

function submitReview() {
  const name = document.getElementById('company-name').value.trim();
  const title = document.getElementById('review-title').value.trim();
  const text = document.getElementById('review-text').value.trim();
  const resultBox = document.getElementById('review-result');

  if (!name || !title || !text || selectedRating == 0) {
    resultBox.textContent = 'Please fill in all fields and select a rating.';
    return;
  }

  const review = `Company: ${name}\nTitle: ${title}\nRating: ${selectedRating}/5\nReview: ${text}\n\n`;
  resultBox.textContent = 'Review submitted successfully!\n\n' + review + resultBox.textContent;

  // Reset form
  document.getElementById('company-name').value = '';
  document.getElementById('review-title').value = '';
  document.getElementById('review-text').value = '';
  selectedRating = 0;
  highlightStars(0);
}
