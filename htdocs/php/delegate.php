<?php

require_once 'auth.php';

session_start();

// XXX wash file access data (everywhere in app)
$success = delegate($_POST['what'],current_user(),$_POST['whom']);

$out = Array('success' => $success);

if($success) {
    log_it("Permission to edit ".tripos_name($_POST['what'])." given to ".$_POST['whom']." by ".current_user().".");
} else {
    log_it("Failed attempt: permission to edit ".tripos_name($_POST['what'])." attempted by ".$_['whom']." by ".current_user());    
}

echo json_encode($out);

