<?php

// curl 'http://localhost/timetables/php/altupload.php/<id>?token=xyz' --data-binary @-

require_once("sharedHandlers.php");
require_once 'auth.php';
require_once 'config.php';


$hmac = $_REQUEST['token'];
$user = test_hmac($hmac);

$id = preg_replace('/[^A-Za-z0-9]/','',$_SERVER['PATH_INFO']);

$tripos = substr($id,0,14);

if(!can_edit($user,$tripos)) {
    echo 'Permission denied';
} else {
	$python = new myPythonHandler($sysdir);
	$errors = new myErrorHandling();
		
	$data = file_get_contents("php://input");
	
	file_put_contents("$sysdir/data/alt_$id.alt",$data);
	$pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l $logfile -s -a ". escapeshellarg($id), $errors);
	if($errors->hasError()) {
	    $pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l $logfile -d ". escapeshellarg($id), $errors);
	}
	echo $errors->showFriendlyErrors();
}