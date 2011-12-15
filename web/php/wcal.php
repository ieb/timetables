<?php

require_once 'config.php';

// XXX should use names not fixed
$id = preg_replace('/[^A-Za-z0-9]/','',$_REQUEST['course']);
header("Content-Type: text/json");
//readfile("$sysdir/data/student_$id.$suffix");

$req_start = $_REQUEST['start'];
$req_end = $_REQUEST['end'];

date_default_timezone_set('UTC');

$one_day = 60*60*24; // Add an extra day, just in case we'd be tripped up by timezones, etc.

$data = json_decode(file_get_contents("$sysdir/data/student_$id.json"),TRUE);
$entries = $data['feed']['entry'];
$out = Array();
foreach($entries as $entry) {
	$start = strtotime($entry['gd$when'][0]['startTime']);
	$end = strtotime($entry['gd$when'][0]['endTime']);
	if($start-$one_day > $req_end || $end+$one_day < $req_start)
		continue;
	$out[] = $entry;
}
$data['feed']['entry'] = $out;
echo json_encode($data);
