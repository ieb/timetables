<?php

require_once("../sharedHandlers.php");
require_once '../config.php';

if(substr($sysdir,0,1) != '/') {
	$sysdir = "../$sysdir";
}

$top = json_decode(file_get_contents($sysdir."data/top.json"),TRUE);
$root = get_config('base');

?><html>
  <head>
  	<title>Lecture Listings</title>
  </head>
  <body>
  	<h1>University of Cambridge Lecture Listings</h1>
	<p>
		This version of the site uses only very basic web technology. It is designed for people using very old or unusual web browsers. To see the full version, go to the high qulaity site.
	</p>
	<a href='<?php echo "${root}list.html" ?>'>go to high-quality site</a>

<?php

function squash($text) {
	$text = preg_replace('/[^A-Za-z0-9]/','',$text);
	return $text;
}

foreach($top['years'] as $year) {
	echo "<h2>".$year['name']."</h2>";
	echo "<p style='font-size: 90%'><b>Jump to:</b> ";
	foreach($year['triposes'] as $tripos) {
		echo "<a  style='margin: 0 8px;' href='#".squash($tripos['name'])."'>".$tripos['name']."</a> ";
	}
	echo "</p>";
	foreach($year['triposes'] as $tripos) {
		echo "<a name='".squash($tripos['name'])."'></a>";
		echo "<h3>".$tripos['name']."</h3>";
		foreach($tripos['parts'] as $part) {
			echo "<h4>".$part['name']."</h4>";
			$cal = json_decode(file_get_contents($sysdir."data/cal_".$part['id'].".json"),TRUE);
			echo "<ul>";
			$courses = $cal['courses'];
			ksort($courses);
			foreach($courses as $cid => $course) {
				echo "<li>";
				if(array_key_exists('staticurls',$course)) {
					foreach($course['staticurls'] as $url) {
						echo "<a href='".$url."'>".$course['name']."</a> ";
					}
				} else {
					$report = "${root}report.html#courseids%5B%5D=".$cid."&tripospartid=".$part['id']."&year=".$year['name'];
					$timetable = "${root}view.html#course=".$cid;
					$basic = "report.php?id=".$cid;
					echo $course['name'].": <a href='".$basic."'>basic webpage</a> (high-quality version: <a href='".$report."'>report</a> <a href='".$timetable."'>timetable</a>)";
				}
				echo "</li>";
			}
			echo "</ul>";
		}
	}
}

?>
	<p><a href='<?php echo "${root}list.html" ?>'>go to high-quality site</a></p>
  </body>
</html>