<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>informatique @ europnet.org</title>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" type="text/css" media="all" href="includes/style.css" />
    <script type="text/javascript" src="http://misc.crashdump.fr/irc/includes/jquery.js"></script>
    <script type="application/javascript">
	// Reloader
	var reloadTimer = null;
	var reloadTime = 3; // seconds
	window.onload = function() // au chargement de la page..
	{
		xmlHttpRequest();
	    setReloadTime(reloadTime); 
	}
	function setReloadTime(secs)  // Reload regulier
	{
	    if (arguments.length == 1) {
	        if (reloadTimer) clearTimeout(reloadTimer);
	        reloadTimer = setTimeout("setReloadTime()", Math.ceil(parseFloat(secs) * 1000));
	    }
	    else {
			xmlHttpRequest();
	    }
	}
	function xmlHttpRequest() // Recuperation du log
	{	
		titleStatus("loading"); // Affichage du statut
		$(document).ready(function(){
			$.ajax({
				type: "GET",
				url: "./includes/xmlParse.inc.php?input=informatique.xml",
				dataType: "xml",
				success: function(xml) {
					$('#page-wrap').empty();
					$(xml).find('message').each(function(){
						var timestamp = $(this).find('timestamp').text();
						var username = $(this).find('username').text();
						var type = $(this).find('type').text();
						var message = $(this).find('text').text();
						$('<div class="items"></div>').html('[' + timestamp + '] ' + username + '\> ' + message ).appendTo('#page-wrap');
					});
					titleStatus("done"); // changement du statut
					setReloadTime(reloadTime); // On specifie a nouveau le prochain rechargement de la page
					scrollDown(); // scroll down
				}
			});
		});
	}
	function scrollDown() // Recuperation du log
	{	
		$('#page-wrap').animate({ scrollTop:$('#page-wrap')[0].scrollHeight, duration:'slow', easing:'bounceout'});
	}
	function titleStatus(status) // en fonction de ce qui se fait.. on ajuste le titre
	{
		$('#title').empty();
		if (status == "loading") $('<h1></h1>').html('Reading XML log... please wait.').appendTo('#title');
		else $('<h1></h1>').html('live feed: #informatique @ irc.europnet.org').appendTo('#title');
	}
    </script>
</head>

<body>
	<div id="title"><h1>title</h1></div>
	
	<div id="page-wrap"></div>	
</body>

</html>
