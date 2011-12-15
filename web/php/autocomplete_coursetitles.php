<?php

require_once("sharedHandlers.php");
require_once 'config.php';

$errors = new myErrorHandling();
$renderer = new myRenderer();


$tripos = $_SERVER['PATH_INFO'];
while(strlen($tripos) && (substr($tripos,0,1)=='/' || substr($tripos,0,1)=='\\'))
    $tripos = substr($tripos,1);
$term = $_GET['term'];

function load($id) {
    global $sysdir,$errors;
    $response;
    $file = $sysdir."data/cal_".$id.".json";
    if (file_exists($file)) {
	$response = json_decode(file_get_contents($file));
    }
    else{
	$errors->addErrors("Delete failed: file does not exist: ".$file, "VIEW");
    }
    
    return $response;
}

$data = load($tripos);
$options = array();

if(!$errors->hasError()){
    $courses = $data->courses;
    foreach($courses as $id => $c) {
        $name = $c->name;
        if(strtolower(substr($name,0,strlen($term)))==strtolower($term)) {
            $options[] = array(
                'label' => $name,
                'value' => $name,
                'id' => $id
            );
        }
    }
}

$renderer->renderpage(json_encode($options), $errors);

?>
