<?php

require_once 'auth.php';

$text = get_log();

$data = Array ('text' => $text);

echo json_encode($data);
