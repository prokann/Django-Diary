//home


//all notes
var first_click = true;

function readAll(iterate) {
    let full = 'full_text'.concat(iterate);
    let short = "short_text".concat(iterate);
    if (first_click) {
        document.getElementById(full).style.display = ""
        document.getElementById(short).style.display = "none"
        first_click = false;}
    else {
        document.getElementById(full).style.display = "none"
        document.getElementById(short).style.display = ""
        first_click = true;
        }
}