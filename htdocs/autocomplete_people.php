<?php
$data = $_REQUEST;

require_once 'php/config.php';
require_once("php/sharedHandlers.php");

$sysdir = $sysdir_up;
$errors = new myErrorHandling();
$renderer = new myRenderer();
$python = new myPythonHandler($sysdir);


$term = $data['term'];

// only the last word to search (not if it's and)

$m = FALSE;
$tail = '';
$head = '';
if(preg_match('/\s*and\s*$/',$term,$m,PREG_OFFSET_CAPTURE)) {
	$tail = substr($term,$m[0][1]);
	$head = substr($term,0,$m[0][1]);
	$term = '';
} else {
	$term = preg_replace('/\s+$/','',$term);
	$space = strrpos($term,' ');
	if($space!==FALSE) {
		$head = substr($term,0,$space);
		$term = substr($term,$space+1);
		$tail = '';
	}
}

$databits =  get_user_details_from_ldap($head,$term,$tail);

$renderer->renderpage($databits, $errors);

//requires python-ldap and python-simplejson installed
function get_user_details_from_ldap($head,$term,$tail){	
	global $sysdir,$python,$errors,$pypath,$logfile;
	$py = $python->doit("$pypath ".$sysdir."python/ldapsearcher.py -m ". escapeshellarg($term). " -h ". escapeshellarg($head) ." -t ". escapeshellarg($tail), $errors);
	return $py['stdout'];
}
