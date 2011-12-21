<?php

require_once 'auth.php';
require_once 'config.php';

session_start();
$out = Array();
$perms = null;
if(test_user()) {
	$out['loggedin'] = true;
	$out['user'] = current_user();
    $perms = get_perms($out['user']);
	$out['perms'] = $perms;
} else {
	$out['loggedin'] = false;
}

/* Which triposes should we get? */
if($perms['all']) {
    $triposes = true;
} else {
    $triposes = $perms['triposes'];
}

$out['triposes'] = get_triposes($triposes);
$out['colour'] = $colour;

header('Cache-Control: no-cache, must-revalidate');
header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');
header('Content-type: application/json');

echo json_encode($out);
