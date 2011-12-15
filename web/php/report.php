<?php

require_once 'config.php';

$collate = preg_replace('/[^A-Za-z0-9_]/','',$_REQUEST['collate']);

if(substr($collate,0,strlen('collate_')) == 'collate_') {
	$collate = substr($collate,strlen('collate_'));
}
if($collate == 'standard' || !$collate) {
	$collate = '';
} else {
	$collate = "_$collate";
}

foreach($_REQUEST['id'] as $id) {
	$id = preg_replace('/[^A-Za-z0-9]/','',$id);

	readfile("$sysdir/data/report${collate}_$id.html");
}

