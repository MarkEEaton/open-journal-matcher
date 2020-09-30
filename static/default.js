document.getElementById("show").addEventListener("click", function() {
    document.getElementById("waiting").style.display = "";
    document.getElementById("results").style.display = "none";
    document.getElementById("docs").style.display = "none";
    window.location.hash = "jump";
    history.replaceState(null, null, ' ');
});      

document.getElementById("finger").addEventListener("click", function() {
    document.getElementById("docs").style.display = "";
    document.getElementById("results").style.display = "none";
    if (document.getElementById("waiting").style.display === "") {
        document.getElementById("docs").style.margin = 0;
    }
    window.location.hash = "jump";
    history.replaceState(null, null, " ");
});

document.getElementById("hideDocs").addEventListener("click", function() {
	document.getElementById("docs").style.display = "none";
    if (document.getElementById("waiting").style.display === "") {
		document.getElementById("results").style.display = "none";
    } else {
		document.getElementById("results").style.display = "";
	}
    document.getElementById("error").style.display = "none";
}); 
