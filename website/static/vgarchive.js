$(document).ready(function () {
  // Function to add a game to the collection
  function addGame(name, genre, console, completed, recommend) {
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
          updateTable();
        } else {
          console.log("Error adding game");
        }
      },
    });
  }

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
  
  // Function to remove a game from the collection
  function removeGame(game_id) {
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
    // Clear the current table contents
    $("#game-table tbody").empty();

    // Fetch games from the server
    $.ajax({
      url: "/get_games",
      type: "GET",
      success: function (response) {
        var gameCollection = response.games;
        // Loop through the game collection and add each game to the table
        for (var i = 0; i < gameCollection.length; i++) {
          var game = gameCollection[i];
          var row =
            "<tr>" +
            "<td>" +
            game.name +
            "</td>" +
            "<td>" +
            game.genre +
            "</td>" +
            "<td>" +
            game.console +
            "</td>" +
            "<td>" +
            (game.completed ? "Yes" : "No") +
            "</td>" +
            "<td>" +
            (game.recommend ? "Yes" : "No") +
            "</td>" +
            '<td><button class="edit" data-id="' +
            game.id +
            '">Edit</button> ' +
            '<button class="delete" data-id="' +
            game.id +
            '">Delete</button></td>' +
            "</tr>";
          $("#game-table tbody").append(row);
        }
      },
    });
  }

  // Add a submit handler for the game form
  $("#game-form").submit(function (event) {
    event.preventDefault();
    var name = $("#name").val();
    var genre = $("#genre").val();
    var console = $("#console").val();
    var completed = $("#completed").is(":checked");
    var recommend = $("#recommend").is(":checked");
    addGame(name, genre, console, completed, recommend);
    $("#name").val("");
    $("#genre").val("");
    $("#console").val("");
    $("#completed").prop("checked", false);
    $("#recommend").prop("checked", false);
  });

  // Add a click handler for the delete buttons
  $("#game-table").on("click", ".delete", function () {
    var game_id = $(this).data("id");
    removeGame(game_id);
  });

  // Add a click handler for the edit buttons
  $("#game-table").on("click", ".edit", function () {
    var game_id = $(this).data("id");
  
    // Fetch game data from the server
    $.ajax({
      url: "/get_game/" + game_id,
      type: "GET",
      success: function (response) {
        var game = response.game;
    
        // Populate the form with the fetched data
        $("#game-id").val(game.id); // Add this line
        $("#name").val(game.name);
        $("#genre").val(game.genre);
        $("#console").val(game.console);
        $("#completed").prop("checked", game.completed);
        $("#recommend").prop("checked", game.recommend);
  
        // Change the submit handler to call updateGame() instead of addGame()
        $("#game-form").off("submit").submit(function (event) {
          event.preventDefault();
          var name = $("#name").val();
          var genre = $("#genre").val();
          var console = $("#console").val();
          var completed = $("#completed").is(":checked");
          var recommend = $("#recommend").is(":checked");
          updateGame(game_id, name, genre, console, completed, recommend);
          $("#name").val("");
          $("#genre").val("");
          $("#console").val("");
          $("#completed").prop("checked", false);
          $("#recommend").prop("checked", false);
  
          // Reset the submit handler back to addGame()
          $("#game-form").off("submit").submit(addGameSubmitHandler);
        });
      },
    });
  });
  
  function addGameSubmitHandler(event) {
    event.preventDefault();
    var name = $("#name").val();
    var genre = $("#genre").val();
    var console = $("#console").val();
    var completed = $("#completed").is(":checked");
    var recommend = $("#recommend").is(":checked");
    addGame(name, genre, console, completed, recommend);
    $("#name").val("");
    $("#genre").val("");
    $("#console").val("");
    $("#completed").prop("checked", false);
    $("#recommend").prop("checked", false);
  }
  
  $("#game-form").submit(addGameSubmitHandler);
  
  updateTable();
});

