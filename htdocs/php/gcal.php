<?php

require_once 'config.php';
require_once("sharedHandlers.php");

// XXX should use names not fixed
$id = preg_replace('/[^A-Za-z0-9,]/','',$_REQUEST['course']);

if(array_key_exists('type',$_REQUEST) && $_REQUEST['type'] == 'ical') {
	$suffix = 'ical';
	$mime = 'text/calendar';
	$flag = '';
} else {
	$suffix = 'json';
	$mime = 'text/json';
	$flag = '-a';
}

$proc=proc_open("$pypath ".$sysdir."python/indium/indium.py -l $logfile -F $flag $id", array(0=>array('pipe', 'r'), 1=>array('pipe', 'w'), 2=>array('pipe', 'w')), $pipes); 
fwrite($pipes[0], "");fclose($pipes[0]); 
$stdout=stream_get_contents($pipes[1]);fclose($pipes[1]); 
$stderr=stream_get_contents($pipes[2]);fclose($pipes[2]); 
# XXX error handling
# XXX cache

header("Content-Type: $mime");
echo $stdout;
