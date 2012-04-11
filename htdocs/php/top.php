<?php

require_once("sharedHandlers.php");
require_once 'config.php';

$errors = new myErrorHandling();
$renderer = new myRenderer();
$python = new myPythonHandler($sysdir);

$debugit = false;
if(isset($_REQUEST['debug'])){
	$debugit = $_REQUEST['debug']; // get the debugstatus
}

$data = $_REQUEST;
$file = $sysdir."data/top.json";
$response = array();

if (file_exists($file)) {
	$jsonstuff = json_decode(file_get_contents($file),TRUE);
	$jsonstuff['root'] = get_config('base');
	$response = json_encode($jsonstuff);
}
else{
	$errors->addErrors("View failed: file does not exist: ".$file);
}
$renderer->renderpage($response, $errors);
