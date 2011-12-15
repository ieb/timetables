<?php

require_once("sharedHandlers.php");

require_once 'auth.php';
require_once 'config.php';

$errors = new myErrorHandling();
$renderer = new myRenderer();
$python = new myPythonHandler($sysdir);

$data = $_REQUEST;
$response = array();

switch($_SERVER['REQUEST_METHOD'])
{
case 'GET':
   $filename = $data['tripospartid'];
   
   $file = $sysdir."data/cal_".$filename.".json";
   if (file_exists($file)) {
       $jsonstuff = file_get_contents($file);
       $response = $jsonstuff;
   }
   else{
	$errors->addErrors("Get failed: file does not exist: ".$file);
   }
   $renderer->renderpage($response, $errors);
break;
case 'POST':
//do post
    doPOST();
break;
case 'DELETE':
   $filename = $data['tripospartid'];

    $tripos = substr($filename,0,14);

    if(!can_edit(current_user(),$tripos)) {
        header("HTTP/1.0 500 Security check failed");
        return;
    }


   $file = $sysdir."data/cal_".$filename.".json";
   if (file_exists($file)) {
      unlink($file);
      $response["msg"] = "Delete successful: ".$file."\"";
   }
   else{
	$errors->addErrors("Delete failed: file does not exist: ".$file);
   }
   $renderer->renderpage(json_encode($response), $errors);
break;

default:
}

function doPOST(){
    global $data,$sysdir,$errors, $python, $renderer,$pypath,$logfile;
    
    $payload3 = $data['payload'];
	if(get_magic_quotes_gpc()) {
	    $payload3 = $payload3;
	}
    $payload = json_decode($payload3,true);  

    $tripos = substr($payload['id'],0,14);

    if(!can_edit(current_user(),$tripos)) {
        header("HTTP/1.0 500 Security check failed");
        return;
    }

	// Check vhash for currency
	$prev = json_decode(file_get_contents($sysdir."data/cal_".$payload['id'].".json"),TRUE);
	if($payload['vhash'] != $prev['vhash']) {
        header("HTTP/1.0 409 has been updated");
        return;		
	}


    $test = file_put_contents($sysdir."data/cal_".$payload['id'].".json",json_encode($payload));
    $pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l $logfile -c ". escapeshellarg($payload['id']), $errors);
	if($errors->hasError()) {
		file_put_contents($sysdir."data/cal_".$payload['id'].".json",json_encode($prev));
	}
    $payload = file_get_contents($sysdir."data/cal_".$payload['id'].".json");
    $renderer->renderpage($payload, $errors);
}



//Errors return 500 or 404 etc and string message

//id
//courses
//rectangles

//rectangles%5B1%5D%5Bid%5D:createdseries_1
