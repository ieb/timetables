<?php

require_once 'config.php';

// XXX should use names not fixed
$id = preg_replace('/[^A-Za-z0-9]/','',$_REQUEST['id']);

header("Content-Type: text/plain");
header('Content-Disposition: attachment; filename="data.txt"');

readfile("$sysdir/data/alt_$id.alt");
