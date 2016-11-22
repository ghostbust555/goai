var board = document.getElementById('board');
var pieceSize = 30;
var boardsize = 9;

var boardState = initalize();

function initalize(){
    var gs = []
    for (var i =0; i < boardsize; i++){
        gs.push([])
        for (var j =0; j < boardsize; j++){
            gs[i].push('-')
        }
    }
    return gs
}

function drawBoardState(){
    for (var i = 0; i < boardsize; i++){
        for (var j = 0; j < boardsize; j++){
            if(boardState[i][j] !== '-'){
                y = j * 54 + 25
                x = i * 54 + 25

                var piece = document.createElement("img");
                piece.style.position = "absolute"

                piece.src = boardState[i][j] == "x" ? "http://bsccongress.com/im3/glossy-black-circle-button-clip-art.png" : "http://cdn.shopify.com/s/files/1/0185/5092/products/symbols-0200_large.png?v=1369543715";
                piece.height = pieceSize;
                piece.width = pieceSize;
                piece.style.left = x;
                piece.style.top = y;
                document.getElementById('main').appendChild(piece);
            }
        }
    }
}

function placeStone(x, y, xoro){
    boardState[x][y] = xoro
    $.get("/move", {"x": x, "y":y})
       .done(function(string) {
        $("#the-string").show();
        $("#the-string input").val(string);
      });
    drawBoardState()
}

board.onclick = function (evt) {
    var x = evt.clientX - pieceSize/2;
    var y = evt.clientY - pieceSize/2;

    y = Math.round((y-23)/54)
    x = Math.round((x-23)/54)

    placeStone(x, y, "x")
};