$(document).ready(function () {
  // Function to update a game record on the server
  function updateGame(game_id, completed_response, recommend_response) {
    // Fetch the game from the server
    $.ajax({
      url: "/get_game/" + game_id,
      type: "GET",
      success: function(response) {
        var game = response.game;
  
        // Update the game's completed status in the database
        if (completed_response !== undefined) {
          // Update the value of game.completed
          game.completed = completed_response;
  
          // Send a POST request to update the completed status in the database
          $.ajax({
            url: "/update_game/" + game_id,
            type: "POST",
            data: {
              name: game.name,
              completed: game.completed ? "true" : "false"
            },
            success: function(response) {
              console.log("Completed status update response:", response);
  
              // Update the completed status in the table
              if (response.success) {
                var row = $("button[data-id='" + game_id + "']").closest("tr");
                row.find(".completed").text(completed_response ? "Yes" : "No");
              } else {
                console.log("Error updating completed status:", response.error);
                alert("Error updating completed status: " + response.error);
              }
            },
            error: function(xhr, status, error) {
              console.log("Error updating completed status:", error);
              alert("Error updating completed status: " + error);
            }
          });
        }
  
        // Update the game's recommend status in the database
        if (recommend_response !== undefined) {
          // Update the value of game.recommend
          game.recommend = recommend_response;
  
          // Send a POST request to update the recommend status in the database
          $.ajax({
            url: "/update_game/" + game_id,
            type: "POST",
            data: {
              recommend: recommend_response === null ? null : recommend_response
            },
            success: function(response) {
              console.log("Recommend update response:", response);
  
              // Update the recommend status in the table
              if (response.success) {
                var row = $("button[data-id='" + game_id + "']").closest("tr");
                row.find(".recommend").text(recommend_response === null ? "Unrated" : recommend_response ? "Like" : "Dislike");
              } else {
                console.log("Error updating recommend:", response.error);
                alert("Error updating recommend: " + response.error);
              }
            },
            error: function(xhr, status, error) {
              console.log("Error updating recommend:", error);
              alert("Error updating recommend: " + error);
            }
          });
        }
      },
      error: function(xhr, status, error) {
        console.log("Error fetching game:", error);
        alert("Error fetching game: " + error);
      }
    });

    console.log(completed_response, recommend_response)
  }
  
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
            .addClass("recommended") // Add the "recommended" class here
            .text(game.recommend == null ? "Unrated" : (game.recommend ? "Like" : "Dislike"))
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
            .attr("data-platform", game.console)
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
  console.log("Edit button clicked");

  var game_id = $(this).attr("data-id");
  var completed = ($(this).closest("tr").find(".completed").text().trim().toLowerCase() === "yes");

  var completed_msg = "Have you completed the game? (Yes/No)";
  var recommend_msg = "Do you recommend this game? (Yes/No)";

  showDialogBox(completed_msg, function (response1) {
    console.log("response1:", response1);

    var completed_response = response1.toLowerCase() === "yes";

    showDialogBox(recommend_msg, function (response2) {
      console.log("response2:", response2);

      var recommend_response;
      if (response2.toLowerCase() === "yes") {
        recommend_response = true;
      } else if (response2.toLowerCase() === "no") {
        recommend_response = false;
      }

      updateGame(game_id, completed_response, recommend_response);
      updateTable();
    });
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
    var recommend = $("#recommend-input").is(":checked");

  
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
        recommend: recommend, // Update the property name to "recommend"
      }),
      success: function (response) {
        if (response.success) {
          // Clear the form and update the table
          $("#name-input").val("");
          $("#genre-input").val("");
          $("#console-input").val("");
          $("#completed-input").prop("checked", false);
          $("#recommend-input").prop("checked", false);
    
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







