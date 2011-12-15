<?php

require_once("../sharedHandlers.php");
require_once '../config.php';

if(substr($sysdir,0,1) != '/') {
	$sysdir = "../$sysdir";
}

$root = get_config('base');
$id = preg_replace('/[^A-Za-z0-9]/','',$_REQUEST['id']);

$report = file_get_contents($sysdir."data/report_$id.html");
$time = file_get_contents($sysdir."data/report_time_$id.html");


?><html>
	<head>
		<meta charset="utf-8" />
	  	<title>Lecture Listings</title>
		<style>
			table, tr, td, th {
			  padding: 8px;
			  border: 1px solid black;
			  border-collapse: collapse;
			}
		</style>
	</head>
	<body>
	<p>
		<p>
			This version of the site uses only very basic web technology. It is designed for people using very old or unusual web browsers. To see the full version, go to the high qulaity site.
		</p>
		<a href='<?php echo "${root}list.html" ?>'>go to high-quality site</a>
		<a href='list.php'>back to list</a>
	</p>
		
<?php

echo $report;
echo $time;
?>
	<p>
		<a href='list.php'>back to list</a><br/>
		<a href='<?php echo "${root}list.html" ?>'>go to high-quality site</a>
	</p>
	</body>
</html>
