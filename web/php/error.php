<?php

/* Receives errors from the client and passes them onto the python error receiver. key-value pairs are sent literally. Extra parameters "receiver-time", which
 * is a UNIX timestamp and receive-session, receive-user which are session and session user (where available) are added, and other keys of the form "receiver-*" 
 * are reserved for future use. Unsafe characters are stripped.
 */

// XXX REQUEST to POST
 
require_once 'config.php';
require_once("sharedHandlers.php");
require_once 'auth.php';

start_session_if_not_started();

$out = Array();

$receiver = Array(
	'receiver-time' => time(),
	'receiver-session' => session_id(),
	'receiver-user' => current_user(),
	'receiver-real-user' => current_user(True)
);

$time = time();
$str = "$pypath ${sysdir}python/error/error.py ";
foreach($_POST as $k => $v) {
	$str .= escapeshellarg($k) . " " . escapeshellarg($v). " ";
}
foreach($receiver as $k => $v) {
	$str .= escapeshellarg($k) . " " . escapeshellarg($v). " ";
}

$proc=proc_open(escapeshellcmd($str), array(0=>array('pipe', 'r'), 1=>array('pipe', 'w'), 2=>array('pipe', 'w')), $pipes); 
fwrite($pipes[0], "");fclose($pipes[0]); 
$stdout=stream_get_contents($pipes[1]);fclose($pipes[1]); 
$stderr=stream_get_contents($pipes[2]);fclose($pipes[2]); 

header("Content-Type: text/json");
echo "{}"; // For future use, maybe.
