var el=document.getElementById("remarks");
function handler1() {
    el.style.display="block";
}

function handler2() {
    el.style.display="none";
}

document.getElementById("option1").addEventListener("click", handler2)
document.getElementById("option2").addEventListener("click", handler1);