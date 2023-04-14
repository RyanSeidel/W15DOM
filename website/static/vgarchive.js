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
  
  function deleteGame(game_id) {
    // Delete the game from the server
    $.ajax({
      url: "/delete_game/" + game_id,
      type: "DELETE",
      success: function (response) {
        if (response.success) {
          // Remove the deleted game from the HTML table
          $("#game-table tr[data-id='" + game_id + "']").remove();
        } else {
          console.log("Error deleting game");
        }
      },
      error: function (xhr, status, error) {
        console.log(xhr.responseText);
      }
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
              .attr("data-completed", game.completed)
              .attr("data-recommend", game.recommend)
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
      title = callback ? "Confirm" : "Error";
      var box = $("<div>").attr("title", title).addClass("dialog-box");
      $("<p>").text(message).appendTo(box).addClass("dialog-text");
      box.dialog({
        modal: true,
        buttons: callback ? {
          "Yes": function() {
            $(this).dialog("close");
            callback("yes");
          },
          "No": function() {
            $(this).dialog("close");
            callback("no");
          },
        } : {
          "OK": function() {
            $(this).dialog("close");
          }
        }
      });
    }
      
    $(document).on("click", ".edit", function () {
      var game_id = $(this).attr("data-id");
      var completed = $(this).attr("data-completed");
      var recommend = $(this).attr("data-recommend");
    
      showDialogBox("Is the game completed?", function(response1) {
        if (response1 === "yes" || response1 === "no") {
          showDialogBox("Would you recommend this game?", function(response2) {
            if (response2 === "yes" || response2 === "no") {
              updateGame(game_id, null, null, null, response1 === "yes", response2 === "yes");
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
    
          if (game.pltoLowerCase() === "steam") {
            showDialogBox("You cannot delete a Steam game.", null);
          } else {
            showDialogBox("Are you sure you want to delete this game?", function(response) {
              if (response === "yes") {
                deleteGame(game_id);
              }
            });
          }
        },
        error: function (xhr, status, error) {
          console.log(xhr.responseText);
        }
      });
    });
    
     
      
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
            name: $("#name-input").val(),
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
              window.console.log("Error adding game");
            }
          },
          error: function(xhr, status, error) {
            window.console.log("Error adding game");
          }
        });
        
        
        
      });
    });
      
              