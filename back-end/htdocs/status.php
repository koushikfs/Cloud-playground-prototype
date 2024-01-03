<?php

$statusFile = 'D:/xampp/htdocs/status.log';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (file_exists($statusFile)) {
        $lines = file($statusFile);
        foreach ($lines as $line) {
            echo htmlspecialchars($line);
        }
    } else {
        echo "No status messages found.";
    }
} else {
    http_response_code(405);
    echo "This script only handles POST requests.";
}

?>