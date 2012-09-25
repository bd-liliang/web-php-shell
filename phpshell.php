<?php

$handle = fopen('php://stdin','r');
//chroot('env/');

while(!feof($handle))
{
	echo "#php_shell_start_lee_890707\n";

	$command = fgets($handle);
	$command = rtrim($command);
	$command[strlen($command) - 1] == ';' || $command .= ';';
	$code = highlight_string('<?php ' . $command,true);
	$code = str_replace('&lt;?php','',$code);
	
	echo json_encode(array($code));
	echo "\n";

	ob_start();
	eval($command);
	$output = ob_get_contents();
	ob_end_clean();

	echo json_encode(array($output));
	echo "\n";

	echo "#php_shell_end_lee_890707\n";
}
fclose($handle);

function shutdown()
{
	$output = ob_get_contents();
	ob_end_clean();
	echo json_encode(array($output));
	echo "\n";

	echo "#php_shell_end_lee_890707\n";
	fclose($handle);
}

register_shutdown_function('shutdown');
?>
