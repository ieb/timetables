<?php
require_once 'config.php';
require_once("sharedHandlers.php");

require_once 'auth.php';

$errors = new myErrorHandling();
$renderer = new myRenderer();
$python = new myPythonHandler($sysdir);

$data = $_REQUEST;
$response = array();


switch($_SERVER['REQUEST_METHOD'])
{
case 'GET':
   $filename = $data ['courseid'];
   
$file = $sysdir."data/details_".$filename.".json";
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
   $filename = $data ['courseid'];
   
    $tripos = substr($filename,0,14);

    if(!can_edit(current_user(),$tripos)) {
        header("HTTP/1.0 500 Security Check Failed");
        return;
    }   
   
   $file = $sysdir."data/details_".$filename.".json";
   if (file_exists($file)) {
      unlink($file);
      $response["msg"] = "Delete successfull: ".$file."\"";
   }
   else{
	$errors->addErrors("Delete failed: file does not exist: ".$file);
   }
   $renderer->renderpage(json_encode($response), $errors);
break;

default:
}

function doPOST(){
    global $data,$sysdir,$errors, $python, $renderer, $pypath, $logfile;
    
    $payload3 = $data['payload'];
    $payload = json_decode($payload3,true);  

    $tripos = substr($payload['id'],0,14);

    if(!can_edit(current_user(),$tripos)) {
        header("HTTP/1.0 500 Security check failed");
        return;
    }
    
	// Check vhash for currency
	$prev = json_decode(file_get_contents($sysdir."data/details_".$payload['id'].".json"),TRUE);
	if($payload['vhash'] != $prev['vhash']) {
        header("HTTP/1.0 409 has been updated");
        return;		
	}
	
	
    file_put_contents($sysdir."data/details_".$payload['id'].".json",json_encode($payload));
    $pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l $logfile -d ". escapeshellarg($payload['id']), $errors);
	$payload = json_decode(file_get_contents($sysdir."data/details_".$payload['id'].".json"),TRUE);	
    $renderer->renderpage(json_encode($payload), $errors);
}
