<?php

// Useful for testing and not harmful otherwise. Not linked anywhere. Simply returns a good HMAC for you which lives for about five minutes

require_once 'auth.php';

session_start();

$user = current_user();
$time = time()+5*60;

header("Content-type: text/plain");

echo "$user:$time:".generate_hmac($user,$time)."\n";