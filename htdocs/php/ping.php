<?php

require_once("sharedHandlers.php");
require_once 'config.php';

// Keeps session alive

$messages = Array();
if ($handle = opendir($sysdir."/data")) {
    /* This is the correct way to loop over the directory. */
    while (false !== ($file = readdir($handle))) {
		if(substr($file,0,4)=='msg_') {
			$data = file_get_contents($sysdir."data/".$file);
			$messages[$file] = $data;
		}
    }
    closedir($handle);
}
$out = Array();
if(count($messages)) {
	$out['messages'] = $messages;
}
$ping = get_config('ping');
if($ping) {
	$out['ping'] = $ping;
}
$reload = get_config('reload');
if($reload) {
	$out['reload'] = $reload;
}

echo json_encode($out);
