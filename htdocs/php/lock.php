<?php

require_once("sharedHandlers.php");
require_once 'auth.php';
require_once 'config.php';

// ?tripos=ID&time=secs
// Lock the supplied tripos for the speicified time in seconds.
// Slight race here, but this is advisory, anyway.

$filename = $sysdir."data/lock_".$_REQUEST['tripos'];

// Check for existing lock
if(file_exists($filename)) {
	$data = file_get_contents($filename);
	$m = explode(':',$data);
	if(time()<$m[1] && $m[0]!=current_user() && $_REQUEST['steal']!='true') {
		// Reject, lock exists
		echo json_encode(Array('success' => false, 'user' => $m[0]));
		return;
	}
}

// Expiry
$time = time() + $_REQUEST['time'];
file_put_contents($filename,current_user().":".$time);
echo json_encode(Array('success' => true));
