<?php

$statusFile = 'D:/xampp/htdocs/status.log';
chdir('./deploy/');


function writeStatus($message, $statusFile) {
    date_default_timezone_set('Asia/Kolkata');

    $timestamp = date('jS M Y / h:i A');
    $messageWithLineNumber = $timestamp . ": " . "          " . $message . PHP_EOL;
    file_put_contents($statusFile, $messageWithLineNumber, FILE_APPEND);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    writeStatus("[+] Terraform destroy in progress", $statusFile);
    exec('terraform destroy -auto-approve', $terraformdestroyOutput, $terraformdestroyReturnVar);
    if ($terraformdestroyReturnVar == 0) {
        writeStatus("[+] Terraform destroy completed\n", $statusFile);
    } else {
        writeStatus("[-] Error: Terraform destroy failed\n", $statusFile);
    }
    echo "<h3>destroy in progress<h3>";
}else {
    http_response_code(405); // Method Not Allowed
    echo json_encode(['status' => 'error', 'message' => 'Invalid request method.']);
}
?>
