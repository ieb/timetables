<?php

$sysdir = "../../";
$sysdir_up = "../";
$pypath = "python";
$keyfile = "../../secret/hmac-key";

// If $colour is set then it is provided to  mercury-common.js when it requests 
// php/user.php. The live site's University logo & grey background is in place
// by default and is left there if no colour is specified here. It should be
// set to a hash prefixed 24bit hex string if desired, e.g. "#000099"
$colour = null;

$logfile = '/tmp/mercury.log';
