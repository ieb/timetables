<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Mercury</title>

    <!-- Mercury CSS -->
    <link rel="stylesheet" href="../css/mercury.css" type="text/css" media="screen, print" />

    <!-- Libs JS-->
    <script src="../lib/common-libs.js" type="text/javascript"></script>
	<script src="../lib/jstorage.min.js" type="text/javascript"></script>


    <!-- Mercury Lib JS-->
    <script src="../js/mercury-common.js" type="text/javascript"></script>

</head>

<body>

    <!-- App header -->
    <div id="header">
        <h1 class="product_title">Mercury <sup>BETA</sup></h1>
    </div>

    <!-- Course and part selectors -->
    <div id="select_container" style="display: none;">

        <select id="select_year" class="inline">
            <!-- Filled by JS -->
        </select>

        <select id="select_tripos" class="inline">
            <!-- Filled by JS -->
        </select>

        <select id="select_part" class="inline">
            <!-- Filled by JS -->
        </select>

    </div>

    <div id="courselist_container">
		<p>
			As you logged in with raven, you will need to close your browser to logout.
		</p>
	</div>

</body>
</html>
<?php
	require_once 'auth.php';

	session_start();
	unset_user();
