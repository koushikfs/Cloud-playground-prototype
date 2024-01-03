<?php

$statusFile = 'D:/xampp/htdocs/status.log';

$lineCount = 0;

function writeStatus($message, $statusFile) {
    date_default_timezone_set('Asia/Kolkata');

    $space = "        ";
    $space1 = "      ";
    
    if (file_exists($statusFile)) {
        $lineCount = count(file($statusFile));
    }
    $nextLineNumber = $lineCount + 1;

    $timestamp = date('jS M Y / h:i A');
    if ($nextLineNumber >= 100) {
        $messageWithLineNumber = $timestamp . ": " . "" . $space1 . $message . PHP_EOL;
    } elseif ($nextLineNumber >= 10) {
        $messageWithLineNumber = $timestamp . ": " . "  " . $space . $message . PHP_EOL;
    } else {
        $messageWithLineNumber = $timestamp . ": " . "            " . $message . PHP_EOL;
    }
    
    file_put_contents($statusFile, $messageWithLineNumber, FILE_APPEND);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    writeStatus("[+] Received POST request", $statusFile);

    $jsonInput = file_get_contents('php://input');

    $decodedInput = json_decode($jsonInput, true);

    if (isset($decodedInput['data']) && is_string($decodedInput['data'])  && !empty($decodedInput['data'])) {

        $data = json_decode($decodedInput['data'], true);
        if ($data !== null || json_last_error() === JSON_ERROR_NONE) {
            
            writeStatus("[+] Valid JSON data found", $statusFile);

            file_put_contents('input.json', $decodedInput['data']);
            writeStatus("[+] Created input.json file", $statusFile);

            writeStatus("[+] Generating terraform code", $statusFile);
            exec('python3.10 generate.py input.json', $output, $returnVar);
            
            if ($returnVar == 0) {
                writeStatus("[+] Generation complete", $statusFile);

                
                writeStatus("[+] Removing instance profiles", $statusFile);
                
                exec('python3.10 remove_instance_profiles.py', $remove_instance_output, $remove_instance_returnVar);

                if ($remove_instance_returnVar == 0) {
                    writeStatus("[+] Removed instance profiles", $statusFile);

                    writeStatus("[+] creating a terraform file", $statusFile);
    
                    $filePath = './deploy/deploy.tf';
                    $pythonOutput = implode("\n", $output);
                    file_put_contents($filePath, $pythonOutput);
                    writeStatus("[+] created a terraform file", $statusFile);
    
                    chdir('./deploy/');
    
                    writeStatus("[+] Starting ~# terraform init", $statusFile);
    
                    exec('terraform init', $terraformInitOutput, $terraformInitReturnVar);
                    if ($terraformInitReturnVar == 0) {
                        writeStatus("[+] Terraform init completed", $statusFile);
                        writeStatus("[+] Terraform apply in progress, will take ~5min :-)", $statusFile);

                        exec('python3.10 terraform_apply.py', $output, $returnVar);
    
                    } else {
                        writeStatus("[-] Error: Terraform init failed\n", $statusFile);
                    }

                }else{
                    writeStatus("[-] Failed to remove instance profiles\n", $statusFile);
                }

            } else{
                writeStatus("[-] Terraform code Generation Failed\n", $statusFile);
            }

        } else {
            writeStatus("[-] Invalid JSON format\n", $statusFile);
        }

    } else {
        
        writeStatus("[-] Error: No data passed\n", $statusFile);
    }

    exit;

} else {
    
    writeStatus("[-] Something went wront in above steps / Error: Not a POST request\n", $statusFile);
    exit;
}

?>