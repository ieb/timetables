<?php

require_once 'auth.php';

session_start();
set_user($_SERVER['REMOTE_USER']);

header("Location: ../list.html");
