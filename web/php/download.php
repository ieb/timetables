<?php

require_once 'config.php';

// XXX should use names not fixed
$filename = 'timetable.csv';
$id = preg_replace('/[^A-Za-z0-9]/','',$_REQUEST['id']);

header("Content-Type: text/csv");
header('Content-Disposition: attachment; filename="'.$filename.'"');

readfile("$sysdir/data/csv_$id.csv");
