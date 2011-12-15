<?php
require_once("sharedHandlers.php");

require_once 'auth.php';

require_once 'config.php';


switch($_SERVER['REQUEST_METHOD']) {
case 'GET':
    $out = Array();
    foreach($_REQUEST['id'] as $id) {
        $id = preg_replace('/[^A-Za-z0-9]/','',$id);
        $filename = "$sysdir/data/audit_$id.json";    
        if(file_exists($filename)) {
            $data = json_decode(file_get_contents($filename));
        } else {
            $data = Array ( 'status' => "no recorded status", "time" => "never updated", 'who' => 'no one' );
        }
        $out[$id] = $data;
    }
    echo json_encode($out);   
    break;
case 'POST':
    $id = preg_replace('/[^A-Za-z0-9]/','',$_POST['id']);
    $filename = "$sysdir/data/audit_$id.json";
    file_put_contents($filename,json_encode(Array(
        'status' => $_POST['status'],
        'time' => date('Y-m-d H:i'),
        'who' => $_SESSION['user']
    )));
    readfile($filename);
    break;
}
