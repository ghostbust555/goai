var board = document.getElementById('board');
var back = document.getElementById('back');
var next = document.getElementById('next');

var x_score_element = document.getElementById('x_score');
var o_score_element = document.getElementById('o_score');

var pieceSize = 30;
var boardsize = 9;

var boardState = initialize();
var waiting = false;

function initialize(){
    var gs = [];
    for (var i =0; i < boardsize; i++){
        gs.push([]);
        for (var j =0; j < boardsize; j++){
            gs[i].push('-')
        }
    }
    return gs
}

function drawBoardState(){
    $('.piece').remove();

    for (var i = 0; i < boardsize; i++){
        for (var j = 0; j < boardsize; j++){
            if(boardState[i][j] !== '-'){
                x = j * 54 + 25;
                y = i * 54 + 25;

                var piece = document.createElement("img");
                piece.className = "piece";
                piece.style.position = "absolute";

                piece.src = boardState[i][j] == "x" ? "http://bsccongress.com/im3/glossy-black-circle-button-clip-art.png" : "http://cdn.shopify.com/s/files/1/0185/5092/products/symbols-0200_large.png?v=1369543715";
                piece.height = pieceSize;
                piece.width = pieceSize;
                piece.style.left = x+2;
                piece.style.top = y+2;
                document.getElementById('main').appendChild(piece);
            }
        }
    }
}

function placeStone(x, y, xoro){
    if(!waiting && boardState[x][y] == "-") {
        boardState[x][y] = xoro;

        $.get("/move", {"x": x, "y": y}).done(updateBoard);

        waiting = true;

        drawBoardState()
    }
}

function updateBoard(jsonResult){
    waiting = false;
    res = JSON.parse(jsonResult);
    boardState = res.state;
    x_score_element.innerText = res.x_captures;
    o_score_element.innerText = res.o_captures;
    drawBoardState();
}

board.onclick = function (evt) {
    var x = evt.clientX - pieceSize/2;
    var y = evt.clientY - pieceSize/2;

    y = Math.round((y-23)/54);
    x = Math.round((x-23)/54);

    placeStone(y, x, "x")
};

back.onclick = function (evt) {
    waiting = true;
    $.get("/back").done(updateBoard);
};

next.onclick = function (evt) {
    waiting = true;
    $.get("/next").done(updateBoard);
};

reset.onclick = function (evt) {
    waiting = true;
    $.get("/reset").done(updateBoard);
};