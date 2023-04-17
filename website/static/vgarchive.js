$(document).ready(function () {
  // Function to update a game record on the server
  // Function to update a game record on the server
function updateGame(game_id, completed_response, rating_response) {
  var completed = (typeof completed_response === "string" && completed_response.toLowerCase() === "yes") ? true : false;
  var rating = (rating_response.toLowerCase() === "like") ? "like" : (rating_response.toLowerCase() === "dislike") ? "dislike" : "unrated";

  $.ajax({
    url: "/update_game/" + game_id,
    type: "POST",
    data: { rating: rating },
    success: function (response) {
      // Update the rating in the table
      if (response.success) {
        var newRating = (rating === "like") ? "Like" : (rating === "dislike") ? "Dislike" : "Unrated";
        var row = $("button[data-id='" + game_id + "']").closest("tr");
        row.find(".rating").text(newRating);
      }
    },
  });
  // Update the game's completed status in the database
  $.ajax({
    url: "/update_game_completed/" + game_id,
    type: "POST",
    data: { completed: completed },
    success: function (response) {
      // Update the completed status in the table
      if (response.success) {
        var row = $("button[data-id='" + game_id + "']").closest("tr");
        row.find(".completed").text(completed ? "Yes" : "No");
      }
    },
  });
}


  
  // Function to update the table with the current game collection
  function updateTable() {
    // Fetch games from the server
    $.ajax({
      url: "/get_games",
      type: "GET",
      success: function (response) {
        var gameCollection = response.games;
  
        // Create an empty table
        var table = $("<table>").attr("id", "game-table");
  
        // Create the table header
        var header = $("<thead>").appendTo(table);
        var headerRow = $("<tr>").appendTo(header);
        $("<th>").text("Name").appendTo(headerRow);
        $("<th>").text("Genre").appendTo(headerRow);
        $("<th>").text("Console").appendTo(headerRow);
        $("<th>").text("Completed").appendTo(headerRow);
        $("<th>").text("Recommended").appendTo(headerRow);
        $("<th>").text("Rating").appendTo(headerRow);
        $("<th>").text("Action").appendTo(headerRow);
  
        // Create the table body
        var body = $("<tbody>").appendTo(table);
        for (var i = 0; i < gameCollection.length; i++) {
          var game = gameCollection[i];
          var row = $("<tr>").appendTo(body);
          $("<td>").text(game.name).appendTo(row);
          $("<td>").text(game.genre).appendTo(row);
          $("<td>").text(game.console).appendTo(row);
          $("<td>")
          .addClass("completed")
            .text(game.completed ? "Yes" : "No")
            .appendTo(row);
          $("<td>")
            .addClass("rating") //Add the "rating" class here
            .text(game.rating)
            .appendTo(row);
  
          // Create the Edit and Delete buttons
          var buttonGroup = $("<td>").appendTo(row);
          $("<button>")
          .addClass("edit")
          .attr("data-id", game.id)
          .text("Edit")
          .appendTo(buttonGroup);
  
          $("<button>")
            .addClass("delete")
            .attr("data-id", game.id)
            .attr("data-platform", game.console) // Add this line
            .text("Delete")
            .appendTo(buttonGroup);
        }
  
        // Replace the old table with the new one
        $("#game-table").replaceWith(table);
      },
    });
  }
  
  function showDialogBox(message, callback, title) {
    title = title ? title : (callback ? "Confirm" : "Error");
    var box = $("<div>").attr("title", title).addClass("dialog-box");
    $("<p>").text(message).appendTo(box).addClass("dialog-text");
    if (callback) {
        box.dialog({
            modal: true,
            buttons: {
                Yes: function () {
                    $(this).dialog("close");
                    callback("yes");
                },
                No: function () {
                    $(this).dialog("close");
                    callback("no");
                },
                Cancel: function () {
                    $(this).dialog("close");
                    callback("cancel");
                },
            },
        });
    } else {
        box.dialog({
            modal: true,
            buttons: {
                OK: function () {
                    $(this).dialog("close");
                },
            },
        });
    }
}


$(document).on("click", ".edit", function () {
  var game_id = $(this).attr("data-id");
  var rating = $(this).closest("tr").find(".rating").text().trim();
  var completed = $(this).closest("tr").find(".completed").text().trim() === "Yes";

  var completed_msg = completed ? "Is the game still completed? (Yes/No)" : "Have you completed the game? (Yes/No)";
  var rating_msg = "Did you like this game? (Like/Dislike/Unrated)";

  showDialogBox(completed_msg, function (response1) {
    if (response1 === "yes" || response1 === "no") {
      var completed_response = response1;
      showDialogBox(rating_msg, function (response2) {
        if (response2 === "like" || response2 === "dislike" || response2 === "unrated") {
          updateGame(game_id, completed_response, response2);
        }
      });
    }
  });   
});

  
  $(document).on("click", ".delete", function () {
    var game_id = $(this).attr("data-id");

    $.ajax({
      url: "/get_game/" + game_id,
      type: "GET",
      success: function (response) {
        var game = response.game;
        console.log(game); // Add this line to inspect the game object

        if (game.platform && game.platform.toLowerCase() === "steam") {
          showDialogBox("You cannot delete a Steam game.", null);
        } else {
          showDialogBox(
            "Are you sure you want to delete this game?",
            function (response) {
              if (response === "yes") {
                deleteGame(game_id);
              }
            }
          );
        }
      },
      error: function (xhr, status, error) {
        console.log(xhr.responseText);
      },
    });
  });

  // Function to handle the form submission for adding a new game
  $("#game-form").submit(function (event) {
    event.preventDefault();
  
    var name = $("#name-input").val();
    var genre = $("#genre-input").val();
    var gameConsole = $("#console-input").val(); // Rename the variable
    var completed = $("#completed-input").is(":checked");
    var rating = $("#rating-input").val(); // Use rating instead of recommend
  
    // Ensure that all required fields are filled out
    if (name === "" || genre === "" || gameConsole === "") {
      alert("Please fill out all required fields.");
      return;
    }

    $.ajax({
      url: "/add_game",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        name: name,
        genre: genre,
        console: gameConsole,
        completed: completed,
        rating: rating
      }),
      success: function (response) {
        if (response.success) {
          // Clear the form and update the table
          $("#name-input").val("");
          $("#genre-input").val("");
          $("#console-input").val("");
          $("#completed-input").prop("checked", false);
    
          updateTable();
          alert("Game added successfully.");
        } else {
          console.log("Error adding game: " + response.error);
          alert("Error adding game: " + response.error);
        }
      },
      error: function (xhr, status, error) {
        console.log("Error adding game: " + error);
        alert("Error adding game: " + error);
      },
    });
    
    
  });
});







