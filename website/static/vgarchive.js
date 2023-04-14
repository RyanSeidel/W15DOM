$(document).ready(function () {
  // Function to update a game record on the server
  function updateGame(game_id, name, genre, console, completed, recommend) {
    $.ajax({
      url: "/update_game/" + game_id,
      type: "PUT",
      contentType: "application/json",
      data: JSON.stringify({
        name: name,
        genre: genre,
        console: console,
        completed: completed,
        recommend: recommend,
      }),
      success: function (response) {
        if (response.success) {
          updateTable();
        } else {
          console.log("Error updating game");
        }
      },
    });
  }

  // Function to delete a game record from the server
  function deleteGame(game_id) {
    $.ajax({
      url: "/delete_game/" + game_id,
      type: "DELETE",
      success: function (response) {
        if (response.success) {
          updateTable();
        } else {
          console.log("Error deleting game");
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
          $("<th>").text("Action").appendTo(headerRow);
  
          // Create the table body
          var body = $("<tbody>").appendTo(table);
          for (var i = 0; i < gameCollection.length; i++) {
            var game = gameCollection[i];
            var row = $("<tr>").appendTo(body);
            $("<td>").text(game.name).appendTo(row);
            $("<td>").text(game.genre).appendTo(row);
            $("<td>").text(game.console).appendTo(row);
            $("<td>").text(game.completed ? "Yes" : "No").appendTo(row);
            $("<td>").text(game.recommend ? "Yes" : "No").appendTo(row);
  
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
              .text("Delete")
              .appendTo(buttonGroup);
          }
  
          // Replace the old table with the new one
          $("#game-table").replaceWith(table);
  
          // Attach click handlers to the edit and delete buttons
          $(".edit").click(function () {
            var game_id = $(this).attr("data-id");
            var name = prompt("Enter the new game name:");
            var genre = prompt("Enter the new game genre:");
            var console = prompt("Enter the new game console:");
            var completed = confirm("Is the game completed?");
            var recommend = confirm("Would you recommend this game?");

            if (name !== null && genre !== null && console !== null) {
              updateGame(game_id, name, genre, console, completed, recommend);
            }
            
            // Function to handle the form submission for adding a new game
            $("#game-form").submit(function (event) {
              event.preventDefault();
            
              var name = $("#name-input").val();
              var genre = $("#genre-input").val();
              var console = $("#console-input").val();
              var completed = $("#completed-input").is(":checked");
              var recommend = $("#recommend-input").is(":checked");
            
              // Ensure that all required fields are filled out
              if (name === "" || genre === "" || console === "") {
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
                  console: console,
                  completed: completed,
                  recommend: recommend,
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
                    console.log("Error adding game");
                  }
                },
              });
            });
            
  // Attach click handlers to the edit and delete buttons
  $(document).on("click", ".edit", function () {
    var game_id = $(this).attr("data-id");
    var name = prompt("Enter the new game name:");
    var genre = prompt("Enter the new game genre:");
    var console = prompt("Enter the new game console:");
    var completed = confirm("Is the game completed?");
    var recommend = confirm("Would you recommend this game?");

    if (name !== null && genre !== null && console !== null) {
      updateGame(game_id, name, genre, console, completed, recommend);
    }
  });
            
  $(document).on("click", ".delete", function () {
    var game_id = $(this).attr("data-id");
    var confirmation = confirm("Are you sure you want to delete this game?");

    if (confirmation) {
      deleteGame(game_id);
    }
  });
            


function deleteGame(game_id) {
  $.ajax({
    url: "/delete_game/" + game_id,
    type: "DELETE",
    success: function (response) {
      if (response.success) {
        updateTable();
      } else {
        console.log("Error deleting game");
      }
    },
  });
}

  // Function to handle the form submission for adding a new game
  $("#game-form").submit(function (event) {
    event.preventDefault();
    
    // ...
  });
});



            