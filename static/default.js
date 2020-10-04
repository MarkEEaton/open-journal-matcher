document.getElementById("show").addEventListener("click", function() {
    document.getElementById("waiting").style.display = "block";
    document.getElementById("results").style.display = "none";
    document.getElementById("docs").style.display = "none";
    window.location.hash = "jump";
    history.replaceState(null, null, ' ');
});      

document.getElementById("finger").addEventListener("click", function() {
    document.getElementById("docs").style.display = "block";
    document.getElementById("results").style.display = "none";
    if (document.getElementById("waiting").style.display === "block") {
        document.getElementById("docs").style.marginTop = "0px";
    }
    window.location.hash = "jump";
    history.replaceState(null, null, " ");
});

document.getElementById("hideDocs").addEventListener("click", function() {
	document.getElementById("docs").style.display = "none";
    if (document.getElementById("waiting").style.display === "block") {
		document.getElementById("results").style.display = "none";
    } else {
		document.getElementById("results").style.display = "block";
	}
	if (document.getElementById("error") !== null) {
    	document.getElementById("error").style.display = "none";
	}	
}); 
