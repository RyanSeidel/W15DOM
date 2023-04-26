// For the main page

// h1.addEventListener('click', function(){
//   h1.textContent = myName;
//   h1.style.backgroundColor = "red";
//   h1.style.padding = "5rem";
// });

// make mobile navigation work
const headerEl = document.querySelector(".header");

btnNavEl.addEventListener("click", function() {
  headerEl.classList.toggle("nav-open");
});

///////////////////////////////////////////////////////////
// Smooth scrolling animation

const allLinks = document.querySelectorAll('a:link');

allLinks.forEach(function(link) {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    const href = link.getAttribute("href");

    // Scroll back to top
    if(href == "#") window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

    // Scroll to other links
    if(href !== "#" && href.startsWith('#'))
    {
      const selectionEl = document.querySelector(href);
      selectionEl.scrollIntoView({ behavior: "smooth" });
    }

    // Close mobile navigation
    if(link.classList.contains('main-nav-link'))
    headerEl.classList.toggle("nav-open");
  });
});

///////////////////////////////////////////////////////////
// Sticky navigation

const sectionHeroEl = document.querySelector(".section-hero");

const obs = new IntersectionObserver(
  function (entries) {
    const ent = entries[0];
    console.log(ent);

    if (ent.isIntersecting === false) {
      document.body.classList.add("sticky");
    }

    if (ent.isIntersecting === true) {
      document.body.classList.remove("sticky");
    }
  },
  {
    // In the viewport
    root: null,
    threshold: 0,
    rootMargin: "-80px",
  }
);
obs.observe(sectionHeroEl);

///////////////////////////////////////////////////////////
// Fixing flexbox gap property missing in some Safari versions
function checkFlexGap() {
  var flex = document.createElement("div");
  flex.style.display = "flex";
  flex.style.flexDirection = "column";
  flex.style.rowGap = "1px";

  flex.appendChild(document.createElement("div"));
  flex.appendChild(document.createElement("div"));

  document.body.appendChild(flex);
  var isSupported = flex.scrollHeight === 1;
  flex.parentNode.removeChild(flex);
  console.log(isSupported);

  if (!isSupported) document.body.classList.add("no-flexbox-gap");
}
checkFlexGap();


///////////////////////////////////////////////////////////
// Display All Button
    
    var toggleGamesBtn = document.querySelector('#toggle-games-btn');
    var gameList = document.querySelector('.game-list');
    
    toggleGamesBtn.addEventListener('click', function() {
      event.preventDefault();
      if (gameList.style.display === 'none') {
        gameList.style.display = 'block';
        toggleGamesBtn.innerHTML = 'Hide My Games';
        toggleGamesBtn.dataset.showGames = 'true';
      } else {
        gameList.style.display = 'none';
        toggleGamesBtn.innerHTML = 'Show My Games';
        toggleGamesBtn.dataset.showGames = 'false';
      }
    });
    
    // Add this block to update the game list display when the page is loaded or reloaded
    if (toggleGamesBtn.dataset.showGames === 'true') {
      gameList.style.display = 'block';
      toggleGamesBtn.innerHTML = 'Hide My Games';
    } else {
      gameList.style.display = 'none';
      toggleGamesBtn.innerHTML = 'Show My Games';
    }

    
///////////////////////////////////////////////////////////
// Register Login Button
$(document).ready(function () {
  $("#signup-form").on("submit", function (event) {
      event.preventDefault();

      const email = $("#email").val();
      const name = $("#username").val();
      const password = $("#password").val();

      $.ajax({
        url: '/',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            email: email,
            name: name,
            password: password
        }),
        success: function (response) {
            if (response.message === 'success') {
                window.location.href = '/login';
            } else {
                alert(response.value);
            }
        },
        error: function (response) {
            alert('An error occurred. Please try again.');
        }
    });
    
  });
});
















