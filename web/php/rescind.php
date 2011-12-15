<?php

require_once 'auth.php';

session_start();

// XXX wash file access data (everywhere in app)

$success = rescind($_POST['what'],current_user(),$_POST['whom']);

if($success) {
    log_it("Permission to edit ".tripos_name($_POST['what'])." rescinded from ".$_POST['whom']." by ".current_user());
} else {
    log_it("Failed attempt: permission to rescind edit from ".tripos_name($_POST['what'])." attempted by ".$_['whom']." by ".current_user());    
}

$out = Array('success' => $success);

echo json_encode($out);

