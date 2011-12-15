<?php

require_once('config.php');

session_start();

class myPythonHandler {
        
	public function __construct($arg) {
		$this->sysdir = $arg;
	}
	public function doit($cmd, $errors){
		return $this->my_exec($cmd, $errors, $this->sysdir, $input='');
	}
	
	function my_exec($cmd, $errors, $sysdir, $input='') {
		$proc=proc_open($cmd, array(0=>array('pipe', 'r'), 1=>array('pipe', 'w'), 2=>array('pipe', 'w')), $pipes); 
		fwrite($pipes[0], $input);fclose($pipes[0]); 
		$stdout=stream_get_contents($pipes[1]);fclose($pipes[1]); 
		$stderr=stream_get_contents($pipes[2]);fclose($pipes[2]); 
		$rtn=proc_close($proc);
		if($stderr !=""){
			$myFile = $sysdir."error/stdout.txt";
			$fh = fopen($myFile, 'a+') or $errors->addErrors("can't open file: ".$myFile) ;
			
			if(!$errors->hasError()){
				$stringData = 'CMD:'.$cmd."\n";
				fwrite($fh, $stringData);
				$stringData = 'stdout:'.$stdout."\n";
				fwrite($fh, $stringData);
				$stringData = 'stderr:'.$stderr."\n";
				fwrite($fh, $stringData);
				$stringData = 'return:'.$rtn."\n";
				fwrite($fh, $stringData);
				fclose($fh);
			}
			$errors->addErrors("Python failed: ".$cmd.": ".$stderr);
		}
		return array('stdout'=>$stdout, 
			'stderr'=>$stderr, 
			'return'=>$rtn 
		); 
	} 
}

class myRenderer{
	public function __construct() {
	}
	function doHeader(){
		header('Cache-Control: no-cache, must-revalidate');
		header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');
		header('Content-type: application/json');
	}

	public function renderpage($data, $errors){	    
	    if($errors->hasError()){
		header("Status: 500 Internal Server Error", false, 500);
		echo $errors->showFriendlyErrors();
	    }
	    else{
		$this->doHeader();
		echo $data;
	    }
	}

}

    
class myErrorHandling {
        
	public function __construct() {
		$this->errormsgs =  array();
	}
    
	public function hasError(){
            if(sizeof($this->errormsgs) > 0){
                return true;
            }
	    return false;
	}
	
	public function showStringErrors(){
		$stng = "";
		foreach($this->errormsgs as $data){
			$stng .= $data["msg"]. "\n";
		}
		return $stng;
	}
    
	public function showErrors(){
		return $this->errormsgs;		
	}

	public function showFriendlyErrors() {
		$stng = $this->showStringErrors();
		if(preg_match('/{{(.*)}}/',$stng,$match))
			$stng = $match[1];
		return $stng;
	}
    
	public function addErrors($msg){
            $this->errormsgs[] = array( "msg" => $msg);
	}
    
    
	public function clearErrors(){
            $this->errormsgs = array();		
	}
}


// Undo damage done by magic quotes
if (get_magic_quotes_gpc()) {
    $process = array(&$_GET, &$_POST, &$_COOKIE, &$_REQUEST);
    while (list($key, $val) = each($process)) {
        foreach ($val as $k => $v) {
            unset($process[$key][$k]);
            if (is_array($v)) {
                $process[$key][stripslashes($k)] = $v;
                $process[] = &$process[$key][stripslashes($k)];
            } else {
                $process[$key][stripslashes($k)] = stripslashes($v);
            }
        }
    }
    unset($process);
}

function load_config() {
	global $sysdir;
	
	$out = Array();
	$data = file_get_contents("$sysdir/config/config.txt");
	$lines = explode("\n",$data);
	foreach($lines as $line) {
		$eq = split('=',$line,2);
		if(count($eq)<2)
			continue;
		$out[trim($eq[0])] = trim($eq[1]);
	}
	return $out;
}

function get_config($key) {
	// XXX do it more efficiently
	$config = load_config();
	if(array_key_exists($key,$config))
		return $config[$key];
	else
		return false;
}
