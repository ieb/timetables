<?php

require_once 'config.php';

function get_perms($user) {
	global $sysdir;
	$data = @file_get_contents($sysdir."data/user_".$user.".json");
	if(!$data) {
		$data = json_encode(Array(
			'triposes' => Array(),
			'all' => false
		));
	}
	return json_decode($data,TRUE);
}

function save_perms($user,$data) {
	global $sysdir;
	file_put_contents($sysdir."data/user_".$user.".json",json_encode($data));
}

function tripos_name($id) {
    global $sysdir;
    $top = json_decode(file_get_contents($sysdir."data/top.json"),$assoc = TRUE);
    $data = $top['years'][0]['triposes'];
    foreach($data as $tripos) {
        $parts = $tripos['parts'];
        foreach($parts as $part) {
            if($part['id'] == $id)
                return $part['name'];
        }
    }
    return null;
}

function get_triposes($list) {
	global $sysdir;
	$top = json_decode(file_get_contents($sysdir."data/top.json"),$assoc = TRUE);
	$data = $top['years'][0]['triposes'];
	$out = Array();
    if($list) {
    	foreach($data as $tripos) {
    		$parts = $tripos['parts'];
    		foreach($parts as $part) {
                if($list === true || in_array($part['id'],$list)) {
        			$out[$part['id']] = $part['name'];
                }
    		}
    	}
    }
	return $out;
}

function log_it($what) {
    global $sysdir;
    
    $user = current_user();
    $daytime = date("Y-m-d H:i:s");
    $msg = "$user\t$daytime\t$what\n";
    file_put_contents($sysdir."data/log.txt",$msg,FILE_APPEND);
}

function get_log() {
    global $sysdir;
    
    $log = file_get_contents($sysdir."data/log.txt");
    // reverse log
    $log = join("\n",array_reverse(preg_split('/[\\n\\r]+/',$log)));
    return $log;    
}

function get_delegations() {
    global $sysdir;
    $out = Array();
    if ($handle = opendir($sysdir."data")) {
        /* This is the correct way to loop over the directory. */
        while (false !== ($file = readdir($handle))) {
            if(preg_match('/^user_(.+).json$/',$file,$m)) {
                $data = get_perms($m[1]);
                $tout = Array();
                foreach($data['triposes'] as $t) {
                    $tout[] = tripos_name($t);
                }                
                sort($tout);
                $out[$m[1]] = Array('triposes' => $tout, 'all' => $data['all']);
            }
        }    
        closedir($handle);
    }
    return $out;
}

function delegate($tripos,$from_u,$to_u) {
	$out = false;
	$from = get_perms($from_u);
	$to = get_perms($to_u);
	if($from['all'] || in_array($tripos,$from['triposes'])) {
		# ok, but is it there?
		if(!in_array($tripos,$to['triposes'])) {
			$to['triposes'][] = $tripos;
		}
		$out = true;
	}
	save_perms($to_u,$to);
	return $out;
}

function rescind($tripos,$by_u,$from_u) {
    $out = false;
    $by = get_perms($by_u);
    $from = get_perms($from_u);
    if($by['all'] || in_array($tripos,$by['triposes'])) {
        foreach($from['triposes'] as $i => $t) {
            if($t == $tripos) {
                unset($from['triposes'][$i]);
            }
        }
        $from['triposes'] = array_values($from['triposes']);
        $out = true;
    }
    save_perms($from_u,$from);
    return $out;
}

function can_edit($who,$tripos) {
    $user = get_perms($who);
    return $user['all'] || in_array($tripos,$user['triposes']);
}

function is_super() {
    $user = get_perms(current_user(True));
    return $user['all'];	
}

function set_impersonate($who) {
	start_session_if_not_started();
	$_SESSION['impersonate'] = $who;
}

function start_session_if_not_started() {
 if (!isset ($_SESSION)) {
    session_start();
  }
}

function current_user($real = False) {
	start_session_if_not_started();
	if(!test_user())
		return '';
	if(isset($_SESSION['impersonate']) && !$real)
		return $_SESSION['impersonate'];
	return $_SESSION['user'];
}

function set_user($whom) {
	start_session_if_not_started();
	$_SESSION['user'] = $whom;
}

function unset_user() {
	start_session_if_not_started();
	if(test_user())
		unset($_SESSION['user']);
}

function test_user() {
	start_session_if_not_started();
	return array_key_exists('user',$_SESSION);	
}

function pseudorandom_bytes($count) {
	
}

/**
 * Reads $count bytes from /dev/random. Returns FALSE on failure (e.g. if we're 
 * on Windows).
 */
function pseudorandom_string_dev_random($count) {
	if($count < 1)
		throw new InvalidArgumentException("Count was < 1: " . $count);
	
	$dev_random = @fopen("/dev/random", "r");
	if($dev_random !== FALSE) {
		$pseudo_random_data = fread($dev_random, $count);
		fclose($dev_random);
		if(strlen($pseudo_random_data) === $count) {
			return $pseudo_random_data;
		}
	}
	return FALSE;
}

/** Generates $length random bytes using mt_rand. */
function pseudorandom_string_mt_rand($length) {
	if($length < 1)
		throw new InvalidArgumentException("length was < 1: " . $length);
	$pseudo_random_string = "";
	for($i = 0; $i < $length; ++$i) {
		$pseudo_random_string .= chr(mt_rand(0, 255));
	}
	return $pseudo_random_string;
}

/**
 * Generates a random string sutable for using to key hash_hmac. A sequence of
 * random bytes are generated which are then hashed by the specified algorithm 
 * (default is sha256) and the result is returned.
 */
function generate_key($source_bytes_count = 64, $hash_algo = "sha256") {
	$pseudo_random_data = pseudorandom_string_dev_random($source_bytes_count);
	if(!$pseudo_random_data)
		$pseudo_random_data = pseudorandom_string_mt_rand($source_bytes_count);
	
	assert(strlen($pseudo_random_data) === $source_bytes_count);
	return hash($hash_algo, $pseudo_random_data);
}

/** Writes a key to the configured key file. Throws a RuntimeException if the 
 * key could not be written to the file. */
function write_default_key($keyfile, $key) {
	$keyfile = fopen($keyfile, "w");
	if(!$keyfile) {
		throw new RuntimeException("Couldn't create default keyfile at: " 
			. $keyfile);
	}
	
	assert(fwrite($keyfile, $key, strlen($key)));
	fclose($keyfile);
}

function generate_hmac($who,$time) {
	global $keyfile;
	$key = trim(@file_get_contents($keyfile));
	
	// We need to ensure that we get some data from the keyfile to salt the hmac
	// generation with, otherwise anyone could create their own valid MACs.
	if(strlen($key) == 0) {
		$key = generate_key();
		write_default_key($keyfile, $key);
	}
	
	$key = pack("H".strlen($key),$key);
	return hash_hmac('sha1',"$who:$time",$key);
}

function test_hmac($in) {
	$parts = split(':',trim($in));
	if($parts[1]<time())
		return FALSE;
	if(generate_hmac($parts[0],$parts[1]) != $parts[2])
		return FALSE;
	return $parts[0];
}
