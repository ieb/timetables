<?php

require_once("sharedHandlers.php");
require_once 'auth.php';
require_once 'config.php';

$python = new myPythonHandler($sysdir);
$errors = new myErrorHandling();

$id = preg_replace('/[^A-Za-z0-9]/','',$_POST['id']);

$path = "$sysdir/data/csv_$id.csv";

$result = '';

$tripos = substr($id,0,14);

if(!can_edit(current_user(),$tripos)) {
    $result = 'Permission denied';
} else {

    if(@move_uploaded_file($_FILES['spreadsheet']['tmp_name'], $path)) {
        
        $pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l ". escapeshellarg($logfile) ." -s ". escapeshellarg($id), $errors);
        $result = preg_replace('/[\\r\\n]/',' ',$errors->showFriendlyErrors());
        $result = preg_replace('/"/','\\"',$result);
		if($errors->hasError()) {
	        $pyerrors = $python->doit("$pypath ".$sysdir."python/indium/indium.py -l $logfile -d ". escapeshellarg($id), $errors);
		}
    }
}
?>
<html>
    <body>
        <script language="javascript" type="text/javascript">
            window.top.window.mercury.list.upload_done("<?php echo $result; ?>");
        </script>        
    </body>
</html>
